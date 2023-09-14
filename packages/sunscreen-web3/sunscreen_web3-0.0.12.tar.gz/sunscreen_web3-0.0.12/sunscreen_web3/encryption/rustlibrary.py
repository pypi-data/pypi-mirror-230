import ctypes
import platform
from .. import c_libs

try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources


class InteropBuffer(ctypes.Structure):
    _fields_ = [
        ("buffer", ctypes.c_void_p),
        ("capacity", ctypes.c_int32),
        ("used", ctypes.c_int32),
    ]


class Keys(ctypes.Structure):
    _fields_ = [
        ("public_key", ctypes.c_void_p),
        ("private_key", ctypes.c_void_p),
    ]


class RustLibrary:
    def __init__(self):
        plt = platform.system()
        file_name = None
        if plt == "Windows":
            raise Exception("Windows is not supported.")
        elif plt == "Linux":
            file_name = "linux.so"
        elif plt == "Darwin":
            file_name = "osx.dylib"
        else:
            raise Exception("Unknown OS")

        f = resources.open_text(c_libs, file_name)
        self.rust_lib = ctypes.CDLL(f.name)
        self.__initialize_library()

    def __initialize_library(self):
        # Initialize Context
        self.rust_lib.initialize_context.argtypes = (ctypes.c_uint32, ctypes.c_bool)
        self.rust_lib.initialize_context.restype = ctypes.c_void_p

        # Initialize Context With Params
        self.rust_lib.initialize_context_with_params_as_string.argtypes = (
            ctypes.POINTER(InteropBuffer),
        )
        self.rust_lib.initialize_context_with_params_as_string.restype = ctypes.c_void_p

        # Initialize Context With Params
        self.rust_lib.initialize_context_with_standard_params.argtypes = ()
        self.rust_lib.initialize_context_with_standard_params.restype = ctypes.c_void_p

        # Release Context
        self.rust_lib.release_context.argtypes = (ctypes.c_void_p,)

        # Release Cipher
        self.rust_lib.release_cipher.argtypes = (ctypes.c_void_p,)

        # Get Cipher as string
        self.rust_lib.get_cipher_as_string.argtypes = (
            ctypes.c_void_p,
            ctypes.POINTER(InteropBuffer),
        )

        self.rust_lib.get_cipher_from_string.argtypes = (ctypes.POINTER(InteropBuffer),)
        self.rust_lib.get_cipher_from_string.restype = ctypes.c_void_p

        # Get PK as string
        self.rust_lib.get_public_key_as_string.argtypes = (
            ctypes.c_void_p,
            ctypes.POINTER(InteropBuffer),
        )

        self.rust_lib.get_public_key_from_string.argtypes = (
            ctypes.POINTER(InteropBuffer),
        )
        self.rust_lib.get_public_key_from_string.restype = ctypes.c_void_p

        # Get Params
        self.rust_lib.get_params_as_string.argtypes = (
            ctypes.c_void_p,
            ctypes.POINTER(InteropBuffer),
        )

        # Buffer Create
        self.rust_lib.buffer_create.argtypes = (ctypes.c_uint32,)
        self.rust_lib.buffer_create.restype = ctypes.POINTER(InteropBuffer)

        # Buffer Release
        self.rust_lib.buffer_release.argtypes = (ctypes.POINTER(InteropBuffer),)

        # Buffer Data
        self.rust_lib.buffer_data.argtypes = (ctypes.POINTER(InteropBuffer),)
        self.rust_lib.buffer_data.restype = ctypes.c_void_p

        # Buffer Capacity
        self.rust_lib.buffer_capacity.argtypes = (ctypes.POINTER(InteropBuffer),)
        self.rust_lib.buffer_capacity.restype = ctypes.c_uint32

        # Buffer Length
        self.rust_lib.buffer_length.argtypes = (ctypes.POINTER(InteropBuffer),)
        self.rust_lib.buffer_length.restype = ctypes.c_uint32

        # Set Buffer Length
        self.rust_lib.set_buffer_length.argtypes = (
            ctypes.POINTER(InteropBuffer),
            ctypes.c_uint32,
        )

        # Generate Keys
        self.rust_lib.generate_keys.argtypes = (ctypes.c_void_p,)
        self.rust_lib.generate_keys.restype = ctypes.POINTER(Keys)

        # Get public key
        self.rust_lib.get_public_key.argtypes = (ctypes.POINTER(Keys),)
        self.rust_lib.get_public_key.restype = ctypes.c_void_p

        # Get private key
        self.rust_lib.get_private_key.argtypes = (ctypes.POINTER(Keys),)
        self.rust_lib.get_private_key.restype = ctypes.c_void_p

        # Encrypt Number
        self.rust_lib.encrypt_float.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_double,
        )

        self.rust_lib.encrypt_float.restype = ctypes.c_void_p

        # Decrypt Number
        self.rust_lib.decrypt_float.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        )
        self.rust_lib.decrypt_float.restype = ctypes.c_double

        # Encrypt Number
        self.rust_lib.encrypt_signed.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_int64,
        )

        self.rust_lib.encrypt_signed.restype = ctypes.c_void_p

        # Decrypt Number
        self.rust_lib.decrypt_signed.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        )
        self.rust_lib.decrypt_signed.restype = ctypes.c_int64

        # Encrypt Number
        self.rust_lib.encrypt_unsigned64.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint64,
        )

        self.rust_lib.encrypt_unsigned64.restype = ctypes.c_void_p

        # Decrypt Number
        self.rust_lib.decrypt_unsigned64.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
        )
        self.rust_lib.decrypt_unsigned64.restype = ctypes.c_uint64

        # Encrypt Number
        self.rust_lib.encrypt_unsigned256.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(InteropBuffer),
        )

        self.rust_lib.encrypt_unsigned256.restype = ctypes.c_void_p

        # Decrypt Number
        self.rust_lib.decrypt_unsigned256.argtypes = (
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.POINTER(InteropBuffer),
        )

        self.rust_lib.release_public_key.argtypes = (ctypes.c_void_p,)
        self.rust_lib.release_private_key.argtypes = (ctypes.c_void_p,)

    def get(self):
        return self.rust_lib
