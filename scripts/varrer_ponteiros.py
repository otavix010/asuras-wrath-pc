"""Finds functions reached only through pointers kept in data: every aligned word of the image outside the code that
points into the code, at a plausible function start not yet known, goes into config/funcoes.toml.

    py -3 scripts/varrer_ponteiros.py imagem.bin [--gravar]

imagem.bin: the loaded image (PORT_DUMP_IMAGE=file on a run). A plausible start: the word before is a return (blr,
bctr), an unconditional branch or padding, or the word itself opens a frame (mflr r12, stwu r1)."""
import bisect
import re
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from port import FUNCS, GENERATED, NAME  # noqa: E402

PCH = GENERATED / f'{NAME}_pch.h'
REGISTER = GENERATED / f'{NAME}_register.cpp'


def define(name):
    return int(re.search(rf'#define {name} (0x[0-9A-Fa-f]+)', PCH.read_text()).group(1), 16)


def main():
    image = Path(sys.argv[1]).read_bytes()
    write = '--gravar' in sys.argv
    base, code, code_size = define('REX_IMAGE_BASE'), define('REX_CODE_BASE'), define('REX_CODE_SIZE')
    end = code + code_size
    known = {int(a, 16) for a in re.findall(r'SetFunction\(0x([0-9A-Fa-f]{8})', REGISTER.read_text())}
    declared = {int(a, 16) for a in re.findall(r'^0x([0-9A-Fa-f]{8})\s*=', FUNCS.read_text(), re.M)}

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

    def candidate(v):
        return code <= v < end and v % 4 == 0 and v not in known and v not in declared and plausible(v)

    found = {}
    for o in range(0, len(image) - 3, 4):
        addr = base + o
        if code <= addr < end:
            continue  # the code itself: its own constants are not pointers
        v = struct.unpack_from('>I', image, o)[0]
        if candidate(v):
            found.setdefault(v, addr)

    # addresses the code builds itself, a callback handed over: lis rD,hi then, a few instructions on,
    # addi rX,rD,lo (hi adjusted for lo's sign) or ori rX,rD,lo. Only one outside the function that builds it: inside,
    # it is that function's own label (the way back from a computed jump), and declaring it would split the function.
    starts = sorted(known | declared)

    def function_of(a):
        i = bisect.bisect_right(starts, a) - 1
        return starts[i] if i >= 0 else None

    built = {}
    for o in range(max(0, code - base), min(len(image), end - base) - 3, 4):
        v = struct.unpack_from('>I', image, o)[0]
        if v >> 26 != 15 or (v >> 16) & 31 != 0:  # lis is addis rD,0,hi
            continue
        rd, hi = (v >> 21) & 31, v & 0xFFFF
        for k in range(1, 9):
            if o + 4 * k > len(image) - 4:
                break
            u = struct.unpack_from('>I', image, o + 4 * k)[0]
            if (u >> 16) & 31 != rd:
                continue
            if u >> 26 == 14:  # addi
                lo = u & 0xFFFF
                t = ((hi << 16) + (lo - 0x10000 if lo & 0x8000 else lo)) & 0xFFFFFFFF
            elif u >> 26 == 24:  # ori
                t = (hi << 16) | (u & 0xFFFF)
            else:
                continue
            if candidate(t) and t not in found and function_of(t) != function_of(base + o):
                built.setdefault(t, base + o)
            break
    print(f'{len(known)} funções conhecidas, {len(declared)} declaradas, {len(found)} candidatas novas nos dados, '
          f'{len(built)} montadas no código')
    for v in sorted(found)[:10]:
        print(f'  0x{v:08X} (ponteiro em 0x{found[v]:08X})')
    for v in sorted(built)[:10]:
        print(f'  0x{v:08X} (montada em 0x{built[v]:08X})')
    if write and (found or built):
        text = FUNCS.read_text(encoding='utf-8').rstrip('\n')
        if found:
            text += '\n\n# pointers in data to plausible function starts (scripts/varrer_ponteiros.py)\n'
            text += ''.join(f'0x{v:08X} = {{}}\n' for v in sorted(found))
        if built:
            text += '\n\n# addresses the code builds (lis + addi/ori) at plausible function starts (scripts/varrer_ponteiros.py)\n'
            text += ''.join(f'0x{v:08X} = {{}}\n' for v in sorted(built))
        FUNCS.write_text(text, encoding='utf-8')
        print('gravadas em', FUNCS)


if __name__ == '__main__':
    main()
