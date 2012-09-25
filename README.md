# Vendorize
Copyright (c) 2012 Juan Sebastián Casallas 

A quick and dirty module for "vendorizing" osg binaries, libs and plugins under Mac OS X

## In English:
Suppose you want to copy osg bins and libs and bundle them with your app, this may be
troublesome due to libraries linked to your own system. Vendorize makes sure all links
become relative for bins, libs and plugins.

## Usage:
Just place vendorize.py in the root of your copied osg directory (the one you want to bundle)
execute `python vendorize.py` and voilà!

## Dependencies:
[python-magic](https://github.com/ahupp/python-magic)
Note: You may get away without this extension, say by looking at file extensions or doing
the magic yourself (read the header of each file and determine its type)

### Installing python-magic
First install libmagic, my favorite way to do this is using [homebrew]:
`brew install libmagic`
Then just use pip
`pip install python-magic`

## Wishlist
- Linux
- Vendorize more than osg (this can actually be done by removing the "osgPlugins"
portion of the code, provided there are no lib and bin subfolders in the vendorized library

## Disclaimer/Licensing
This script and this README (the "Software") is released under the 
[MIT license](http://www.opensource.org/licenses/mit-license.php), see LICENSE.txt.