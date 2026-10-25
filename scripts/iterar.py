"""Runs the port, and while it stops on a call to a function the analysis missed, declares that function in
config/asuraswrath.toml, regenerates and rebuilds, then runs again.

    py -3 scripts/iterar.py [--vezes 25] [--segundos 40]

Each run: the window on the left monitor, the log in out/build/win-amd64-release/run.log."""
import argparse
import ctypes
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / 'out' / 'build' / 'win-amd64-release'
CONFIG = ROOT / 'config' / 'asuraswrath.toml'
REXGLUE = ROOT.parent / 'rexglue-sdk' / 'win-amd64' / 'bin' / 'rexglue.exe'
MISSING = re.compile(r'Call to invalid or unregistered function at guest address 0x([0-9A-Fa-f]{8})')


def move_left(pid):
    """the game's window to the left monitor, away from the main one"""
    user32 = ctypes.windll.user32
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def each(hwnd, _):
        owner = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            found.append(hwnd)
        return True

    user32.EnumWindows(each, 0)
    for hwnd in found:
        # the whole window on the left monitor (1080x1920 at x=-1080): 1080 wide, 16:9
        user32.SetWindowPos(hwnd, None, -1080, 300, 1080, 640, 0x14)  # NOZORDER | NOACTIVATE
    return bool(found)


def window_state(pid):
    """(x, y, w, h, maximized) of the process's visible windows"""
    user32 = ctypes.windll.user32
    out = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def each(hwnd, _):
        owner = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == pid and user32.IsWindowVisible(hwnd):
            r = (ctypes.c_long * 4)()
            user32.GetWindowRect(hwnd, r)
            out.append((r[0], r[1], r[2] - r[0], r[3] - r[1], bool(user32.IsZoomed(hwnd))))
        return True

    user32.EnumWindows(each, 0)
    return out


def run(seconds):
    log = BUILD / 'run.log'
    log.unlink(missing_ok=True)
    # never fullscreen: a window, moved to the left monitor
    env = dict(os.environ, REX_LOG_FILE=str(log), REX_GAME_DATA_ROOT=str(ROOT / 'assets'), REX_GPU_PLUGIN='xenos',
               REX_FULLSCREEN='false')
    p = subprocess.Popen([str(BUILD / 'asuraswrath.exe')], cwd=BUILD, env=env)
    t0, moved = time.time(), False
    while time.time() - t0 < seconds and p.poll() is None:
        time.sleep(0.3)
        if not moved:
            moved = move_left(p.pid)
    alive = p.poll() is None
    if alive:
        p.kill()
        p.wait()
    text = log.read_text(encoding='utf-8', errors='replace') if log.exists() else ''
    return alive, p.returncode, text


def declare(addr):
    text = CONFIG.read_text(encoding='utf-8')
    key = f'0x{addr.upper()} = {{}}'
    if key in text:
        return False
    CONFIG.write_text(text.rstrip('\n') + f'\n{key}  # called through a pointer\n', encoding='utf-8')
    return True


def rebuild():
    r = subprocess.run([str(REXGLUE), 'codegen', 'asuraswrath_manifest.toml'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        return False
    r = subprocess.run(['cmd', '/c', str(ROOT / 'build.cmd'), 'release'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:])
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--vezes', type=int, default=25)
    ap.add_argument('--segundos', type=float, default=40)
    a = ap.parse_args()
    for n in range(1, a.vezes + 1):
        t0 = time.time()
        alive, code, text = run(a.segundos)
        m = MISSING.search(text)
        if alive:
            print(f'[{n}] rodou {a.segundos:.0f} s sem parar')
            break
        if not m:
            print(f'[{n}] saiu com {code} sem função faltando; fim do log:')
            print('\n'.join(text.splitlines()[-15:]))
            break
        addr = m.group(1)
        if not declare(addr):
            print(f'[{n}] 0x{addr} já declarada e ainda faltando; parando')
            break
        print(f'[{n}] faltava 0x{addr} (rodou {time.time() - t0:.0f} s); gerando e compilando...', flush=True)
        if not rebuild():
            print('falhou a geração ou a compilação')
            break


if __name__ == '__main__':
    main()
