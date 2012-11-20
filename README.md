## Basic Usage

    import drill
    doc = drill.parse(path_or_url_or_string)
    
    # Drill down to a specific element.
    print unicode(doc.book.title)
    
    # Iterate through all "title" tags in the document.
    for t in doc.iter('title'):
        print t.attrs, t.data
    
    # Find all "bar" nodes with a "baz" child and a "foo" parent.
    q = doc.find('//foo/bar[baz]'):
    # Easily access the first and last elements of matching results.
    print q.first(), q.last()
    # Iterate over results.
    for e in q:
        do_something(e)

## Features

* Runnable test suite
* Python 3 support

## Advantages

* Pure python
* Faster, more efficient parsing than ElementTree
    * Using drill, a 150 MB XML file took 23 seconds to parse, consuming 990 MB of RAM
    * The same file parsed using ElementTree took 46 seconds, and consumed 1.3 GB of RAM
