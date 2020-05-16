# -*- coding: utf-8 -*-
'''
Created on 2014-07-16
@summary: Just a pure python module for encrypt and decrypt with interleaving 
          and random padding random number TEA.
@author: fiefdx

Modified on 2014-12-26
@summary: Add 32 and 64 iterations support
@author: fiefdx
'''

import os
import sys
import struct
import logging
import binascii
from random import seed
from random import randint

LOG = logging.getLogger(__name__)

__version__ = "1.0.4"

DELTA = 0x9e3779b9
OP_32 = 0xffffffff
OP_64 = 0xffffffffffffffff

def get_encrype_length(length):
    fill_n = (8 - (length + 2))%8 + 2
    result = 1 + length + fill_n + 7
    return result

def get_tea_sum(tea_num, delta):
    tea_sum = 0
    for i in range(tea_num):
        tea_sum += delta
    return tea_sum&OP_32

def tea_encrypt(v, k, iterations = 32):
    '''
    v is utf-8
    '''
    v0, v1 = struct.unpack(">LL", v)
    k0, k1, k2, k3 = struct.unpack(">LLLL", k)
    tea_sum = 0
    for i in range(iterations):
        tea_sum += DELTA
        tea_sum &= OP_32
        v0 += ((((v1 << 4) & OP_32) + k0) ^ (v1 + tea_sum) ^ (((v1 >> 5) & OP_32) + k1))
        v0 &= OP_32
        v1 += ((((v0 << 4) & OP_32) + k2) ^ (v0 + tea_sum) ^ (((v0 >> 5) & OP_32) + k3))
        v1 &= OP_32
    return struct.pack('>LL', v0, v1)

def tea_decrypt(v, k, iterations = 32):
    '''
    v is utf-8
    '''
    v0, v1 = struct.unpack(">LL", v)
    k0, k1, k2, k3 = struct.unpack(">LLLL", k)
    tea_sum = 0xC6EF3720 if iterations == 32 else 0x8DDE6E40
    for i in range(iterations):
        v1 -= (((v0 << 4) + k2) ^ (v0 + tea_sum) ^ ((v0 >> 5) + k3))
        v1 &= OP_32
        v0 -= (((v1 << 4) + k0) ^ (v1 + tea_sum) ^ ((v1 >> 5) + k1))
        v0 &= OP_32
        tea_sum -= DELTA
        tea_sum &= OP_32
    return struct.pack('>LL', v0, v1)

def str_encrypt(v, k, iterations = 32):
    '''
    v is unicode or string
    k is md5 unicode
    iterations must be 32 or 64
    return string
    '''
    v = v.encode("utf-8") if isinstance(v, str) else v
    k = str(k)
    iterations = 64 if iterations > 32 else 32
    # ascii str to bin str
    k = binascii.unhexlify(k)
    result = b""
    cipertext = OP_64
    pre_plaintext = OP_64
    end_char = b"\0"
    fill_n_or = 0xf8
    v_length = len(v)
    fill_n = (8 - (v_length + 2))%8 + 2
    fill_s = b""
    fill_bytes = []
    for i in range(fill_n):
        fill_bytes.append(randint(0, 0xff))
        # fill_s = fill_s + chr(0x02)
    fill_s = bytes(fill_bytes)
    v = bytes([(fill_n - 2) | fill_n_or]) + fill_s + v + end_char * 7

    for i in range(0, len(v), 8):
        if i == 0:
            encrypt_text = tea_encrypt(v[i:i + 8], k, iterations)
            result += encrypt_text
            cipertext = struct.unpack(">Q", encrypt_text)[0]
            pre_plaintext = struct.unpack(">Q", v[i:i + 8])[0]
        else:
            plaintext = struct.unpack(">Q", v[i:i + 8])[0] ^ cipertext
            encrypt_text = tea_encrypt(struct.pack(">Q", plaintext), k, iterations)
            encrypt_text = struct.pack(">Q", struct.unpack(">Q", encrypt_text)[0] ^ pre_plaintext)
            result += encrypt_text
            cipertext = struct.unpack(">Q", encrypt_text)[0]
            pre_plaintext = plaintext
    # bin to ascii return is str not unicode
    return result

def str_decrypt(v, k, iterations = 32):
    '''
    v is unicode or string
    k is md5 unicode
    iterations must be 32 or 64
    return string
    '''
    k = str(k)
    iterations = 64 if iterations > 32 else 32
    # ascii to bin
    if isinstance(v, str):
        v = binascii.unhexlify(v)
    k = binascii.unhexlify(k)
    result = b""
    cipertext = OP_64
    pre_plaintext = OP_64
    pos = 0
    for i in range(0, len(v), 8):
        if i == 0:
            cipertext = struct.unpack(">Q", v[i:i + 8])[0]
            plaintext = tea_decrypt(v[i:i + 8], k, iterations)
            pos = (plaintext[0] & 0x07) + 2
            result += plaintext
            pre_plaintext = struct.unpack(">Q", plaintext)[0]
        else:
            encrypt_text = struct.pack(">Q", struct.unpack(">Q", v[i:i + 8])[0] ^ pre_plaintext)
            plaintext = tea_decrypt(encrypt_text, k, iterations)
            plaintext = struct.unpack(">Q", plaintext)[0] ^ cipertext
            result += struct.pack(">Q", plaintext)
            pre_plaintext = plaintext ^ cipertext
            cipertext = struct.unpack(">Q", v[i:i + 8])[0]

    # if result[-7:] != "\0" * 7: return None
    if result[-7:] != b"\0" * 7: return ""
    # return str not unicode
    return result[pos + 1: -7].decode("utf-8")


if __name__ == "__main__":
    # v = b"testtest"
    # k = b"b5d2099e49bdb07b8176dff5e23b3c14"
    # k = binascii.unhexlify(k)
    # print("first key: ", k)

    # r = tea_encrypt(v, k)
    # print(r)

    # r = tea_decrypt(r, k)
    # print(r)

    v = "this is a test, 这是一个测试" # .encode("utf-8")
    k = "b3be6b55584e1a4e13928e8fdb6e1e5f"
    print(type(v))

    r = str_encrypt(v, k)
    print(r, type(r))

    # import base64

    # r = '5a9e9393747a171c88582aa3fd9b9644'
    # k = '06673e0eda575ffe65cfb13843cf1a28'

    # b64 = "gryXJ1D5k3+bLByjRcffGg=="
    # k = "0d77b5ddb781eabd41d84f635fad9d25"
    # r = base64.b64decode(b64)

    # print("v: ", r, type(r), k, type(k))

    r = str_decrypt(r, k)
    print(r)
