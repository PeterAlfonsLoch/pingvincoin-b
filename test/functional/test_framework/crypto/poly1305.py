#!/usr/bin/env python3
# Copyright (c) 2022 The Pingvincoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

"""Test-only implementation of Poly1305 authenticator

It is designed for ease of understanding, not performance.

WARNING: This code is slow and trivially vulnerable to side channel attacks. Do not use for
anything but tests.
"""

import unittest


class Poly1305:
    """Class representing a running poly1305 computation."""
    MODULUS = 2**130 - 5

    def __init__(self, key):
        self.r = int.from_bytes(key[:16], 'little') & 0xffffffc0ffffffc0ffffffc0fffffff
        self.s = int.from_bytes(key[16:], 'little')

    def tag(self, data):
        """Compute the poly1305 tag."""
        acc, length = 0, len(data)
        for i in range((length + 15) // 16):
            chunk = data[i * 16:min(length, (i + 1) * 16)]
            val = int.from_bytes(chunk, 'little') + 256**len(chunk)
            acc = (self.r * (acc + val)) % Poly1305.MODULUS
        return ((acc + self.s) & 0xffffffffffffffffffffffffffffffff).to_bytes(16, 'little')


# Test vectors from RFC7539/8439 consisting of message to be authenticated, 32 byte key and computed 16 byte tag
POLY1305_TESTS = [
    # RFC 7539, section 2.5.2.
    ["43727970746f6772617068696320466f72756d2052657365617263682047726f7570",
     "85d6be7857556d337f4452fe42d506a80103808afb0db2fd4abff6af4149f51b",
     "a8061dc1305136c6c22b8baf0c0127a9"],
    # RFC 7539, section A.3.
    ["00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
     "000000000000000000000000000",
     "0000000000000000000000000000000000000000000000000000000000000000",
     "00000000000000000000000000000000"],
    ["416e79207375626d697373696f6e20746f20746865204945544620696e74656e6465642062792074686520436f6e747269627"
     "5746f7220666f72207075626c69636174696f6e20617320616c6c206f722070617274206f6620616e204945544620496e7465"
     "726e65742d4472616674206f722052464320616e6420616e792073746174656d656e74206d6164652077697468696e2074686"
     "520636f6e74657874206f6620616e204945544620616374697669747920697320636f6e7369646572656420616e2022494554"
     "4620436f6e747269627574696f6e222e20537563682073746174656d656e747320696e636c756465206f72616c20737461746"
     "56d656e747320696e20494554462073657373696f6e732c2061732077656c6c206173207772697474656e20616e6420656c65"
     "6374726f6e696320636f6d6d756e69636174696f6e73206d61646520617420616e792074696d65206f7220706c6163652c207"
     "768696368206172652061646472657373656420746f",
     "0000000000000000000000000000000036e5f6b5c5e06070f0efca96227a863e",
     "36e5f6b5c5e06070f0efca96227a863e"],
    ["416e79207375626d697373696f6e20746f20746865204945544620696e74656e6465642062792074686520436f6e747269627"
     "5746f7220666f72207075626c69636174696f6e20617320616c6c206f722070617274206f6620616e204945544620496e7465"
     "726e65742d4472616674206f722052464320616e6420616e792073746174656d656e74206d6164652077697468696e2074686"
     "520636f6e74657874206f6620616e204945544620616374697669747920697320636f6e7369646572656420616e2022494554"
     "4620436f6e747269627574696f6e222e20537563682073746174656d656e747320696e636c756465206f72616c20737461746"
     "56d656e747320696e20494554462073657373696f6e732c2061732077656c6c206173207772697474656e20616e6420656c65"
     "6374726f6e696320636f6d6d756e69636174696f6e73206d61646520617420616e792074696d65206f7220706c6163652c207"
     "768696368206172652061646472657373656420746f",
     "36e5f6b5c5e06070f0efca96227a863e00000000000000000000000000000000",
     "f3477e7cd95417af89a6b8794c310cf0"],
    ["2754776173206272696c6c69672c20616e642074686520736c6974687920746f7665730a446964206779726520616e6420676"
     "96d626c6520696e2074686520776162653a0a416c6c206d696d737920776572652074686520626f726f676f7665732c0a416e"
     "6420746865206d6f6d65207261746873206f757467726162652e",
     "1c9240a5eb55d38af333888604f6b5f0473917c1402b80099dca5cbc207075c0",
     "4541669a7eaaee61e708dc7cbcc5eb62"],
    ["ffffffffffffffffffffffffffffffff",
     "0200000000000000000000000000000000000000000000000000000000000000",
     "03000000000000000000000000000000"],
    ["02000000000000000000000000000000",
     "02000000000000000000000000000000ffffffffffffffffffffffffffffffff",
     "03000000000000000000000000000000"],
    ["fffffffffffffffffffffffffffffffff0ffffffffffffffffffffffffffffff11000000000000000000000000000000",
     "0100000000000000000000000000000000000000000000000000000000000000",
     "05000000000000000000000000000000"],
    ["fffffffffffffffffffffffffffffffffbfefefefefefefefefefefefefefefe01010101010101010101010101010101",
     "0100000000000000000000000000000000000000000000000000000000000000",
     "00000000000000000000000000000000"],
    ["fdffffffffffffffffffffffffffffff",
     "0200000000000000000000000000000000000000000000000000000000000000",
     "faffffffffffffffffffffffffffffff"],
    ["e33594d7505e43b900000000000000003394d7505e4379cd01000000000000000000000000000000000000000000000001000000000000000000000000000000",
     "0100000000000000040000000000000000000000000000000000000000000000",
     "14000000000000005500000000000000"],
    ["e33594d7505e43b900000000000000003394d7505e4379cd010000000000000000000000000000000000000000000000",
     "0100000000000000040000000000000000000000000000000000000000000000",
     "13000000000000000000000000000000"],
]


class TestFrameworkPoly1305(unittest.TestCase):
    def test_poly1305(self):
        """Poly1305 test vectors."""
        for test_vector in POLY1305_TESTS:
            hex_message, hex_key, hex_tag = test_vector
            message = bytes.fromhex(hex_message)
            key = bytes.fromhex(hex_key)
            tag = bytes.fromhex(hex_tag)
            comp_tag = Poly1305(key).tag(message)
            self.assertEqual(tag, comp_tag)
