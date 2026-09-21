# Chapter 4 — Unicode Text Versus Bytes

> *"The best way to avoid Unicode pain is to follow the Unicode sandwich: always decode on input, always encode on output, and handle only str internally."*

---

## 🎯 Core Concept

Python 3 makes a hard distinction: `str` is Unicode text, `bytes` is raw binary. Understanding encodings, codec errors, and normalization is essential for any program that handles text from the real world.

---

## 📐 Character Issues

```
Code point  → Abstract identity (U+0041 = LATIN CAPITAL LETTER A)
Encoding    → Algorithm to convert code points to bytes (UTF-8, UTF-16, Latin-1)
Decoding    → Bytes → str (code points)
Encoding    → str → bytes

str  = sequence of Unicode code points
bytes = sequence of raw bytes (0–255)
```

```python
s = 'café'
len(s)           # 4 characters

b = s.encode('utf-8')
b                # b'caf\xc3\xa9'
len(b)           # 5 bytes — é is 2 bytes in UTF-8

b.decode('utf-8')  # 'café'
```

---

## 🔢 Byte Essentials

```python
# bytes and bytearray — immutable vs. mutable
b1 = bytes([99, 97, 102, 101])    # b'cafe'
b2 = bytearray(b'café')           # mutable

# Access produces integers, slice produces bytes
b1[0]       # 99   (int)
b1[0:1]     # b'c' (bytes)

# Constructors
bytes('café', 'utf-8')            # b'caf\xc3\xa9'
bytes.fromhex('31 4B CE A9')      # b'1K\xce\xa9'
```

---

## 🌐 Basic Encoders/Decoders

```python
# UTF-8 — variable width (1-4 bytes), handles all Unicode, web default
'Hello'.encode('utf-8')      # b'Hello'       (ASCII subset, 1 byte each)
'こんにちは'.encode('utf-8')  # 3 bytes per Japanese char

# Latin-1 / ISO-8859-1 — Western European, 1 byte each
'café'.encode('latin-1')     # b'caf\xe9'

# UTF-16 — 2+ bytes, includes BOM (Byte Order Mark)
'café'.encode('utf-16')      # b'\xff\xfec\x00a\x00f\x00\xe9\x00'

# cp1252 — Windows Western European
'café'.encode('cp1252')      # b'caf\xe9'
```

---

## 🛠️ Handling Encode/Decode Errors

```python
city = 'São Paulo'

# Default: strict — raises on unencodable char
city.encode('ascii')         # UnicodeEncodeError: 'ã' not in ASCII

# errors='replace' — substitute ? for unencodable
city.encode('ascii', errors='replace')   # b'S?o Paulo'

# errors='ignore' — silently drop unencodable
city.encode('ascii', errors='ignore')    # b'So Paulo'

# errors='xmlcharrefreplace' — HTML entities
city.encode('ascii', errors='xmlcharrefreplace')  # b'S&#227;o Paulo'

# Decode errors
octets = b'Montr\xe9al'
octets.decode('utf-8', errors='replace')   # 'Montr\ufffdal' (U+FFFD replacement char)
octets.decode('latin-1')                   # 'Montréal' — correct
```

---

## 🥪 The Unicode Sandwich Pattern

```
Input          Processing       Output
(bytes)  →→→  decode  →→→  str  →→→  encode  →→→  bytes
```

```python
# CORRECT approach
def read_process_write(filename):
    with open(filename, 'rb') as f:        # read as bytes
        raw = f.read()
    text = raw.decode('utf-8')              # decode once at the boundary
    result = process(text)                  # work entirely in str
    with open('output.txt', 'w', encoding='utf-8') as f:
        f.write(result)                     # encode at output boundary

# NEVER mix bytes and str in the middle of processing
```

---

## 🔤 Unicode Normalization

```python
# The problem: same visual character, different code points
s1 = 'café'    # 4 chars: e + combining acute accent (U+0301)
s2 = 'café'    # 4 chars: é as precomposed character (U+00E9)

len(s1)        # 5
len(s2)        # 4
s1 == s2       # False! — different representations

# Solution: normalize before comparing
from unicodedata import normalize

normalize('NFC', s1) == normalize('NFC', s2)   # True
# NFC — Canonical Decomposition followed by Canonical Composition (preferred for text)
# NFD — Canonical Decomposition
# NFKC/NFKD — Compatibility forms (fold ligatures, subscripts, etc.)

# Case folding (lowercase for comparison)
'Straße'.casefold()  # 'strasse' — German ß → ss
```

---

## 🗂️ Sorting Unicode Text

```python
fruits = ['caju', 'atemoia', 'cajá', 'açaí', 'acerola']
sorted(fruits)
# ['acerola', 'atemoia', 'açaí', 'caju', 'cajá'] — wrong! ç and á out of place

# Correct: use locale-aware collation
import locale
locale.setlocale(locale.LC_COLLATE, 'pt_BR.UTF-8')
sorted(fruits, key=locale.strxfrm)
# ['açaí', 'acerola', 'atemoia', 'cajá', 'caju'] ✓

# Better: pyuca (Unicode Collation Algorithm, no locale needed)
import pyuca
coll = pyuca.Collator()
sorted(fruits, key=coll.sort_key)
```

---

## 🔑 Key Takeaways

- `str` = Unicode text (code points); `bytes` = binary data — never mix them
- The "Unicode sandwich": decode at input, encode at output, work in `str` internally
- Explicit encoding everywhere: `open(f, encoding='utf-8')` not `open(f)`
- Normalize with NFC before comparing or hashing Unicode strings
- Use `casefold()` for case-insensitive matching (not just `lower()`)
- UTF-8 is the right default for almost everything on the web
