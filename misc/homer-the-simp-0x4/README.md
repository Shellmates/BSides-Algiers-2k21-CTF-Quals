# Challenge Name

**`Author:`** [hfz](https://hfz1337.github.io)

## Description


## Write-up

Use the euclidean algorithm to calculate the pairwise Greatest Common Divisor of the moduli, each GCD will be a distinct prime number among the three.

```python
#!/usr/bin/python3
from Crypto.Util.number import (
    inverse,
    bytes_to_long as b2l,
    long_to_bytes as l2b,
    GCD as gcd,
)
from base64 import b64decode

FILENAME = "love_letter.txt"
e = 0x10001

data = [line.strip().split(":") for line in open(FILENAME).readlines()]
rsa = {}

for c, pair in enumerate(data):
    rsa[f"n{c + 1}"] = int(pair[0])
    rsa[f"c{c + 1}"] = b2l(b64decode(pair[1]))

p1, p2, p3 = (
    gcd(rsa["n1"], rsa["n2"]),
    gcd(rsa["n1"], rsa["n3"]),
    gcd(rsa["n2"], rsa["n3"]),
)
phi1, phi2, phi3 = (p1 - 1) * (p2 - 1), (p1 - 1) * (p3 - 1), (p2 - 1) * (p3 - 1)
d1, d2, d3 = inverse(e, phi1), inverse(e, phi2), inverse(e, phi3)

m1, m2, m3 = (
    l2b(pow(rsa["c1"], d1, rsa["n1"])),
    l2b(pow(rsa["c2"], d2, rsa["n2"])),
    l2b(pow(rsa["c3"], d3, rsa["n3"])),
)

plaintext = (m1 + m2 + m3).decode()

print(plaintext)
```

```
Maybe it's the beer talking Marge but you got a butt that won't quit. They got those big chewy pretzels here merJanthfgrr...... five dollars??!!!? Get outta here!

// https://www.reddit.com/r/TheSimpsons/comments/3ryi62/maybe_its_the_beer_talking_marge_but_you_got_a/
// Flag: shellmates{m1sS10n_4cC0mplisHed_t1m3_t0_g0_h0m3}
```

Flag: `shellmates{m1sS10n_4cC0mplisHed_t1m3_t0_g0_h0m3}`
