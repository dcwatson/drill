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
        titles = [unicode(t) for t in self.catalog.iter('title')]
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

    def test_query(self):
        # Find all book ISBNs.
        isbns = [unicode(e) for e in self.catalog.find('book/isbn')]
        self.assertEqual(isbns, ['0-684-84328-5', '0-684-84328-6'])
        # Same thing, but with a descendant query to search all subnodes.
        isbns = [unicode(e) for e in self.catalog.find('//book/isbn')]
        self.assertEqual(isbns, ['0-684-84328-5', '0-684-84328-6', '0-000-00000-0'])
        # Find the author of anything in the top-level catalog.
        authors = [unicode(e) for e in self.catalog.find('*/author')]
        self.assertEqual(authors, ['Watson, Dan', u('Rodriguez, José'), 'Watson, Dan'])
        # Find all the grandchildren elements.
        grandchildren = [e.tagname for e in self.catalog.find('*/*')]
        self.assertEqual(grandchildren, ['author', 'isbn', 'title', 'author', 'isbn', 'title', 'extra_element', 'author', 'title', 'price', 'book'])
        # Child tag predicates.
        self.assertEqual([e.tagname for e in self.catalog.find('*[price]')], ['magazine'])
        # Child tag with matching data predicates.
        self.assertEqual([e.path() for e in self.catalog.find('*[author="Watson, Dan"]')], ['book[0]', 'magazine[2]'])
        # Attribute existence predicates.
        self.assertEqual([e.path() for e in self.catalog.find('*/*[@marked]')], ['book[1]/isbn[1]', 'magazine[2]/price[2]'])
        # Attribute value predicates.
        self.assertEqual([e.path() for e in self.catalog.find('*/*[@marked=1]')], ['book[1]/isbn[1]'])
        # Index predicates.
        self.assertEqual([e.path() for e in self.catalog.find('book[0]/*[2]')], ['book[0]/title[2]'])
        # Negative index predicates.
        self.assertEqual([e.path() for e in self.catalog.find('*[-2]/*[-1]')], ['book[1]/extra_element[3]'])
        # Find all title elements under child nodes with tagname "magazine".
        self.assertEqual([unicode(e) for e in self.catalog.find('magazine//title')], ['Test Magazine', 'Nonsense'])
        # Underscores in tag names.
        self.assertEqual([e.path() for e in self.catalog.find('book/extra_element')], ['book[1]/extra_element[3]'])

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
            'author', 'isbn', 'title', 'extra_element', 'book', # The second book
            'author', 'title', 'price', # Magazine elements
                'title', 'isbn', 'book', # Book inside the magazine
            'magazine', # The magazine
            'catalog' # Finally, the root catalog
        ])
        # The last element should be the finished root element, and it should be empty (since we cleared as we parsed).
        self.assertEqual(e.tagname, 'catalog')
        self.assertEqual(len(e), 0)

if __name__ == '__main__':
    unittest.main()
