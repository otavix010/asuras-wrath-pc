// fps = 30 (the original), 60 or more. Two places hold the game at 30, both found by boma for Xenia (game-patches,
// "Unlock FPS"); here they are hooks that follow the option instead of bytes patched for good:
//   0x8299A70C  li r11,2: the presentation interval handed to the GPU, 2 vertical blanks a frame; 1 at 60 fps
//               (the midasm hook in config/asuraswrath.toml).
//   sub_824D7110  the engine's tick-rate cap: 0 (none) unless a global flag is set, then a field of the engine
//               (1224); at 60 fps always 0, the vertical blank alone paces the game.
// Above 60 the console's vertical blank itself runs faster (video_mode_refresh_rate, unless set): 120 fps is a blank
// every 8.3 ms.

#pragma once

#include <string>

#include <rex/cvar.h>
#include <rex/hook.h>
#include <rex/ppc.h>

REXCVAR_DEFINE_INT32(fps, 60, "Port", "Frame rate: 30 (the original), 60, 120, 144...");

inline bool HighFrameRate() { return REXCVAR_GET(fps) >= 60; }

// before the GPU starts: the vertical blank at the frame rate when it is above 60
inline void ApplyFrameRate() {
  int fps = REXCVAR_GET(fps);
  if (fps > 60 && rex::cvar::GetFlagSource("video_mode_refresh_rate") == rex::cvar::Source::kDefault)
    rex::cvar::SetFlagByName("video_mode_refresh_rate", std::to_string(fps));
}

void AwPresentInterval(PPCRegister& r11) {
  if (HighFrameRate()) r11.u64 = 1;
}

REX_EXTERN(__imp__sub_824D7110);

REX_HOOK_RAW(sub_824D7110) {
  __imp__sub_824D7110(ctx, base);
  if (HighFrameRate()) ctx.f1.f64 = 0.0;
}
