"""Runs the port in a window on the left monitor (never fullscreen) for some seconds, with screenshots.

    py -3 scripts/rodar.py [--segundos 60] [--prints 15,30,55] [--var NOME=valor ...]

Screenshots go to tela_<s>.png, the log to out/build/win-amd64-release/run.log."""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from iterar import BUILD, ROOT, move_left  # noqa: E402

CAPTURE = r'C:\Users\otavi\fifast2-port\scripts\captura.ps1'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--segundos', type=float, default=60)
    ap.add_argument('--prints', default='15,30,55')
    ap.add_argument('--var', action='append', default=[])
    a = ap.parse_args()
    log = BUILD / 'run.log'
    log.unlink(missing_ok=True)
    env = dict(os.environ, REX_LOG_FILE=str(log), REX_GAME_DATA_ROOT=str(ROOT / 'assets'), REX_FULLSCREEN='false')
    for v in a.var:
        k, _, val = v.partition('=')
        env[k] = val
    p = subprocess.Popen([str(BUILD / 'asuraswrath.exe')], cwd=BUILD, env=env)
    marks = sorted(float(x) for x in a.prints.split(',') if x)
    t0, moved = time.time(), False
    while time.time() - t0 < a.segundos and p.poll() is None:
        time.sleep(0.3)
        if not moved:
            moved = move_left(p.pid)
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


if __name__ == '__main__':
    main()
