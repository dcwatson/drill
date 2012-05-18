__version_info__ = (1, 0, 0)
__version__ = '.'.join(str(i) for i in __version_info__)

from xml.sax import make_parser
from xml.sax.handler import feature_namespaces, ContentHandler
from xml.sax.saxutils import escape, quoteattr
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    from io import StringIO as string_io
    from io import BytesIO as bytes_io
    import urllib.request as url_lib
    unicode = str
    basestring = str
    xrange = range
else:
    from StringIO import StringIO as string_io
    from cStringIO import StringIO as bytes_io
    import urllib2 as url_lib

class XmlWriter (object):

    def __init__(self, stream, pretty=True, indent='    ', level=0, invalid='', replacements=None):
        self.stream = stream
        self.pretty = pretty
        self.level = level
        self.replacements = {}
        for c in range(32):
            # \t, \n, and \r are the only valid control characters in XML.
            if c not in (9, 10, 13):
                self.replacements[chr(c)] = invalid
        if replacements:
            self.replacements.update(replacements)
        self.indent = escape(indent, self.replacements)

    def _write(self, data):
        if PY3 and not isinstance(data, bytes):
            # For Python 3, convert string literals to bytes with the file's encoding.
            data = bytes(data, 'utf-8')
        self.stream.write(data)

    def data(self, data, newline=False):
        self._write(escape(unicode(data).strip(), self.replacements).encode('utf-8'))
        if self.pretty and newline:
            self._write('\n')

    def start(self, tag, attrs, newline=False):
        if self.pretty:
            self._write(self.indent * self.level)
        self._write('<')
        self._write(escape(tag, self.replacements).encode('utf-8'))
        for attr, value in attrs.items():
            if value is None:
                value = ''
            attr = escape(unicode(attr), self.replacements).encode('utf-8')
            value = quoteattr(unicode(value), self.replacements).encode('utf-8')
            self._write(' ')
            self._write(attr)
            self._write('=')
            self._write(value)
        self._write('>')
        if self.pretty and newline:
            self._write('\n')
        self.level += 1

    def end(self, tag, indent=False, newline=True):
        self.level -= 1
        if self.pretty and indent:
            self._write(self.indent * self.level)
        self._write('</')
        self._write(escape(tag, self.replacements).encode('utf-8'))
        self._write('>')
        if self.pretty and newline:
            self._write('\n')

    def simple_tag(self, tag, attrs={}, data=None):
        self.start(tag, attrs, newline=False)
        if data is not None:
            self.data(data, newline=False)
        self.end(tag, indent=False)

class XmlElement (object):

    def __init__(self, name, attrs=None, data=None, parent=None, index=None):
        self.tagname = name
        self.parent = parent
        self.index = index # The index of this node in the parent's children list.
        self.attrs = {}
        if attrs:
            self.attrs.update(attrs)
        self.data = ''
        if data:
            self.data += unicode(data)
        self._children = []

    def __repr__(self):
        return '<XmlElement %s>' % self.tagname

    def __unicode__(self):
        return self.data

    def __str__(self):
        if PY3:
            return self.data
        else:
            return self.data.encode('utf-8')

    def __bool__(self):
        """ If we exist, we should evaluate to True, even if __len__ returns 0. """
        return True
    __nonzero__ = __bool__

    def __len__(self):
        """ Return the number of child nodes. """
        return len(self._children)

    def __getitem__(self, idx):
        """ Returns the child node at the given index. """
        if isinstance(idx, basestring):
            return self.attrs[idx]
        return self._children[idx]

    def __getattr__(self, name):
        """ Allows access to any attribute or child node directly. """
        return self.first(name)

    def write(self, writer):
        """ Writes an XML representation of this node (including descendants) to the specified file-like object. """
        nodata = not bool(self.data)
        writer.start(self.tagname, self.attrs, newline=nodata)
        if self.data:
            writer.data(self.data)
        for c in self._children:
            c.write(writer)
        writer.end(self.tagname, indent=nodata)

    def xml(self, **kwargs):
        """ Returns an XML representation of this node (including descendants). """
        s = bytes_io()
        writer = XmlWriter(s, **kwargs)
        self.write(writer)
        return s.getvalue()

    def append(self, name, attrs, data=None):
        """ Called when the parser detects a start tag (child element) while in this node. """
        elem = XmlElement(name, attrs, data, self, len(self._children))
        self._children.append(elem)
        return elem

    def characters(self, ch=None):
        """ Called when the parser detects character data while in this node. """
        if ch is not None:
            self.data += unicode(ch)

    def finalize(self):
        """ Called when the parser detects an end tag. """
        self.data = self.data.strip()

    def items(self):
        """ Generator yielding key, value attribute pairs, sorted by key name. """
        for key in sorted(self.attrs):
            yield key, self.attrs[key]

    def children(self, name=None, reverse=False):
        """ Generator yielding children of this node, optionally matching the given tag name. """
        elems = self._children
        if reverse:
            elems = reversed(elems)
        for elem in elems:
            if name is None or elem.tagname == name:
                yield elem

    def find(self, name=None):
        """ Generator yielding any descendants of this node with the given tag name. """
        for c in self._children:
            if name is None or c.tagname == name:
                yield c
            for gc in c.find(name):
                yield gc

    def first(self, name=None):
        """ Returns the first child of this node, optionally matching the given tag name. """
        for c in self.children(name):
            return c

    def last(self, name=None):
        """ Returns the last child of this node, optionally matching the given tag name. """
        for c in self.children(name, reverse=True):
            return c

    def next(self, name=None):
        """ Returns the next sibling of this node, optionally matching the given tag name. """
        if self.parent is None or self.index is None:
            return None
        for idx in xrange(self.index + 1, len(self.parent)):
            if name is None or self.parent[idx].tagname == name:
                return self.parent[idx]

    def prev(self, name=None):
        """ Returns the previous sibling of this node, optionally matching the given tag name. """
        if self.parent is None or self.index is None:
            return None
        for idx in xrange(self.index - 1, -1, -1):
            if name is None or self.parent[idx].tagname == name:
                return self.parent[idx]

class XMLHandler (ContentHandler):

    def __init__(self):
        self.root = None
        self.current = None

    def startElement(self, name, attrs):
        if not self.root:
            self.root = XmlElement(name, attrs)
            self.current = self.root
        elif self.current is not None:
            self.current = self.current.append(name, attrs)

    def endElement(self, name):
        if self.current is not None:
            self.current.finalize()
            self.current = self.current.parent

    def characters(self, ch):
        if self.current is not None:
            self.current.characters(ch)

def parse(url_or_path, encoding='utf-8'):
    handler = XMLHandler()
    parser = make_parser()
    parser.setFeature(feature_namespaces, 0)
    parser.setContentHandler(handler)
    if isinstance(url_or_path, basestring):
        if '://' in url_or_path[:50]:
            # URL.
            parser.parse(url_lib.urlopen(url_or_path))
        elif url_or_path[:100].strip().startswith('<'):
            # Actual XML data.
            parser.parse(string_io(url_or_path))
        else:
            # A filesystem path.
            parser.parse(open(url_or_path, 'rb'))
    elif PY3 and isinstance(url_or_path, bytes):
        parser.parse(string_io(str(url_or_path, encoding)))
    else:
        # A file-like object or an InputSource.
        parser.parse(url_or_path)
    return handler.root