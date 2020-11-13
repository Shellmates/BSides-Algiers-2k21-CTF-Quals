#!/usr/bin/python3
from Crypto.Util.number import (
    inverse,
    getPrime,
    bytes_to_long as b2l,
    long_to_bytes as l2b,
)
from itertools import combinations
from base64 import b64encode

FILENAME = "love_letter.txt"
KEY_SIZE = 2048
e = 0x10001

data = open(FILENAME, "rb").read()
chunk_size = len(data) // 3 + (3 - len(data) % 3)

assert chunk_size <= KEY_SIZE // 8 - 11

data += b"\x00" * (chunk_size * 3 - len(data))
chunks = [data[i * chunk_size : (i + 1) * chunk_size] for i in range(3)]

primes = [getPrime(KEY_SIZE // 2) for _ in range(3)]

cipher = ""
for c, pair in enumerate(combinations(primes, 2)):
    p, q = pair
    n = p * q
    phi = (p - 1) * (q - 1)

    enc = b64encode(l2b(pow(b2l(chunks[c]), e, n))).decode()

    cipher += f"{n}:{enc}\n"

open(FILENAME, "w").write(cipher)
