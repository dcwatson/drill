__version_info__ = (1, 0, 0)
__version__ = '.'.join(str(i) for i in __version_info__)

from xml.sax import make_parser
from xml.sax.handler import feature_namespaces, ContentHandler
import sys

PY3 = sys.version_info[0] == 3

if PY3:
    import io
    import urllib.request as url_lib
    def unicode(s): return str(s)
    basestring = str
else:
    import StringIO as io
    import urllib2 as url_lib

class XMLElement (object):

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
        return '<XMLElement %s>' % self.tagname

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

    def write(self, fp, indent=0, level=0):
        """ Writes an XML representation of this node (including descendants) to the specified file-like object. """
        if indent:
            if level > 0:
                fp.write('\n')
            fp.write(' ' * (indent * level))
        fp.write('<%s' % self.tagname)
        for key, val in self.attrs.items():
            fp.write(' %s="%s"' % (key, val))
        fp.write('>')
        if self.data:
            fp.write(self.data)
        for c in self._children:
            c.write(fp, indent, level + 1)
        if indent and self._children:
            fp.write('\n')
            fp.write(' ' * (indent * level))
        fp.write('</%s>' % self.tagname)

    def xml(self, indent=0):
        """ Returns an XML representation of this node (including descendants). """
        s = io.StringIO()
        self.write(s, indent=indent)
        return s.getvalue()

    def append(self, name, attrs, data=None):
        """ Called when the parser detects a start tag (child element) while in this node. """
        elem = XMLElement(name, attrs, data, self, len(self._children))
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
            self.root = XMLElement(name, attrs)
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

def parse(url_or_path):
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
            parser.parse(io.StringIO(url_or_path))
        else:
            # A filesystem path.
            parser.parse(open(url_or_path, 'rb'))
    else:
        # A file-like object or an InputSource.
        parser.parse(url_or_path)
    return handler.root
