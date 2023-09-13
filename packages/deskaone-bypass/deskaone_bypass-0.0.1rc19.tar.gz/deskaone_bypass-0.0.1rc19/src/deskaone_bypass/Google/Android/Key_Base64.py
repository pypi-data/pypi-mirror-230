import base64
import binascii
import hashlib

from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA
from Cryptodome.PublicKey.RSA import RsaKey

def bytes_to_int(bytes_seq: bytes) -> int:
    """Convert bytes to int."""
    return int.from_bytes(bytes_seq, "big")

def key_from_b64(b64_key: bytes) -> RsaKey:
    """Extract key from base64."""
    binary_key = base64.b64decode(b64_key)

    i = bytes_to_int(binary_key[:4])
    mod = bytes_to_int(binary_key[4 : 4 + i])

    j = bytes_to_int(binary_key[i + 4 : i + 4 + 4])
    exponent = bytes_to_int(binary_key[i + 8 : i + 8 + j])

    key = RSA.construct((mod, exponent))

    return key

B64_KEY_7_3_29 = (
    b"AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3"
    b"iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pK"
    b"RI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/"
    b"6rmf5AAAAAwEAAQ=="
)

ANDROID_KEY_7_3_29 = key_from_b64(B64_KEY_7_3_29)

def int_to_bytes(num: int, pad_multiple: int = 1) -> bytes:
    """Packs the num into a byte string 0 padded to a multiple of pad_multiple
    bytes in size. 0 means no padding whatsoever, so that packing 0 result
    in an empty string. The resulting byte string is the big-endian two's
    complement representation of the passed in long."""

    # source: http://stackoverflow.com/a/14527004/1231454

    if num == 0:
        return b"\0" * pad_multiple
    if num < 0:
        raise ValueError("Can only convert non-negative numbers.")
    value = hex(num)[2:]
    value = value.rstrip("L")
    if len(value) & 1:
        value = "0" + value
    result = binascii.unhexlify(value)
    if pad_multiple not in [0, 1]:
        filled_so_far = len(result) % pad_multiple
        if filled_so_far != 0:
            result = b"\0" * (pad_multiple - filled_so_far) + result
    return result

def key_to_struct(key: RsaKey) -> bytes:
    """Convert key to struct."""
    mod = int_to_bytes(key.n)
    exponent = int_to_bytes(key.e)

    return b"\x00\x00\x00\x80" + mod + b"\x00\x00\x00\x03" + exponent

def construct_signature(email: str, password: str, key: RsaKey) -> bytes:
    """Construct signature."""
    signature = bytearray(b"\x00")

    struct = key_to_struct(key)
    signature.extend(hashlib.sha1(struct).digest()[:4])

    cipher = PKCS1_OAEP.new(key)
    encrypted_login = cipher.encrypt((email + "\x00" + password).encode("utf-8"))

    signature.extend(encrypted_login)

    return base64.urlsafe_b64encode(signature)