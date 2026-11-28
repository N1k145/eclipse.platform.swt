#!/usr/bin/env python3
###############################################################################
# Copyright (c) 2026 Aleksandar Kurtakov and others.
#
# This program and the accompanying materials
# are made available under the terms of the Eclipse Public License 2.0
# which accompanies this distribution, and is available at
# https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
#
# Contributors:
#     Aleksandar Kurtakov - initial API and implementation
###############################################################################
"""Writes swt-test-font.ttf, a minimal TrueType font for the SWT tests.

Family "SWT Test Font", style Regular. Glyph 0 is .notdef, glyph 1 the empty
space, glyph 2 a 400x700 box drawn for every printable ASCII character
U+0021..U+007E. Only the Python standard library is used.

Usage: python3 generate-swt-test-font.py swt-test-font.ttf
"""
import struct, sys
FAMILY = "SWT Test Font"
SUBFAMILY = "Regular"
PS_NAME = "SWTTestFont-Regular"
COPYRIGHT = "Copyright (c) 2026 Aleksandar Kurtakov and others. EPL-2.0"
UPEM, ASC, DESC = 1000, 800, -200
ADV = 600

def pad4(b):
    return b + b"\0" * (-len(b) % 4)

def checksum(b):
    b = pad4(b)
    return sum(struct.unpack(">%dI" % (len(b) // 4), b)) & 0xFFFFFFFF

# glyf: one box contour, points (100,0) (100,700) (500,700) (500,0), clockwise
box = struct.pack(">hhhhh", 1, 100, 0, 500, 700)
box += struct.pack(">H", 3)            # endPtsOfContours
box += struct.pack(">H", 0)            # instructionLength
box += bytes([0x01] * 4)               # on-curve, int16 deltas
box += struct.pack(">hhhh", 100, 0, 400, 0)
box += struct.pack(">hhhh", 0, 700, 0, -700)
box = pad4(box)
glyphs = [box, b"", box]               # .notdef, space, box
glyf, loca_offsets = b"", []
for g in glyphs:
    loca_offsets.append(len(glyf))
    glyf += g
loca_offsets.append(len(glyf))
loca = struct.pack(">%dI" % len(loca_offsets), *loca_offsets)  # long format

# cmap: format 4, U+0020 -> 1, U+0021..U+007E -> 2
first, last = 0x20, 0x7E
gids = [1] + [2] * (last - first)
seg = 2
body = struct.pack(">HH", last, 0xFFFF)          # endCode
body += struct.pack(">H", 0)                     # reservedPad
body += struct.pack(">HH", first, 0xFFFF)        # startCode
body += struct.pack(">hh", 0, 1)                 # idDelta
body += struct.pack(">HH", seg * 2, 0)           # idRangeOffset
body += struct.pack(">%dH" % len(gids), *gids)   # glyphIdArray
length = 14 + len(body)
sub = struct.pack(">HHHHHHH", 4, length, 0, seg * 2, 4, 1, 0) + body
cmap = struct.pack(">HH", 0, 1) + struct.pack(">HHI", 3, 1, 12) + sub

head = struct.pack(">IIIIHHqqhhhhHHhhh",
    0x00010000, 0x00010000, 0, 0x5F0F3CF5, 0x000B, UPEM,
    0, 0, 100, 0, 500, 700, 0, 8, 2, 1, 0)
hhea = struct.pack(">IhhhHhhhhhh4hhH",
    0x00010000, ASC, DESC, 0, ADV, 0, 100, 500, 1, 0, 0,
    0, 0, 0, 0, 0, 3)
hmtx = struct.pack(">HhHhHh", ADV, 100, 300, 0, ADV, 100)
maxp = struct.pack(">IHHHHHHHHHHHHHH",
    0x00010000, 3, 4, 1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0)
post = struct.pack(">IIhhIIIII", 0x00030000, 0, -100, 50, 0, 0, 0, 0, 0)

os2 = struct.pack(">HhHHH", 4, ADV, 400, 5, 0)
os2 += struct.pack(">10h", 650, 600, 0, 75, 650, 600, 0, 350, 50, 250)
os2 += struct.pack(">h", 0)                       # sFamilyClass
os2 += bytes(10)                                  # panose
os2 += struct.pack(">IIII", 1, 0, 0, 0)           # Basic Latin
os2 += b"SWT "                                    # achVendID
os2 += struct.pack(">HHH", 0x0040, first, last)   # REGULAR
os2 += struct.pack(">hhhHH", ASC, DESC, 0, ASC, -DESC)
os2 += struct.pack(">II", 1, 0)                   # Latin 1 code page
os2 += struct.pack(">hhHHH", 500, 700, 0, 0x20, 1)
assert len(os2) == 96, len(os2)

names = {0: COPYRIGHT, 1: FAMILY, 2: SUBFAMILY, 3: PS_NAME + ";1.0",
         4: FAMILY, 5: "Version 1.0", 6: PS_NAME}
records, strings = b"", b""
for nid, text in sorted(names.items()):
    s = text.encode("utf-16-be")
    records += struct.pack(">HHHHHH", 3, 1, 0x409, nid, len(s), len(strings))
    strings += s
name = struct.pack(">HHH", 0, len(names), 6 + len(records)) + records + strings

tables = {b"OS/2": os2, b"cmap": cmap, b"glyf": glyf, b"head": head,
          b"hhea": hhea, b"hmtx": hmtx, b"loca": loca, b"maxp": maxp,
          b"name": name, b"post": post}
n = len(tables)
font = struct.pack(">IHHHH", 0x00010000, n, 128, 3, n * 16 - 128)
offset = 12 + 16 * n
directory, data = b"", b""
for tag in sorted(tables):
    t = tables[tag]
    directory += struct.pack(">4sIII", tag, checksum(t), offset + len(data), len(t))
    data += pad4(t)
font += directory + data
adj = (0xB1B0AFBA - checksum(font)) & 0xFFFFFFFF
head_off = 12 + 16 * n + sum(len(pad4(tables[t])) for t in sorted(tables) if t < b"head")
font = font[:head_off + 8] + struct.pack(">I", adj) + font[head_off + 12:]

with open(sys.argv[1], "wb") as f:
    f.write(font)
print(len(font), "bytes")
