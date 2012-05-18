#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import drill
import os

if drill.PY3:
    def u(s): return s
    unicode = str
else:
    def u(s): return unicode(s, 'utf-8')

class DrillTests (unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catalog.xml')
        self.catalog = drill.parse(self.path)

    def test_basics(self):
        # Drill down by tag names, test that unicode() returns element character data.
        self.assertEqual(unicode(self.catalog.book.author), 'Watson, Dan')
        # Access .attrs directly.
        self.assertEqual(self.catalog.book.attrs['author'], 'watsond')
        # Access element children by index.
        self.assertEqual(unicode(self.catalog[1].author), u('Rodriguez, José'))
        # Access element attributes using index notation.
        self.assertEqual(self.catalog[1]['author'], u('josé'))
        # Access attributes on an element that also has data.
        self.assertEqual(self.catalog.book.title['language'], 'en')
        # Access element character data directly via .data.
        self.assertEqual(self.catalog[1].title.data, u('Él Libro'))

    def test_traversal(self):
        # First child.
        self.assertEqual(self.catalog.first()['id'], 'book1')
        # Last child.
        self.assertEqual(self.catalog.last()['id'], 'mag1')
        # Last child matching tag name.
        self.assertEqual(self.catalog.last('book')['id'], 'book2')
        # Recursive find.
        titles = [unicode(t) for t in self.catalog.find('title')]
        self.assertEqual(titles, ['Test Book', u('Él Libro'), 'Test Magazine'])
        # Next sibling matching tag name.
        self.assertEqual(self.catalog.book.author.next('title')['language'], 'en')
        # Previous sibling.
        self.assertEqual(self.catalog[1][2].prev().tagname, 'isbn')

    def test_parse(self):
        # Parse out the drive on Windows, they don't play nice with file:// URLs.
        drive, path = os.path.splitdrive(self.path)
        # Load XML document from a URL.
        drill.parse('file://' + path.replace('\\', '/'))
        # Load an XML (unicode) string.
        drill.parse(u('<title>Él Libro</title>'))
        # Load XML document from a string (will be bytes on Python 3)
        f = open(self.path, 'rb')
        drill.parse(f.read())
        f.close() # Avoid ResourceWarning on Python 3.

    def test_escape(self):
        e = drill.XmlElement('tag', attrs={'foo\x02': 'ba&r\x05'}, data='tes\x01\x03t<ing')
        self.assertEqual(e.xml(pretty=False).decode('utf-8'), '<tag foo="ba&amp;r">test&lt;ing</tag>')

    def test_build(self):
        e = drill.XmlElement('root', data='some data')
        s = e.append('second', data='two')
        s.append('sub', attrs={'x': u('É')})
        f = e.insert(s, 'first', data=u('oné'))
        # Test some different common character encodings.
        # TODO: Figure out why UTF-16 doesn't want to work here.
        for enc in ('utf-8', 'latin-1', 'iso-8859-1', 'mac-roman', 'cp1252'):
            xml = e.xml(pretty=False, encoding=enc).decode(enc)
            self.assertEqual(xml, u('<root>some data<first>oné</first><second>two<sub x="É"></sub></second></root>'))

if __name__ == '__main__':
    unittest.main()
