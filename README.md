## Basic Usage

    import drill
    doc = drill.parse(path_or_url_or_string)
    
    # Drill down to a specific element.
    print unicode(doc.book.title)
    
    # Iterate through all "title" tags in the document.
    for t in doc.iter('title'):
        print t.attrs, t.data
    
    # Find all "bar" nodes with a "baz" child and a "foo" parent.
    q = doc.find('//foo/bar[baz]')
    # Easily access the first and last elements of matching results.
    print q.first(), q.last()
    # Iterate over results.
    for e in q:
        do_something(e)
    
    # Parse only elements matching some path
    for e in drill.iterparse(filelike, xpath='root/*/something'):
        print e.tagname, e.data

## Features

* Runnable test suite
* Python 3 support

## Advantages

* Pure python
* Faster, more efficient parsing than ElementTree
    * Using ElementTree, a ~150 MB XML file (~3,000,000 elements) took ~46 seconds to parse, consuming ~1.3 GB of RAM
    * Parsing the same file using drill took ~24 seconds and consumed ~950 MB of RAM
    * Very unscientific benchmarks performed on a Core i5 @ 2.8 GHz, running Windows 7. YMMV.
* Lots of convenience methods for accessing elements quickly:
    * doc.response.resultCode.data
    * root[2].child['attr']
    * first/last/prev/next methods for traversing siblings
