from androguard.core.bytecodes import axml
from androguard.core import bytecode
from androguard.core.resources import public
import re
import ctypes

from struct import pack, unpack



RES_NULL_TYPE = 0x0000
RES_STRING_POOL_TYPE = 0x0001
RES_TABLE_TYPE = 0x0002
RES_XML_TYPE = 0x0003

RES_XML_FIRST_CHUNK_TYPE    = 0x0100
RES_XML_START_NAMESPACE_TYPE= 0x0100
RES_XML_END_NAMESPACE_TYPE  = 0x0101
RES_XML_START_ELEMENT_TYPE  = 0x0102
RES_XML_END_ELEMENT_TYPE    = 0x0103
RES_XML_CDATA_TYPE          = 0x0104
RES_XML_LAST_CHUNK_TYPE     = 0x017f

RES_XML_RESOURCE_MAP_TYPE   = 0x0180

RES_TABLE_PACKAGE_TYPE      = 0x0200
RES_TABLE_TYPE_TYPE         = 0x0201
RES_TABLE_TYPE_SPEC_TYPE    = 0x0202
RES_TABLE_LIBRARY_TYPE      = 0x0203
RES_TABLE_OVERLAYABLE_TYPE        = 0x0204,
RES_TABLE_OVERLAYABLE_POLICY_TYPE = 0x0205,
RES_TABLE_STAGED_ALIAS_TYPE       = 0x0206,

# Flags in the STRING Section
SORTED_FLAG = 1 << 0
UTF8_FLAG = 1 << 8

# Position of the fields inside an attribute
ATTRIBUTE_IX_NAMESPACE_URI = 0
ATTRIBUTE_IX_NAME = 1
ATTRIBUTE_IX_VALUE_STRING = 2
ATTRIBUTE_IX_VALUE_TYPE = 3
ATTRIBUTE_IX_VALUE_DATA = 4
ATTRIBUTE_LENGHT = 5

# Internally used state variables for AXMLParser
START_DOCUMENT = 0


def decode_length(data, sizeof_char):
    """
    Generic Length Decoding at offset of string

    The method works for both 8 and 16 bit Strings.
    Length checks are enforced:
    * 8 bit strings: maximum of 0x7FFF bytes (See
    http://androidxref.com/9.0.0_r3/xref/frameworks/base/libs/androidfw/ResourceTypes.cpp#692)
    * 16 bit strings: maximum of 0x7FFFFFF bytes (See
    http://androidxref.com/9.0.0_r3/xref/frameworks/base/libs/androidfw/ResourceTypes.cpp#670)

    :param offset: offset into the string data section of the beginning of
    the string
    :param sizeof_char: number of bytes per char (1 = 8bit, 2 = 16bit)
    :returns: tuple of (length, read bytes)
    """
    sizeof_2chars = sizeof_char << 1
    fmt = "<2{}".format('B' if sizeof_char == 1 else 'H')
    highbit = 0x80 << (8 * (sizeof_char - 1))

    length1, length2 = unpack(fmt, data[0:sizeof_2chars])

    if (length1 & highbit) != 0:
        length = ((length1 & ~highbit) << (8 * sizeof_char)) | length2
        size = sizeof_2chars
    else:
        length = length1
        size = sizeof_char

    # These are true asserts, as the size should never be less than the values
    if sizeof_char == 1:
        assert length <= 0x7FFF, "length of UTF-8 string is too large! At offset={}".format(data)
    else:
        assert length <= 0x7FFFFFFF, "length of UTF-16 string is too large!  At offset={}".format(data)

    return length, size

def encode_length(data, sizeof_char):
    """
    Generic Length Decoding at offset of string

    The method works for both 8 and 16 bit Strings.
    Length checks are enforced:
    * 8 bit strings: maximum of 0x7FFF bytes (See
    http://androidxref.com/9.0.0_r3/xref/frameworks/base/libs/androidfw/ResourceTypes.cpp#692)
    * 16 bit strings: maximum of 0x7FFFFFF bytes (See
    http://androidxref.com/9.0.0_r3/xref/frameworks/base/libs/androidfw/ResourceTypes.cpp#670)

    :param offset: offset into the string data section of the beginning of
    the string
    :param sizeof_char: number of bytes per char (1 = 8bit, 2 = 16bit)
    :returns: tuple of (length, read bytes)
    """
    
    size = len(data)
    if sizeof_char == 1:
        return pack('<BB', size, size)
    else:
        return pack('<H', size)# + 1)

