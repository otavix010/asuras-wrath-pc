// Asura's Wrath's own part of the frame rate (the common part is port/frame_rate.h). Two places hold the game at 30,
// both found by boma for Xenia (game-patches, "Unlock FPS"); here they are hooks that follow the fps option instead of
// bytes patched for good:
//   0x8299A70C  li r11,2: the XDK's presentation interval, the common PortPresentInterval (config/ganchos.toml).
//   sub_824D7110  the engine's tick-rate cap: 0 (none) unless a global flag is set, then a field of the engine
//               (1224); at 60 fps or more always 0, the vertical blank alone paces the game.

#pragma once

#include <rex/hook.h>
#include <rex/ppc.h>

#include "port/frame_rate.h"

REX_EXTERN(__imp__sub_824D7110);

REX_HOOK_RAW(sub_824D7110) {
  __imp__sub_824D7110(ctx, base);
  if (HighFrameRate()) ctx.f1.f64 = 0.0;
}
