import os
import pytest
import shutil

from util.copy import copy_package

SRC_PKG = 'src1/1pkgd'
DEST_PKG = 'export1/p1/pkgd_test'

MAIN = """
from {name} import a, b

def do_a_and_b():
    print(a.foo())
    print(b.bar())

def main():
    do_a_and_b():

if __name__ == "__main__":
    main()
"""

A = """
CONST = 1337

def foo():
    return CONST
"""

B = """
from {name}.a import CONST

def bar():
    return -CONST
"""

files = {
    '__init__.py': '',
    'main.py': MAIN,
    'a.py': A,
    'b.py': B,
}


@pytest.fixture(autouse=True)
def setup_and_delete_pkg():
    os.makedirs(SRC_PKG)
    os.makedirs(DEST_PKG)
    for filename in files:
        filepath = os.path.join(SRC_PKG, filename)
        with open(filepath, 'w') as testfile:
            print(filepath)
            testfile.write(
                files[filename].format(name=os.path.basename(SRC_PKG)))
            print(files[filename].format(name=os.path.basename(SRC_PKG)))

    yield

    shutil.rmtree(SRC_PKG.split('/')[0])
    shutil.rmtree(DEST_PKG.split('/')[0])


def test_copy_package():
    copy_package(SRC_PKG, DEST_PKG)
    for filename in files:
        with open(os.path.join(DEST_PKG, filename)) as destfile:
            assert destfile.read() == files[filename].format(
                name=os.path.basename(DEST_PKG))