class AXMLHeader:

    def __init__(self, type_, size):
        self._type = type_
        self._size = size
        self._header_size = 8

    def pack(self):
        return pack("<HHL", self._type, self._header_size, self._size)

class AXMLHeader_XML(AXMLHeader):

    def __init__(self, size):
        super().__init__(RES_XML_TYPE, size)

class AXMLHeader_STRING_POOL(AXMLHeader):

    def __init__(self, sb, size):
        super().__init__(RES_STRING_POOL_TYPE, size)
        self._header_size = 28
        self._sb_len = len(sb.sb)
        self._st_len = len(sb.st)
        self._size = size + self._header_size + 4 + 4 + 8

    def pack(self):
        return super().pack() + pack("<LL", self._sb_len, self._st_len)

class AXMLHeader_START_ELEMENT(AXMLHeader):

    def __init__(self, size):
        super().__init__(RES_XML_START_ELEMENT_TYPE, size + 8)
        self._header_size = 16

class AXMLHeader_END_ELEMENT(AXMLHeader):

    def __init__(self, size):
        super().__init__(RES_XML_END_ELEMENT_TYPE, size + 8)
        self._header_size = 16

class AXMLHeader_START_NAMESPACE(AXMLHeader):

    def __init__(self, size):
        super().__init__(RES_XML_START_NAMESPACE_TYPE, size + 8)
        self._header_size = 16

class AXMLHeader_END_NAMESPACE(AXMLHeader):

    def __init__(self, size):
        super().__init__(RES_XML_END_NAMESPACE_TYPE, size + 8)
        self._header_size = 16

