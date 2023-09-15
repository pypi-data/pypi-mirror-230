import os

from cval_lib.utils import lib_tools

if os.getenv('CVAL_CHECK_VERSION_DISABLED') is None:
    lib_tools.LibraryChecker('cval-lib')()
