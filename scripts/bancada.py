"""Asura's Wrath's GPU bench: the same stretch, Episode 4's first fight, under each configuration given, to compare
what each runtime option costs. Each run: the game started with the options, Episode 4 from the episode menu, its
opening left to play, the village walked until the fight (explorar.py), then the fight played (qte.py) for some
seconds while the frame rate and the GPU's use are logged; the fight's averages are printed.

    py -3 scripts/bancada.py --luta 150 "2x" "1x:REX_RESOLUTION_SCALE=1" "rov:REX_RENDER_TARGET_PATH_D3D12=rov"
    py -3 scripts/bancada.py --prints 8,16,24 "rtv" "rov:REX_RENDER_TARGET_PATH_D3D12=rov"   the same moments, to compare

scripts/ref_lista.png, a crop of the episode list's heading, stays out of the repository (the game's picture)."""
import argparse
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from explorar import letterbox  # noqa: E402
from port import BUILD, EXE, ROOT  # noqa: E402
from qte import camera  # noqa: E402
from tecla import press  # noqa: E402


def wait(seconds):
    time.sleep(seconds)


def on_list():
    """the episode menu's list on screen: its EASY/NORMAL/HARD heading like the reference's"""
    from PIL import Image
    cam = camera()
    shot = cam.grab().convert('L').crop((460, 172, 720, 198))
    cam.close()
    ref = Image.open(ROOT / 'scripts' / 'ref_lista.png').convert('L')
    diff = np.abs(np.asarray(shot, dtype=float) - np.asarray(ref, dtype=float)).mean()
    return diff < 20


def lines(path):
    try:
        return path.read_text().splitlines()
    except OSError:
        return []


def start(label, env, fps_overlay=True):
    """the game started with env and Episode 4 begun (the moment Yes is pressed): its rodar.py process, or None"""
    subprocess.run(['taskkill', '/F', '/IM', EXE.name], capture_output=True)
    wait(3)
    args = [sys.executable, '-I', str(ROOT / 'scripts' / 'rodar.py'), '--segundos', '1500', '--prints', '1499',
            '--pad', '45:START', '--var', f'REX_MOSTRAR_FPS={"true" if fps_overlay else "false"}']
    for item in env:
        args += ['--var', item]
    game = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    wait(72)
    # the notice, then the title's EPISODE MENU (marked when there is a save), confirmed by the list's
    # EASY/NORMAL/HARD heading; the list does not wrap, so 5 up and 3 down is Episode 4 wherever the mark was;
    # then PLAY, and Yes on "Start episode?" (No is marked)
    press('A', 0.2)
    wait(8)
    press('A', 0.2)
    wait(3)
    if not on_list():
        print(f'[{label}] o menu de episódios não abriu; rodada descartada', flush=True)
        game.kill()
        return None
    for button, after in [('UP', 0.6)] * 5 + [('DOWN', 0.6)] * 3 + [('A', 2.5), ('A', 2.5), ('UP', 0.8)]:
        press(button, 0.15 if button in ('UP', 'DOWN') else 0.2)
        wait(after)
    press('A', 0.2)
    return game


def shots(label, env, times):
    """prints of Episode 4's opening at the same moments after Yes, for comparing options' pictures"""
    game = start(label, env, fps_overlay=False)
    if not game:
        return
    t0 = time.time()
    cam = camera()
    out = ROOT / 'comparar'
    out.mkdir(exist_ok=True)
    for t in times:
        wait(max(t0 + t - time.time(), 0))
        cam.grab().save(out / f'{label}_{t:05.1f}.png')
    cam.close()
    game.kill()
    subprocess.run(['taskkill', '/F', '/IM', EXE.name], capture_output=True)
    print(f'[{label}] {len(times)} prints em {out}', flush=True)


def run(label, env, fight_seconds):
    game = start(label, env)
    if not game:
        return
    wait(5)
    # the opening: wait for 8 s running without a cutscene's bars, then walk
    cam = camera()
    clear, t0 = 0.0, time.time()
    while clear < 8 and time.time() - t0 < 300:
        clear = clear + 0.5 if not letterbox(np.asarray(cam.grab())) else 0.0
        wait(0.5)
    cam.close()
    walk = subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'explorar.py'), '--segundos', '600',
                           '--passo', '6'], cwd=ROOT, capture_output=True, text=True)
    print(f'[{label}] {walk.stdout.strip()}', flush=True)
    fps_first = len(lines(BUILD / 'fps.log'))
    gpu_start = len(lines(BUILD / 'gpu.log'))
    subprocess.run([sys.executable, '-I', str(ROOT / 'scripts' / 'qte.py'), '--jogar', str(fight_seconds), '--ciclo'],
                   cwd=ROOT, capture_output=True)
    fps = [int(x.split()[1]) for x in lines(BUILD / 'fps.log')[fps_first:] if len(x.split()) == 2]
    gpu = [int(x) for x in lines(BUILD / 'gpu.log')[gpu_start:] if x.strip().isdigit()]
    out = ROOT / 'comparar'
    out.mkdir(exist_ok=True)
    (out / f'{label}_luta.txt').write_text('\n'.join(f'{f} {g}' for f, g in zip(fps, gpu + [0] * len(fps))))
    for log in ('run.log',):
        try:
            (out / f'{label}_{log}').write_bytes((BUILD / log).read_bytes())
        except OSError:
            pass
    game.kill()
    subprocess.run(['taskkill', '/F', '/IM', EXE.name], capture_output=True)
    if not fps:
        print(f'[{label}] sem medição')
        return
    fps_a = np.array(fps)
    print(f'[{label}] luta {len(fps)} s: fps médio {fps_a.mean():.1f}, 1% pior {np.percentile(fps_a, 1):.0f}, '
          f'segundos abaixo de 55: {(fps_a < 55).sum()}, GPU média {np.mean(gpu) if gpu else 0:.0f}%', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--luta', type=float, default=150)
    ap.add_argument('--prints', help='instead of a fight, prints of the opening at these seconds after Yes, e.g. 8,16,24')
    ap.add_argument('configs', nargs='+')
    a = ap.parse_args()
    for config in a.configs:
        label, _, rest = config.partition(':')
        env = [x for x in rest.split(',') if x]
        if a.prints:
            shots(label, env, [float(x) for x in a.prints.split(',')])
        else:
            run(label, env, a.luta)


if __name__ == '__main__':
    main()
