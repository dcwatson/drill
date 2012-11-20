## Basic Usage

    import drill
    doc = drill.parse(path_or_url_or_string)
    for t in doc.find('title'):
        print t.attrs, t.data

## Features

* Runnable test suite
* Python 3 support

## Advantages Over ElementTree

* Faster, more efficient parsing
    * Using drill, a 150 MB XML file took 23 seconds to parse, consuming 990 MB of RAM
    * The same file parsed using ElementTree took 46 seconds, and consumed 1.3 GB of RAM
