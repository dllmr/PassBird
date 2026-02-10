# Security Audit: PassBird Password Generation

Audit of `passbird.py` focusing on the default configuration `3b2d1s` (3 bird names, 2 digits, 1 symbol). Two threat models are considered: an informed attacker who knows the generation scheme, and an uninformed attacker who does not.

## Algorithm Summary

Passwords are constructed by:

1. Selecting 3 bird names uniformly at random **with replacement** from a fixed list of 150
2. Selecting 2 random digits (`0`-`9`) and 1 random symbol from `!@#$%^&*-_+=` (12 symbols)
3. Randomly distributing the 3 filler characters into slots (one slot after each bird name)
4. Shuffling each slot independently using Fisher-Yates
5. Concatenating: `Bird1 + slot1 + Bird2 + slot2 + Bird3 + slot3`

All randomness uses Python's `secrets` module (CSPRNG).

## Informed Attacker

An attacker who knows the PassBird scheme, the 150-word list, and the password code can enumerate the full search space. Each independent random choice contributes entropy as follows:

| Component | Choices | Entropy (bits) |
|---|---|---|
| Bird names (3 from 150, with replacement) | 150^3 = 3,375,000 | 21.69 |
| Digits (2 from 0-9) | 10^2 = 100 | 6.64 |
| Symbols (1 from 12) | 12 | 3.58 |
| Filler arrangement and ordering\* | 60 | 5.91 |
| **Total** | **~2.43 x 10^11** | **~37.8** |

**Effective entropy of the default `3b2d1s`: approximately 37.8 bits.**

\*The 3 fillers are each independently assigned to one of 3 slots, then each slot is shuffled. The number of distinct ordered arrangements of *f* distinguishable fillers into *b* ordered slots is *f*! x C(*f*+*b*-1, *b*-1). For *f*=3, *b*=3: 3! x C(5,2) = 60. A slight overcounting occurs when both digits share the same value (~10% of cases), but this reduces the effective entropy by less than 0.3 bits.

### Attack Feasibility

The practical impact of ~37.8 bits depends on how the password is stored or verified:

| Scenario | Rate (per GPU) | Time to exhaust search space | Expected time (half) |
|---|---|---|---|
| Argon2id (well-tuned) | ~100/s | ~77 years | ~38 years |
| bcrypt (cost 12) | ~300/s | ~26 years | ~13 years |
| SHA-256 (unsalted) | ~10^9/s | ~4 minutes | ~2 minutes |
| MD5 (unsalted) | ~10^10/s | ~24 seconds | ~12 seconds |
| Online (rate-limited, 10/min) | 10/min | ~46,000 years | ~23,000 years |

With modern password hashing (bcrypt, Argon2), the default provides reasonable resistance against a single GPU. With fast or unsalted hashes, the full search space can be exhausted in seconds to minutes.

## Uninformed Attacker

An attacker unaware of the PassBird scheme faces the full combinatorial space of the output character set. Typical output passwords are 15-35 characters drawn from uppercase letters, lowercase letters, digits, and 12 symbols (74 distinct characters). A brute-force over all strings of length 25 from this character set yields ~74^25 ~ 2^155 candidates -- computationally infeasible.

Standard dictionary attacks and common cracking rule sets would not match PassBird's output pattern. An uninformed attacker would almost certainly fail.

However, **security through obscurity is not a defence**. The algorithm is open-source. If the tool sees any adoption, or if an attacker discovers a PassBird-generated password in a breach and recognises the pattern (title-cased English words separated by digits/symbols), the informed-attacker model applies.

## Implementation Review

| Aspect | Finding | Verdict |
|---|---|---|
| CSPRNG usage | All randomness via `secrets` module | Sound |
| Fisher-Yates shuffle | Correct descending implementation using `secrets.randbelow(i + 1)` for range `[0, i]` | Sound |
| Bird selection | With replacement via `secrets.choice()`; uniform, unbiased | Sound |
| Filler slot assignment | `secrets.randbelow(birds)` per filler; uniform | Sound |
| No modulo bias | `secrets.choice()` and `secrets.randbelow()` avoid modulo bias by design | Sound |

No implementation defects were found. The cryptographic primitives are used correctly.

## Structural Observations

### Word list size is the primary constraint

Each bird name contributes log2(150) = 7.23 bits. This is the dominant factor in per-component entropy and is significantly smaller than comparable schemes (Diceware: log2(7776) = 12.93 bits per word). Increasing the word list size is the most effective single lever for improving entropy.

### Variable-length output

Bird name lengths range from 3 characters (Jay, Owl, Tit) to 13 (Oystercatcher). With `3b2d1s`, total password length varies from ~12 to ~42 characters. In scenarios where an attacker can observe password length without content (e.g. encrypted traffic with known framing), this leaks partial information about which birds were selected, narrowing the search space.

### Filler arrangement contributes modestly

The 60 possible arrangements add ~5.9 bits. The bulk of entropy comes from bird name selection (21.7 bits) and filler values (10.2 bits).

### Bird name adjacency parsing

Some bird names are prefixes of others (e.g. "Goose" / "Goosander"). When two birds are placed adjacently with no filler between them, the output is ambiguous to a parser. This does not weaken the scheme -- it means the attacker's enumeration must try all 150^3 combinations regardless of parsing strategy -- but it is a notable structural property.

## Comparison With Other Schemes

| Scheme | Entropy (bits) |
|---|---|
| PassBird `2b1d1s` | ~24.0 |
| PassBird `3b2d1s` (default) | ~37.8 |
| PassBird `3b3d1s` | ~43.7 |
| PassBird `4b2d1s` | ~46.0 |
| PassBird `4b3d1s` | ~52.2 |
| Random 8-char alphanumeric (a-z, A-Z, 0-9) | ~47.6 |
| Diceware (4 words from 7,776) | ~51.7 |
| PassBird `4b3d2s` | ~58.8 |
| Diceware (6 words from 7,776) | ~77.5 |
| Random 12-char full printable ASCII | ~78.8 |

## Recommendations

1. **Consider increasing the default.** `3b2d1s` at ~37.8 bits is below common minimum recommendations (~40 bits for low-value, ~50+ for general use). A default of `4b3d1s` (~52.2 bits) would bring the scheme to parity with Diceware 4 words while remaining memorable.

2. **Document the entropy.** Users should understand the strength of their chosen configuration so they can select an appropriate code for their threat model.

3. **Consider expanding the word list.** The 150-name list was reduced from 240 BTO species. Recovering compound names (e.g. "BlueTit", "GreatTit") or adding names from additional ornithological sources would improve entropy per word without changing the scheme's character.
