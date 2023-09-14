from abc import ABC, abstractmethod
from .buffer import SunscreenBuffer, DEFAULT_BUFFER_LENGTH
from threading import RLock
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any, Union
from .rustlibrary import RustLibrary
import ctypes


class Encrypted(ABC):
    DEFAULT_ZERO_WORKAROUND = 0.000000000000001

    def __init__(
        self,
        buffer: ctypes.c_void_p,
        context: SunscreenFHEContext,
        is_fresh: bool,
        key_set_override: Optional[KeySet] = None,
    ):
        self.rust_library: RustLibrary = context.get_rust_library()
        self.pointer: Optional[ctypes.c_void_p] = buffer
        self.context: SunscreenFHEContext = context
        self.is_fresh: bool = is_fresh
        self.key_set_override: Optional[KeySet] = key_set_override
        self.lock = RLock()

    def __del__(self):
        if self.pointer:
            self.rust_library.get().release_cipher(self.pointer)

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            return self.pointer

    def release(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            pointer = self.get()
            self.pointer = None
            return pointer

    def replace_pointer(self, pointer: Any) -> None:
        with self.lock:
            if self.pointer:
                self.rust_library.get().release_cipher(self.pointer)
            self.pointer = pointer

    def get_cipher(self) -> SunscreenBuffer:
        pointer = self.get()
        if pointer:
            buffer = SunscreenBuffer.create_for_length(DEFAULT_BUFFER_LENGTH)
            self.rust_library.get().get_cipher_as_string(pointer, buffer.get())
            return buffer
        raise Exception("Pointer is null")

    @abstractmethod
    def decrypt(self) -> Union[float, int]:
        raise NotImplementedError("Decryption is not implemented for base class")

    @abstractmethod
    def refresh_cipher(self) -> None:
        raise NotImplementedError("Refresh Cipher is not implemented for base class")

    @abstractmethod
    def shape(self) -> list[int]:
        raise NotImplementedError("Shape is not implemented for base class")

    @classmethod
    def fix_zero_in_plain(cls, value) -> float:
        if value == 0:
            return Encrypted.DEFAULT_ZERO_WORKAROUND

        return value
