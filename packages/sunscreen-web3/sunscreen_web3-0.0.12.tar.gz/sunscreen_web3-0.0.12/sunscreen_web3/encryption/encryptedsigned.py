from .buffer import SunscreenBuffer
from .encrypted import Encrypted
from .context import SunscreenFHEContext, KeySet
from typing import Optional, Any
import ctypes


class EncryptedSigned(Encrypted):
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
    ) -> "EncryptedSigned":
        cipher = (
            context.get_rust_library()
            .get()
            .encrypt_signed(
                context.get_inner_context(),
                context.get_public_key(key_set_override),
                number,
            )
        )

        result = EncryptedSigned(
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
    ) -> "EncryptedSigned":
        cipher = (
            context.get_rust_library().get().get_cipher_from_string(cipher_obj.get())
        )
        return EncryptedSigned(cipher, context, is_fresh, key_set_override)

    @classmethod
    def create_from_encrypted_cipher_pointer(
        cls,
        cipher: ctypes.c_void_p,
        context: SunscreenFHEContext,
        is_fresh: bool = False,
        key_set_override: Optional[KeySet] = None,
    ) -> "EncryptedSigned":
        return EncryptedSigned(cipher, context, is_fresh, key_set_override)

    def refresh_cipher(self):
        value = self.decrypt()
        reencrypted = EncryptedSigned.create_from_plain(
            value, self.context, self.key_set_override
        )
        self.replace_pointer(reencrypted.release())
        self.is_fresh = True

    def decrypt(self) -> int:
        return self.rust_library.get().decrypt_signed(
            self.context.get_inner_context(),
            self.context.get_private_key(self.key_set_override),
            self.get(),
        )

    def shape(self):
        return [1, 1]


class EncryptedSignedZero(EncryptedSigned):
    def __init__(
        self, context: SunscreenFHEContext, key_set_override: Optional[KeySet]
    ):
        EncryptedSigned.__init__(
            self,
            None,
            context,
            True,
            key_set_override,
        )

    def get(self) -> Optional[ctypes.c_void_p]:
        with self.lock:
            if not self.pointer:
                self.pointer = self.rust_library.get().encrypt_signed(
                    self.context.get_inner_context(),
                    self.context.get_public_key(self.key_set_override),
                    0,
                )

            return self.pointer
