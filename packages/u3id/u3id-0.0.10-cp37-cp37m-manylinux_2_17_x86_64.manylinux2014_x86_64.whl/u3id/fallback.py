from __future__ import annotations

import math
import sys
import time
import random
import hashlib
import uuid
from typing import Optional

class U3IDFactory:

    def __init__(
            self,
            timestamp_integer_part_length_bits: int = 32,
            timestamp_decimal_part_length_bits: int = 10,
            total_length_bits: int = 128,
    ):

        if total_length_bits < timestamp_integer_part_length_bits + timestamp_decimal_part_length_bits:
            raise ValueError(f"total_length_bits must greater than or equal to timestamp_integer_part_length_bits + timestamp_decimal_part_length_bits."
                             f"Values provided (timestamp_integer_part_length_bits: {timestamp_integer_part_length_bits}, "
                             f"timestamp_decimal_part_length_bits: {timestamp_decimal_part_length_bits},"
                             f"total_length_bits: {total_length_bits}")

        if total_length_bits % 8 != 0:
            raise ValueError("total_length_bits must equate to a whole number of bytes")

        self.timestamp_integer_part_length_bits = timestamp_integer_part_length_bits

        if timestamp_decimal_part_length_bits > 30:
            raise ValueError("timestamp_decimal_part_length_bits must be less than or equal 30 because that is the maximum precision for ns.")

        self.timestamp_decimal_part_length_bits = timestamp_decimal_part_length_bits
        self.total_length_bits = total_length_bits
        self.previous_ordered_component = '0'
        self.previous_chaotic_component = None
        self.chaotic_part_length_bits = total_length_bits-timestamp_integer_part_length_bits-timestamp_decimal_part_length_bits

        if self.chaotic_part_length_bits > 512:
            raise ValueError(f"The chaotic part can be at most 512 bits in length when user is providing seed. (using SHA512 hashing) "
                             f"Values provided (self.chaotic_part_length_bits: {self.chaotic_part_length_bits})")


    def generate(
            self,
            integer_time_part: Optional[int] = None,
            decimal_time_part_nanoseconds: Optional[int] = None,
            chaotic_part_seed: Optional[str] = None,
            float_time_part: Optional[float] = None,
    ):
        if float_time_part is not None and (integer_time_part is not None or decimal_time_part_nanoseconds is not None):
            raise ValueError("You can provide either the float_time_part or both of integer_time_part and decimal_time_part but not all.")

        if float_time_part is not None:
            integer_time_part = int(float_time_part)
            decimal_time_part_nanoseconds = int((float_time_part - integer_time_part) * 1_000_000_000)


        if integer_time_part is None:
            integer_time_part = int(time.time())

        if decimal_time_part_nanoseconds is None:
            decimal_time_part_nanoseconds = int((time.time() % 1)* 10**9) << 32
            fractional_time_part = int(decimal_time_part_nanoseconds/1000000000)
        else:
            if decimal_time_part_nanoseconds > 999999999 or decimal_time_part_nanoseconds < 0:
                raise ValueError("When providing a time component, the decimal time part must be specified in ns and be between 0 and 999,999,999")

            fractional_time_part = int((decimal_time_part_nanoseconds << 32) / 1000000000)

        if chaotic_part_seed is None:
            chaotic_bits = random.SystemRandom().getrandbits(self.chaotic_part_length_bits)
            chaotic_bits = f'{{0:>0{self.chaotic_part_length_bits}b}}'.format(chaotic_bits)[:self.chaotic_part_length_bits]
        else:
            h = hashlib.sha512()
            h.update(str.encode(chaotic_part_seed))
            chaotic_bytes = h.digest()

            chaotic_bits = ""

            byte_order = sys.byteorder

            if byte_order == "little":
                for i in range(len(chaotic_bytes)-1, -1, -1):
                    byte = chaotic_bytes[i]
                    chaotic_bits += f'{byte:0>8b}'
                chaotic_bits = chaotic_bits[:self.chaotic_part_length_bits]
            else:
                for i in range(0, len(chaotic_bytes), 1):
                    byte = chaotic_bytes[i]
                    chaotic_bits += f'{byte:0>8b}'
                chaotic_bits = chaotic_bits[-1*self.chaotic_part_length_bits:]



        # Format the integer time component into a binary string of set length. crop from left if too long, pad left with 0 if too short.
        if self.timestamp_integer_part_length_bits > 0:
            integer_time_part_binary_string = f'{{0:>0{self.timestamp_integer_part_length_bits}b}}'.format(integer_time_part)[-1*self.timestamp_integer_part_length_bits:]
            integer_time_part_binary_string = integer_time_part_binary_string.zfill(self.timestamp_integer_part_length_bits)
        else:
            integer_time_part_binary_string = ""

        # Format the decimal time component into a binary string of set length
        if self.timestamp_decimal_part_length_bits > 0:
            fractional_time_part_binary_string = f'{{0:>0{32}b}}'.format(fractional_time_part)[:self.timestamp_decimal_part_length_bits]
        else:
            fractional_time_part_binary_string = ""

        time_component = integer_time_part_binary_string + fractional_time_part_binary_string

        full_binary_string = time_component + chaotic_bits

        full_int = int(full_binary_string, 2)

        full_bytes = full_int.to_bytes((len(full_binary_string) + 7) // 8, byteorder='big')
        # # print(full_bytes)
        # # print(int(full_binary_string, 2).to_bytes((full_int.bit_length() + 7) // 8, 'big'))
        # # exit()
        #
        # # print(full_binary_string)
        # # print(full_bytes)
        # # print(full_bytes.hex())
        # # exit()

        # u3id_from_bytes = U3ID(bytes = full_bytes)
        # u3id_from_hex = U3ID(hex=u3id_from_bytes.hex)
        #
        # print(u3id_from_bytes.hex)
        # print(u3id_from_hex.hex)
        # print(u3id_from_bytes.bytes)
        # print(u3id_from_hex.bytes)
        # exit()
        return U3ID(bytes = full_bytes)

_bytes = bytes

class U3ID:
    def __init__(self, bytes: Optional[bytes] = None, hex: Optional[str] = None):
        if bytes is not None and hex is not None:
            raise ValueError("You specify either bytes or hex, but not both")
        elif bytes is not None:
            self.bytes: bytes = bytes
        elif hex is not None:
            hex = hex.replace("-", "")
            self.bytes = _bytes.fromhex(hex)


    # @property
    # def bytes(self) -> bytes:
    #     return self.int.to_bytes((self.int.bit_length() + 7) // 8, 'big')

    @property
    def int(self) -> int:
        return int.from_bytes(self.bytes, 'big')

    @property
    def binary_string(self) -> str:
        bits = ""
        for i in range(len(self.bytes)):
            byte = self.bytes[i]
            bits += f'{byte:0>8b}'

        return bits

    @property
    def hex(self) -> str:
        return self.bytes.hex()

    @property
    def uuid(self) -> str:
        hex_string = self.hex
        return f'{hex_string[0:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20::]}'

    def to_hex(self) -> str:
        return self.hex

    def to_uuid(self) -> str:
        return self.uuid

    def to_binary_string(self) -> str:
        return self.binary_string

    def __str__(self) -> str:
        return self.hex

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<{self.hex}>)"

    def __hash__(self):
        return self.int

    def __eq__(self, other):
        if type(other) != U3ID:
            return False

        return self.int == other.int

    def __lt__(self, other):
        if type(other) != U3ID:
            raise TypeError()

        return self.int < other.int

    def __le__(self, other):
        if type(other) != U3ID:
            raise TypeError()

        return self.int <= other.int

    def __ne__(self, other):
        if type(other) != U3ID:
            return True

        return self.int != other.int

    def __gt__(self, other):
        if type(other) != U3ID:
            raise TypeError()

        return self.int > other.int

    def __ge__(self, other):
        if type(other) != U3ID:
            raise TypeError()

        return self.int >= other.int


if __name__ == "__main__":
    test_class = U3IDFactory(
        timestamp_integer_part_length_bits = 32,
        timestamp_decimal_part_length_bits = 10,
        total_length_bits = 128,
    )

    u3id = test_class.generate()
    u3id_2 = test_class.generate()

    print(u3id < u3id_2)
    print(u3id <= u3id_2)
    print(u3id == u3id_2)
    print(u3id > u3id_2)
    print(u3id >= u3id_2)

    test_u3id = U3ID(hex = "6b15a9f3-5aab-e0d7-4838-b05127c04654")
    print(test_u3id)



