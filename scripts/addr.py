"""Dutch address normalization, shared by every importer.

The primary key of this dataset is an ADDRESS, not a business name, because that
is how the gedooglijst works: the burgemeester tolerates cannabis sales at listed
addresses. Names, owners and brands are tenancies that come and go. So matching
correctly is the whole game, and Amsterdam street names have several traps that
break naive comparison.
"""

import re
import unicodedata

# The trap that eats every first pass: the same street is written five ways.
# "1e Const. Huygensstraat" == "EERSTE CONSTANTIJN HUYGENSSTRAAT".
ORDINALS = {
    "EERSTE": "1E", "1STE": "1E", "1ST": "1E", "1": "1E",
    "TWEEDE": "2E", "2DE": "2E", "2ND": "2E",
    "DERDE": "3E", "3DE": "3E",
    "VIERDE": "4E", "4DE": "4E",
    "VIJFDE": "5E", "5DE": "5E",
}

# Abbreviations that appear in one source and not another.
EXPANSIONS = {
    "ADM": "ADMIRAAL",
    "CONST": "CONSTANTIJN",
    "BURG": "BURGEMEESTER",
    "ST": "SINT",
    "PRINS": "PRINS",
    "JAC": "JACOB",
    "JOH": "JOHANNES",
    "NIC": "NICOLAAS",
    "TT": "TT",          # Tt. Vasumweg, genuinely two letters
    "PC": "PC",          # PC Hooftstraat
}

# Trailing tokens some sources append and the roster never does.
NOISE = {"AMSTERDAM", "NL", "NEDERLAND", "NETHERLANDS"}


def fold(s):
    """Uppercase, strip diacritics and punctuation, collapse whitespace."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.upper().replace("'", " ").replace("`", " ").replace("\u2019", " ")
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def street_key(street):
    """Canonical street token sequence: ordinals numeric, abbreviations expanded."""
    out = []
    for tok in fold(street).split():
        if tok in NOISE:
            continue
        tok = ORDINALS.get(tok, tok)
        tok = EXPANSIONS.get(tok, tok)
        out.append(tok)
    # A leading bare "1E"/"2E" is the common case; also handle it mid-name.
    return " ".join(out)


def split_number(raw):
    """'104 H' / '104H' / '88-90' / '2 A' -> (number, suffix). Ranges keep the low end."""
    s = fold(raw)
    m = re.match(r"^(\d+)\s*[-/]\s*\d+\s*(.*)$", s)     # 88-90 -> 88, note the range
    if m:
        return m.group(1), fold(m.group(2))
    m = re.match(r"^(\d+)\s*([A-Z]{0,3})$", s)
    if m:
        return m.group(1), m.group(2)
    m = re.match(r"^(\d+)", s)
    return (m.group(1) if m else ""), fold(s[m.end():]) if m else ""


def parse_freeform(addr):
    """'Amstelveenseweg 61, 1075 VV Amsterdam' -> dict of parts."""
    a = (addr or "").replace("\n", " ").strip()
    postcode = ""
    m = re.search(r"\b(\d{4})\s*([A-Za-z]{2})\b", a)
    if m:
        postcode = f"{m.group(1)}{m.group(2).upper()}"
        a = (a[: m.start()] + " " + a[m.end():]).strip()
    a = a.split(",")[0].strip()
    m = re.match(r"^(.*?)\s+(\d.*)$", a)
    if not m:
        return {"street": a, "number": "", "suffix": "", "postcode": postcode}
    street, rest = m.group(1), m.group(2)
    number, suffix = split_number(rest)
    return {"street": street, "number": number, "suffix": suffix, "postcode": postcode}


def address_key(street, number, suffix=""):
    """The join key. Suffix is deliberately EXCLUDED.

    Huisletters disagree constantly between sources (the roster says AMSTEL 8 H,
    a directory says Amstel 8). Matching on street+number and then reporting the
    suffix disagreement is right; matching on street+number+suffix silently drops
    real shops.
    """
    return f"{street_key(street)}|{str(number).lstrip('0') or number}"


PARTICLES = {"van", "der", "den", "de", "het", "te", "ten", "ter", "op", "aan", "in", "'t", "bij"}


def dutch_title(street):
    """'EERSTE VAN DER HELSTSTRAAT' -> 'Eerste van der Helststraat'.

    The roster is all caps. Naive .title() produces 'Van Der Helststraat', which is
    wrong in Dutch and looks wrong on a label.
    """
    out = []
    for i, tok in enumerate(street.lower().split()):
        if i and tok in PARTICLES:
            out.append(tok)
        elif re.match(r"^\d+e$", tok):          # 1e, 2e stay lowercase after the digit
            out.append(tok)
        else:
            out.append(tok[:1].upper() + tok[1:])
    return " ".join(out)


def subject_id(street, number, suffix=""):
    """Stable human-readable ID for an address. Suffix included, so it is unique."""
    s = street_key(street).lower().replace(" ", "-")
    n = str(number) + (suffix or "").lower()
    return f"{s}-{n}".strip("-")
