#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import drill
import os

if drill.PY3:
    def u(s): return s
    def unicode(s): return str(s)
    file_mode = 'r'
else:
    def u(s): return unicode(s, 'utf-8')
    file_mode = 'rb'

class DrillTests (unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catalog.xml')
        self.catalog = drill.parse(self.path)

    def test_basics(self):
        # Drill down by tag names, test that unicode() returns element character data.
        self.assertEqual(unicode(self.catalog.book.author), u('Watson, Dan'))
        # Access .attrs directly.
        self.assertEqual(self.catalog.book.attrs['author'], u('watsond'))
        # Access element children by index.
        self.assertEqual(unicode(self.catalog[1].author), u('Rodriguez, José'))
        # Access element attributes using index notation.
        self.assertEqual(self.catalog[1]['author'], u('josé'))
        # Access attributes on an element that also has data.
        self.assertEqual(self.catalog.book.title['language'], u('en'))
        # Access element character data directly via .data.
        self.assertEqual(self.catalog[1].title.data, u('Él Libro'))

    def test_traversal(self):
        self.assertEqual(self.catalog.first()['id'], u('book1'))
        self.assertEqual(self.catalog.last()['id'], u('mag1'))
        self.assertEqual(self.catalog.last('book')['id'], u('book2'))
        titles = [unicode(t) for t in self.catalog.find('title')]
        self.assertEqual(titles, [u('Test Book'), u('Él Libro'), u('Test Magazine')])

    def test_parse(self):
        # Load XML document from a URL.
        drill.parse('file://' + self.path)
        # Load XML document from a string.
        f = open(self.path, file_mode)
        drill.parse(f.read())
        f.close() # Avoid ResourceWarning on Python 3.

if __name__ == '__main__':
    unittest.main()
