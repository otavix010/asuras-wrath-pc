// asuraswrath - ReXGlue Recompiled Project
//
// The port's app: the common base of the Xbox 360 ports (port/port_app.h) and Asura's Wrath's own hooks, the
// engine's tick-rate cap (tick_rate.h). Its render targets stay on the runtime's RTV path: ROV took half the GPU at 2x
// (38-47% of an RTX 5080 against 76-99%), but the darkest parts of some models came out green (Wyzen's hands in
// Episode 5), which RTV draws right.

#pragma once

#include "port/port_app.h"

#include "tick_rate.h"

class AsurasWrathApp : public PortApp {
 public:
  using PortApp::PortApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(rex::ui::WindowedAppContext& ctx) {
    crash_log::Install();
    return std::unique_ptr<AsurasWrathApp>(new AsurasWrathApp(ctx, "asuraswrath", PPCImageConfig));
  }
};
