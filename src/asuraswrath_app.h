// asuraswrath - ReXGlue Recompiled Project
//
// The port's app: the common base of the Xbox 360 ports (port/port_app.h) and Asura's Wrath's own hooks, the
// engine's tick-rate cap (tick_rate.h). Its render targets go through ROV on NVIDIA: at 2x its fights took 76-99% of
// an RTX 5080 through RTV and 38-47% through ROV, the picture the same (port/port_options.h).

#pragma once

#include "port/port_app.h"

#include "tick_rate.h"

class AsurasWrathApp : public PortApp {
 public:
  using PortApp::PortApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(rex::ui::WindowedAppContext& ctx) {
    crash_log::Install();
    port::g_rov_on_nvidia = true;
    return std::unique_ptr<AsurasWrathApp>(new AsurasWrathApp(ctx, "asuraswrath", PPCImageConfig));
  }
};
