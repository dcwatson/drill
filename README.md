# drill

## Basic Usage

    import drill
    doc = drill.parse(path_or_url_or_string)
    for t in doc.find('title'):
        print t.attrs, t.data

## Features

* Runnable test suite
* Python 3 support
