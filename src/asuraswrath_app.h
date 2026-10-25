// asuraswrath - ReXGlue Recompiled Project
//
// The port's app: the common base of the Xbox 360 ports (port/port_app.h) and Asura's Wrath's own hooks, the frame
// rate (frame_rate.h).

#pragma once

#include "port/port_app.h"

#include "frame_rate.h"

class AsurasWrathApp : public PortApp {
 public:
  using PortApp::PortApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(rex::ui::WindowedAppContext& ctx) {
    crash_log::Install();
    return std::unique_ptr<AsurasWrathApp>(new AsurasWrathApp(ctx, "asuraswrath", PPCImageConfig));
  }

  void OnPreSetup(rex::RuntimeConfig& config) override {
    PortApp::OnPreSetup(config);
    ApplyFrameRate();
  }
};
