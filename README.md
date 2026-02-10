# PassBird

A CLI utility that generates memorable, randomised passwords composed of bird names, digits, and symbols.

Bird names are derived from the [BTO](https://www.bto.org/) (British Trust for Ornithology) species code list — 150 unique base names like *Kestrel*, *Ptarmigan*, and *Yellowhammer*.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Usage

```bash
uv run passbird.py [<code>]
```

The code describes the password composition: `<N>b[<N>d][<N>s]` where **b** = bird names, **d** = digits, **s** = symbols.

```
uv run passbird.py 3b2d1s   # 3 birds, 2 digits, 1 symbol (default)
uv run passbird.py 2b1d     # 2 birds, 1 digit
uv run passbird.py 1b       # 1 bird only
```

Example output:

```
Kestrel4#Ptarmigan7Yellowhammer
```

At least one bird name (`1b`) is required. Passwords always start with a bird name. Digits and symbols are distributed between bird names or placed at the end.

- **Digits**: `0-9`
- **Symbols**: `!@#$%^&*-_+=`

## Running Tests

```bash
uv run --with pytest pytest test_passbird.py -v
```

## Licence

MIT