class AXML:

    def __init__(self):
        self.stringblocks = StringBlocks()
        self.resxml = b""

    def start(self, root, attrib):
        index = self.stringblocks.get(root)
        i_namespace = self.stringblocks.get("android")
        attributes = []

        dic_attrib = attrib.items()
        for k, v in dic_attrib:
            tmp = k.split('{')
            if len(tmp) > 1:
                tmp = tmp[1].split('}')
                name = self.stringblocks.get(tmp[1])
                namespace = self.stringblocks.get(tmp[0])
            else:
                namespace = 0xffffffff
                name = self.stringblocks.get(k)

            if v == "true":
                attributes.append(Attribute(namespace, name, 0xffffffff, 0x12000000, 1))
            elif v == "false":
                attributes.append(Attribute(namespace, name, 0xffffffff, 0x12000000, 0))
            elif re.search("^@android:[0-9a-fA-F]+$", v):
                attributes.append(Attribute(namespace, name, 0xffffffff, 0x1000000, int(v[-8:], 16)))
            elif re.search("^@[0-9a-fA-F]+$", v):
                attributes.append(Attribute(namespace, name, 0xffffffff, 0x1000000, int(v[1:], 16)))
            elif re.search("^0x[0-9a-fA-F]+$", v):
                attributes.append(Attribute(namespace, name, 0xffffffff, 0x11000000, int(v[2:], 16)))
            else:
                if self.stringblocks.sb[name] == "versionName":
                    value = self.stringblocks.get(v)
                    attributes.append(Attribute(namespace, name, value, 0x3000008, value))
                elif self.stringblocks.sb[name] == "compileSdkVersionCodename":
                    value = self.stringblocks.get(v)
                    attributes.append(Attribute(namespace, name, value, 0x3000008, value))
                else:
                    try:
                        value = ctypes.c_uint32(int(v)).value
                        attributes.append(Attribute(namespace, name, 0xffffffff, 0x10000008, value))
                    except ValueError:
                        try:
                            value = unpack('>L', pack('!f', float(v)))[0]
                            attributes.append(Attribute(namespace, name, 0xffffffff, 0x04000008, value))
                        except ValueError:
                            value = self.stringblocks.get(v)
                            attributes.append(Attribute(namespace, name, value, 0x3000008, value))

            #print("namespace: ", namespace, "\nname: ", name, "\nvalue: ",
            #        value)


        #print( [ self.stringblocks.sb[a._name] for a in attributes])
        content = RES_XML_START_ELEMENT(0xffffffff, index, attributes).content
        header = AXMLHeader_START_ELEMENT(len(content)).pack()
        self.resxml += header + content

    def start_namespace(self, prefix, uri):
        index = self.stringblocks.get(prefix)
        i_namespace = self.stringblocks.get(uri)
        content = RES_XML_START_NAMESPACE(i_namespace, index).content
        header = AXMLHeader_START_NAMESPACE(len(content)).pack()
        self.resxml += header + content

    def add_package(self, val):
        index = self.stringblocks.get('package')
        val = self.stringblocks.get(val)
        attributes = []
        attributes.append(Attribute(0xffffffff, val, val, 0x3000000, val))
        content = RES_XML_START_ELEMENT(0xffffffff, index, attributes).content
        #header = AXMLHeader_START_ELEMENT(len(content)).pack()
        self.resxml += header + content

    def end_namespace(self, prefix, uri):
        index = self.stringblocks.get(prefix)
        i_namespace = self.stringblocks.get(uri)
        content = RES_XML_END_NAMESPACE(i_namespace, index).content
        header = AXMLHeader_END_NAMESPACE(len(content)).pack()
        self.resxml += header + content

    def end(self, attrib):
        index = self.stringblocks.sb.index(attrib)
        i_namespace = self.stringblocks.sb.index("android")
        #content = RES_XML_END_ELEMENT(i_namespace, index).pack()
        content = RES_XML_END_ELEMENT(0xffffffff, index).content
        header = AXMLHeader_END_ELEMENT(len(content)).pack()
        self.resxml += header + content

    def ressource_map(self, res):
        header = AXMLHeader(RES_XML_RESOURCE_MAP_TYPE, 8)
        header._header_size = 8
        header._size = 8 + 4 * len(res)
        content = Classical_RES_XML(RES_XML_RESOURCE_MAP_TYPE)
        #self.resxml += header.pack() + b"\x03\x00\x01\x01"# + content.pack()
        self.resxml += header.pack()
        for i in range(0, len(res)):
            #print(res[i], self.stringblocks.sb[i])
            self.resxml += pack("<L", res[i])
        #return header.pack()

    def add_all_attrib(self, root):
        res = []
        namespace = "{http://schemas.android.com/apk/res/android}"
        queue = [root]
        while len(queue) > 0:
            r = queue.pop()
            for child in r:
                queue.append(child)
            for k in r.attrib.keys():
                if k.startswith(namespace):
                    name = k[len(namespace):]
                    if name in public.SYSTEM_RESOURCES['attributes']['forward']:
                        val = public.SYSTEM_RESOURCES['attributes']['forward'][name]
                        if not val in res:
                            self.stringblocks.get(name)
                            res.append(val)
        self.ressource_map(res)

    def pack(self):
        sb = self.stringblocks
        sb_pack = sb.pack()
        header_string_pool = AXMLHeader_STRING_POOL(sb, len(sb.pack()) - 28 )# + 4 + 4)
        body = header_string_pool.pack() + sb_pack + self.resxml
        header_xml = AXMLHeader_XML(len(body) + 8)
        return header_xml.pack() + body


