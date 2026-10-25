"""Finds functions reached only through pointers kept in data: every aligned word of the image outside the code that
points into the code, at a plausible function start not yet known, goes into config/asuraswrath.toml.

    py -3 scripts/varrer_ponteiros.py imagem.bin [--gravar]

imagem.bin: the loaded image (AW_DUMP_IMAGE=file on a run). A plausible start: the word before is a return (blr),
an unconditional branch or padding, or the word itself opens a frame (mflr r12, stwu r1)."""
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PCH = ROOT / 'generated' / 'default' / 'asuraswrath_pch.h'
REGISTER = ROOT / 'generated' / 'default' / 'asuraswrath_register.cpp'
CONFIG = ROOT / 'config' / 'asuraswrath.toml'


def define(name):
    return int(re.search(rf'#define {name} (0x[0-9A-Fa-f]+)', PCH.read_text()).group(1), 16)


def main():
    image = Path(sys.argv[1]).read_bytes()
    write = '--gravar' in sys.argv
    base, code, code_size = define('REX_IMAGE_BASE'), define('REX_CODE_BASE'), define('REX_CODE_SIZE')
    end = code + code_size
    known = {int(a, 16) for a in re.findall(r'SetFunction\(0x([0-9A-Fa-f]{8})', REGISTER.read_text())}
    declared = {int(a, 16) for a in re.findall(r'^0x([0-9A-Fa-f]{8})\s*=', CONFIG.read_text(), re.M)}

    def word(addr):
        o = addr - base
        return struct.unpack_from('>I', image, o)[0] if 0 <= o <= len(image) - 4 else None

    def plausible(t):
        before, first = word(t - 4), word(t)
        if first is None or first == 0:
            return False
        if first == 0x7D8802A6 or first >> 16 == 0x9421:  # mflr r12 / stwu r1,-n(r1)
            return True
        # the word before ends a function: blr, bctr, an unconditional branch, or padding
        return before in (0x4E800020, 0x4E800420, 0) or (before is not None and before >> 26 == 18 and before & 3 == 0)

    found = {}
    for o in range(0, len(image) - 3, 4):
        addr = base + o
        if code <= addr < end:
            continue  # the code itself: its own constants are not pointers
        v = struct.unpack_from('>I', image, o)[0]
        if code <= v < end and v % 4 == 0 and v not in known and v not in declared and plausible(v):
            found.setdefault(v, addr)
    print(f'{len(known)} funções conhecidas, {len(declared)} declaradas, {len(found)} candidatas novas')
    for v in sorted(found)[:15]:
        print(f'  0x{v:08X} (ponteiro em 0x{found[v]:08X})')
    if write and found:
        lines = ''.join(f'0x{v:08X} = {{}}\n' for v in sorted(found))
        CONFIG.write_text(CONFIG.read_text(encoding='utf-8').rstrip('\n') +
                          '\n\n# pointers in data to plausible function starts (scripts/varrer_ponteiros.py)\n' + lines,
                          encoding='utf-8')
        print('gravadas em', CONFIG)


if __name__ == '__main__':
    main()
