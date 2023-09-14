import ctypes
import sys
import pathlib

HERE = pathlib.Path(__file__).parent

# only work for 64 bit system
if sys.maxsize < 2**31:
    raise RuntimeError('64 bit system is required')

# platform dependent
if sys.platform.startswith('win'):

    if sys.version_info[0] == 3 and sys.version_info[1] == 10:
        dll_path = HERE
        #for path in sys.path:
        #  if 'DLLs' in path:
        #      dll_path = path
        #      break
        #ctypes.cdll.LoadLibrary(dll_path + '\\libssl-3-x64.dll')
        #ctypes.cdll.LoadLibrary(dll_path + '\\libcrypto-3-x64.dll')
        #ctypes.cdll.LoadLibrary(dll_path + '\\ntpciscr64.dll')
        #ctypes.cdll.LoadLibrary(dll_path + '\\Pnpscr64.dll')
        #ctypes.cdll.LoadLibrary(dll_path + '\\xpcapi.dll')

        try:
            from openHySim.opensees import *
        except:
            raise RuntimeError('Failed to import opensees on Windows.')
    else:
        raise RuntimeError(
            'Python version 3.10 is needed for Windows')

else:

    raise RuntimeError('This package is for Windows only')
