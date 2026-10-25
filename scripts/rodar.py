"""Runs the port in a window on the left monitor (never fullscreen) for some seconds, with screenshots.

    py -3 scripts/rodar.py [--segundos 60] [--prints 15,30,55 | --cada 30] [--novo] [--ciclo 80] [--var NOME=valor ...]

--novo starts a new game on EASY from the title screen (a save must exist: the first run makes it); --ciclo S from second
S goes round every button, trigger and both sticks' four directions, for the QTEs; scripts/tecla.py presses more while
it runs. Screenshots go to tela_<s>.png, the log to out/build/win-amd64-release/run.log."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iterar import BUILD, ROOT, move_left, window_state  # noqa: E402

CAPTURE = r'C:\Users\otavi\fifast2-port\scripts\captura.ps1'


def cycle(start, end):
    """every button, the triggers, both sticks' four directions and the left stick turning round both ways, round and
    round (12 s), for QTEs met unseen"""
    period, out = 12.0, []
    steps = [(0, 'A', 0.15), (0.5, 'B', 0.15), (1, 'X', 0.15), (1.5, 'Y', 0.15), (2, 'RT', 0.4),
             (2.5, 'LY-+RY-', 0.8), (3.5, 'LY++RY+', 0.8), (4.5, 'LX-+RX-', 0.8), (5.5, 'LX++RX+', 0.8),
             (6.5, 'LT+RT', 0.4), (8, 'LROT', 1.8), (10, 'LROT-', 1.8)]
    steps += [(7 + i * 0.2, 'B', 0.1) for i in range(5)]  # a burst, for the mashing ones
    for at, button, hold in steps:
        out.append(f'{start + at:g}-{end:g}@{period:g}/{hold:g}:{button}')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--segundos', type=float, default=60)
    ap.add_argument('--prints', default='15,30,55')
    ap.add_argument('--cada', type=float, default=0)
    ap.add_argument('--novo', action='store_true')
    ap.add_argument('--ciclo', type=float, default=0)
    ap.add_argument('--var', action='append', default=[])
    a = ap.parse_args()
    if a.cada:
        a.prints = ','.join(str(int(x * a.cada)) for x in range(1, int(a.segundos / a.cada) + 1))
    pad = []
    if a.novo:
        pad += ['45:START', '58:A', '64:A', '67:A', '70:UP', '72.5:A']
    if a.ciclo:
        pad += cycle(a.ciclo, a.segundos)
    live = BUILD / 'pad_live.txt'
    live.write_text('', encoding='ascii')
    log = BUILD / 'run.log'
    log.unlink(missing_ok=True)
    fps_log = BUILD / 'fps.log'
    fps_log.unlink(missing_ok=True)
    env = dict(os.environ, REX_LOG_FILE=str(log), REX_GAME_DATA_ROOT=str(ROOT / 'assets'), REX_FULLSCREEN='false',
               REX_HEADLESS='true', AW_PAD=','.join(pad), AW_PAD_LIVE=str(live), AW_FPS_LOG=str(fps_log))
    for v in a.var:
        k, _, val = v.partition('=')
        env[k] = val
    p = subprocess.Popen([str(BUILD / 'asuraswrath.exe')], cwd=BUILD, env=env)
    marks = sorted(float(x) for x in a.prints.split(',') if x)
    t0, moved, last_state = time.time(), False, None
    while time.time() - t0 < a.segundos and p.poll() is None:
        time.sleep(0.3)
        if not moved:
            moved = move_left(p.pid)
        state = window_state(p.pid)
        if moved and state != last_state:
            print(f'janela aos {time.time() - t0:.1f} s: {state}', flush=True)
            last_state = state
            # back to the left monitor whenever it leaves it (it is never to sit on the main one)
            if any(x > -500 for x, y, w, h, zoomed in state):
                move_left(p.pid)
        while marks and time.time() - t0 >= marks[0]:
            s = int(marks.pop(0))
            subprocess.run(['powershell', '-NoProfile', '-File', CAPTURE, '-Id', str(p.pid),
                            '-Saida', str(ROOT / f'tela_{s}.png')], capture_output=True)
            print(f'print aos {s} s', flush=True)
    if p.poll() is None:
        p.kill()
        p.wait()
        print(f'fechado aos {a.segundos:.0f} s')
    else:
        print(f'saiu com {p.returncode} aos {time.time() - t0:.0f} s')
    summarize_fps(fps_log, a.cada or 30)


def summarize_fps(path, window):
    """the frame rate per window of seconds: lowest and mean of the per-second counts"""
    if not path.exists():
        return
    rows = [line.split() for line in path.read_text().splitlines() if line.strip()]
    per_window = {}
    for t, n in rows:
        per_window.setdefault(int(float(t) // window), []).append(int(n))
    print('fps por trecho (mínimo / média):')
    for w, counts in sorted(per_window.items()):
        print(f'  {w * window:>5.0f}-{(w + 1) * window:<5.0f} s  {min(counts):>3} / {sum(counts) / len(counts):5.1f}')


if __name__ == '__main__':
    main()
