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
        # Parents.
        gc = self.catalog.first('book').first('isbn')
        self.assertEqual([p.tagname for p in gc.parents()], ['book', 'catalog'])
        # Siblings.
        self.assertEqual([p.tagname for p in gc.siblings()], ['author', 'title'])
        self.assertEqual(len(list(gc.siblings('title'))), 1)

    def test_path(self):
        # Find all book ISBNs.
        isbns = [unicode(e) for e in self.catalog.path('book/isbn')]
        self.assertEqual(isbns, ['0-684-84328-5', '0-684-84328-6'])
        # Find the author of anything in the catalog.
        authors = [unicode(e) for e in self.catalog.path('*/author')]
        self.assertEqual(authors, ['Watson, Dan', u('Rodriguez, José'), 'Watson, Dan'])
        # Find all the grandchildren elements.
        grandchildren = [e.tagname for e in self.catalog.path('*/*')]
        self.assertEqual(grandchildren, ['author', 'isbn', 'title', 'author', 'isbn', 'title', 'author', 'title'])

    def test_parse(self):
        # Parse out the drive on Windows, they don't play nice with file:// URLs.
        drive, path = os.path.splitdrive(self.path)
        # Load XML document from a URL.
        drill.parse('file://' + path.replace('\\', '/'))
        # Load an XML (unicode) string.
        drill.parse(u('<title>Él Libro</title>'))
        # Load XML document from a string (will be bytes on Python 3)
        with open(self.path, 'rb') as f:
            drill.parse(f.read())

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

    def test_iterparse(self):
        parsed_tags = []
        for e in drill.iterparse(open(self.path, 'rb')):
            parsed_tags.append(e.tagname)
            e.clear()
        self.assertEqual(parsed_tags, [
            'author', 'isbn', 'title', 'book', # The first book, children first
            'author', 'isbn', 'title', 'book', # The second book
            'author', 'title', 'magazine', # The magazine
            'catalog' # Finally, the root catalog
        ])
        # The last element should be the finished root element, and it should be empty (since we cleared as we parsed).
        self.assertEqual(e.tagname, 'catalog')
        self.assertEqual(len(e), 0)

if __name__ == '__main__':
    unittest.main()
