
import sys
from os import walk
from os.path import join
from doctest import testfile

# Make sure I'm getting the local selkie module

sys.path[0:0] = ['../src']
import selkie
assert selkie.__file__.endswith('../src/selkie/__init__.py')

# Recursively list .rst files

def rst_files ():
    for (root, dnames, fnames) in walk('../docs/source'):
        for name in fnames:
            if name.endswith('.rst'):
                yield join(root, name)

for fn in rst_files():
    testfile(fn)