class StringBlocks:

    def __init__(self):
        self.sb = []
        self.st = []

    def __str__(self):
        return " | ".join(self.sb)

    def pack(self):
        st_count = len(self.st)
        sb_count = len(self.sb)
        sb, sb_offsets = self.encode_sb()
        st, st_offsets = b"", b""
        # FIXME: find stringoffse
        stringoffset = 28 + len(sb_offsets) + len(st_offsets)
        # FIXME replace stringoffset
        styleoffset  = 0
        return pack('<LLL', 0, stringoffset, styleoffset) + \
                        sb_offsets + st_offsets + sb + st

    def encode_sb(self):
        buf = b""
        offsets = b""
        idx = 0
        for s in self.sb:
            #tmp = encode_length(s, 1) + s.encode('utf-8') + b'\x00'
            tmp = encode_length(s, 2) + s.encode('utf-16')[2:] + b'\x00\x00'
            #if len(tmp)%4 == 2:
            #    tmp += b'\x00\x00'
            offsets += pack('<I', idx)
            idx += len(tmp)
            buf+=tmp
        buf += b"\x00" * (4 - (len(buf) % 4))
        # FIXME padding
        return buf, offsets

    def get(self, name):
        try:
            index = self.sb.index(name)
        except ValueError:
            index = len(self.sb)
            self.sb.append(name)
        return index

class Attribute:

    def __init__(self, namespaceURI, name, value, type_, data):
        self._namespaceURI = namespaceURI
        self._name = name
        self._value = value
        self._type = type_
        self._data = data

    def pack(self):
        return pack('<LLLLL', self._namespaceURI, self._name, self._value,
                self._type, self._data)


class Classical_RES_XML:

    def __init__(self, type_, lineNumber=0, Comment=0xffffffff):
        self._type = type_
        self._header_size = 8
        self._size = 0
        self._lineNumber = lineNumber
        self._Comment = Comment

    @property
    def content(self):
        return pack('<LL', self._lineNumber, self._Comment)

    @property
    def size(self):
        self._size = self.header_size() + len(self.content)

    def pack(self):
        return pack('<hhL', self._type, self._header_size, self._size) + self.content

class RES_XML_START_ELEMENT(Classical_RES_XML):

    def __init__(self, namespaceURI, name, attributes,
            styleAttribute=-1, classAttribute=-1, lineNumber=0, Comment=0xffffffff):
        super().__init__(RES_XML_START_ELEMENT_TYPE, lineNumber, Comment)
        self._namespaceURI = namespaceURI
        self._name = name
        self._attributes = attributes
        self._styleAttribute = styleAttribute
        self._classAttribute = classAttribute

    @property
    def content(self):
        return super().content + pack('<LLLLhh',
                self._namespaceURI,
                self._name,
                0x140014, # potential attribute value
                len(self._attributes),
                self._styleAttribute,
                self._classAttribute) + \
                        b"".join( a.pack() for a in self._attributes)

    @property
    def attributes(self):
        return b""

class RES_XML_END_ELEMENT(Classical_RES_XML):

    def __init__(self, namespaceURI, name, lineNumber=0, Comment=0xffffffff):
        super().__init__(RES_XML_END_ELEMENT_TYPE, lineNumber, Comment)
        self._namespaceURI = namespaceURI
        self._name = name

    @property
    def content(self):
        return super().content + pack('<LL',
                self._namespaceURI,
                self._name)

class RES_XML_START_NAMESPACE(Classical_RES_XML):

    def __init__(self, prefix, uri, lineNumber=0, Comment=0xffffffff):
        super().__init__(RES_XML_START_NAMESPACE_TYPE, lineNumber, Comment)
        self._prefix = prefix
        self._uri = uri

    @property
    def content(self):
        return super().content + pack('<LL',
                self._prefix,
                self._uri)

class RES_XML_END_NAMESPACE(Classical_RES_XML):

    def __init__(self, prefix, uri, lineNumber=0, Comment=0xffffffff):
        super().__init__(RES_XML_END_NAMESPACE_TYPE, lineNumber, Comment)
        self._prefix = prefix
        self._uri = uri

    @property
    def content(self):
        return super().content + pack('<LL',
                self._prefix,
                self._uri)



def encode_etree(root, axml):
    axml.start(root.tag, root.attrib)
    for e in root:
        encode_etree(e, axml)
    axml.end(root.tag)

def encode(root):
    axml = AXML()
    axml.add_all_attrib(root)
    axml.start_namespace("http://schemas.android.com/apk/res/android", "android")
    #axml.add_package(root.get('package'))
    #print(root.get('package'))
    encode_etree(root, axml)
    axml.end_namespace("http://schemas.android.com/apk/res/android", "android")
    return axml

