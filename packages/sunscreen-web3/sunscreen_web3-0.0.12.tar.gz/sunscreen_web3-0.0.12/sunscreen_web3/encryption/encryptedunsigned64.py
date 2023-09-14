from .buffer import SunscreenBuffer
from .encrypted import Encrypted
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any
import ctypes


class EncryptedUnsigned64(Encrypted):
    def __init__(
        self,
        pointer: Any,
        context: SunscreenFHEContext,
        is_fresh: bool,
        key_set_override: Optional[KeySet],
    ):
        Encrypted.__init__(self, pointer, context, is_fresh, key_set_override)

    @classmethod
    def create_from_plain(
        cls,
        number: int,
        context: SunscreenFHEContext,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedUnsigned64":
        cipher = (
            context.get_rust_library()
            .get()
            .encrypt_unsigned64(
                context.get_inner_context(),
                context.get_public_key(key_set_override),
                number,
            )
        )

        result = EncryptedUnsigned64(
            cipher,
            context,
            True,
            key_set_override,
        )
        return result

    @classmethod
    def create_from_encrypted_cipher(
        cls,
        cipher_obj: SunscreenBuffer,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedUnsigned64":
        cipher = (
            context.get_rust_library().get().get_cipher_from_string(cipher_obj.get())
        )

        return EncryptedUnsigned64(cipher, context, is_fresh, key_set_override)

    @classmethod
    def create_from_encrypted_cipher_pointer(
        cls,
        cipher: Any,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedUnsigned64":
        return EncryptedUnsigned64(cipher, context, is_fresh, key_set_override)

    def refresh_cipher(self):
        value = self.decrypt()
        reencrypted = EncryptedUnsigned64.create_from_plain(
            value, self.context, self.key_set_override
        )
        self.replace_pointer(reencrypted.release())
        self.is_fresh = True

    def decrypt(self) -> int:
        return self.rust_library.get().decrypt_unsigned64(
            self.context.get_inner_context(),
            self.context.get_private_key(self.key_set_override),
            self.get(),
        )

    def shape(self) -> list[int]:
        return [1, 1]


class EncryptedUnsigned64Zero(EncryptedUnsigned64):
    def __init__(
        self, context: SunscreenFHEContext, key_set_override: Optional[KeySet]
    ):
        EncryptedUnsigned64.__init__(
            self,
            None,
            context,
            True,
            key_set_override,
        )

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            if not self.pointer:
                self.pointer = self.rust_library.get().encrypt_unsigned64(
                    self.context.get_inner_context(),
                    self.context.get_public_key(self.key_set_override),
                    0,
                )

            return self.pointer
