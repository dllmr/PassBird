# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""PassBird — Generate randomised passwords from bird names."""

import re
import secrets
import string
import sys

SYMBOLS = "!@#$%^&*-_+="

# Base/family bird names extracted from bto_species_codes.pdf (240 species → 150 unique)
BIRD_NAMES = [
    "Avocet", "Bittern", "Blackbird", "Blackcap", "Bluethroat", "Brambling",
    "Bullfinch", "Bunting", "Buzzard", "Capercaillie", "Chaffinch",
    "Chiffchaff", "Chough", "Coot", "Cormorant", "Corncrake", "Crake",
    "Crossbill", "Crow", "Cuckoo", "Curlew", "Dipper", "Diver", "Dotterel",
    "Dove", "Duck", "Dunlin", "Dunnock", "Eagle", "Egret", "Eider", "Falcon",
    "Fieldfare", "Firecrest", "Flycatcher", "Fulmar", "Gadwall", "Gannet",
    "Garganey", "Godwit", "Goldcrest", "Goldeneye", "Goldfinch", "Goosander",
    "Goose", "Goshawk", "Grebe", "Greenfinch", "Greenshank", "Grouse",
    "Guillemot", "Guineafowl", "Gull", "Harrier", "Hawfinch", "Heron",
    "Hobby", "Hoopoe", "Jackdaw", "Jay", "Kestrel", "Kingfisher", "Kite",
    "Kittiwake", "Knot", "Lapwing", "Linnet", "Magpie", "Mallard", "Martin",
    "Merganser", "Merlin", "Moorhen", "Nightingale", "Nightjar", "Nuthatch",
    "Oriole", "Osprey", "Ouzel", "Owl", "Oystercatcher", "Parakeet",
    "Partridge", "Peregrine", "Petrel", "Phalarope", "Pheasant", "Pigeon",
    "Pintail", "Pipit", "Plover", "Pochard", "Ptarmigan", "Puffin", "Quail",
    "Rail", "Raven", "Razorbill", "Redpoll", "Redshank", "Redstart",
    "Redwing", "Robin", "Rook", "Rosefinch", "Ruff", "Sanderling", "Sandpiper",
    "Scaup", "Scoter", "Serin", "Shag", "Shearwater", "Shelduck", "Shorelark",
    "Shoveler", "Shrike", "Siskin", "Skua", "Skylark", "Snipe", "Sparrow",
    "Sparrowhawk", "Starling", "Stint", "Stonechat", "Swallow", "Swan",
    "Swift", "Teal", "Tern", "Thrush", "Tit", "Treecreeper", "Turnstone",
    "Twite", "Wagtail", "Warbler", "Wheatear", "Whimbrel", "Whinchat",
    "Whitethroat", "Wigeon", "Woodcock", "Woodlark", "Woodpecker",
    "Woodpigeon", "Wren", "Wryneck", "Yellowhammer",
]


def parse_code(code: str) -> tuple[int, int, int]:
    """Parse a password code like '3b2d1s' into (birds, digits, symbols)."""
    m = re.match(r"^(\d+)b(?:(\d+)d)?(?:(\d+)s)?$", code)
    if not m:
        print(
            "Usage: passbird [<N>b[<N>d][<N>s]]\n"
            "\n"
            "  N = count, b = bird names, d = digits, s = symbols\n"
            "  At least 1b is required. d and s default to 0.\n"
            "\n"
            "Examples:\n"
            "  passbird 3b2d1s   # 3 birds, 2 digits, 1 symbol\n"
            "  passbird 2b1d     # 2 birds, 1 digit\n"
            "  passbird 1b       # 1 bird only\n"
            "  passbird          # default: 3b2d1s",
            file=sys.stderr,
        )
        sys.exit(1)

    assert m is not None
    birds = int(m.group(1))
    digits = int(m.group(2)) if m.group(2) else 0
    symbols = int(m.group(3)) if m.group(3) else 0

    if birds < 1:
        print("Error: at least one bird name (1b) is required.", file=sys.stderr)
        sys.exit(1)

    return birds, digits, symbols


def generate_password(bird_names: list[str], birds: int, digits: int, symbols: int) -> str:
    """Generate a password from bird names, digits, and symbols."""
    # Pick random bird names (with replacement)
    chosen_birds = [secrets.choice(bird_names) for _ in range(birds)]

    # Generate random digits and symbols
    fillers: list[str] = []
    for _ in range(digits):
        fillers.append(secrets.choice(string.digits))
    for _ in range(symbols):
        fillers.append(secrets.choice(SYMBOLS))

    # Distribute fillers into slots (one slot after each bird name)
    slots: list[list[str]] = [[] for _ in range(birds)]
    for filler in fillers:
        slot_idx = secrets.randbelow(birds)
        slots[slot_idx].append(filler)

    # Shuffle each slot
    for slot in slots:
        for i in range(len(slot) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            slot[i], slot[j] = slot[j], slot[i]

    # Concatenate: Bird1 + slot1 + Bird2 + slot2 + ...
    parts: list[str] = []
    for bird, slot in zip(chosen_birds, slots):
        parts.append(bird)
        parts.extend(slot)

    return "".join(parts)


def main() -> None:
    if len(sys.argv) > 2:
        print("Usage: passbird [<N>b[<N>d][<N>s]]", file=sys.stderr)
        sys.exit(1)

    code = sys.argv[1] if len(sys.argv) == 2 else "3b2d1s"
    birds, digits, symbols = parse_code(code)
    password = generate_password(BIRD_NAMES, birds, digits, symbols)
    print(password)


if __name__ == "__main__":
    main()
