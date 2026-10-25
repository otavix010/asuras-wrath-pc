// asuraswrath - ReXGlue Recompiled Project
//
// The port's app: paths beside the executable (the game in assets, saves in usuario), the Xenos GPU by default.

#pragma once

#include <cstdio>
#include <cstdlib>
#include <filesystem>

#include <rex/cvar.h>
#include <rex/filesystem.h>
#include <rex/filesystem/devices/disc_image_device.h>
#include <rex/filesystem/vfs.h>
#include <rex/input/device_assignment.h>
#include <rex/logging.h>
#include <rex/input/input_system.h>
#include <rex/rex_app.h>
#include <rex/system/xmemory.h>

#include "crash_log.h"
#include "fps_overlay.h"
#include "frame_rate.h"
#include "input_lock.h"
#include "pad_script.h"
#include "port_options.h"

REXCVAR_DEFINE_STRING(iso, "", "Port",
                      "The game's disc image (.iso), read in place; game_data_root then needs only default.xex");

class AsurasWrathApp : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(
      rex::ui::WindowedAppContext& ctx) {
    crash_log::Install();
    return std::unique_ptr<AsurasWrathApp>(new AsurasWrathApp(ctx, "asuraswrath",
        PPCImageConfig));
  }

  // the game in assets beside the executable unless game_data_root says otherwise; saves and caches in usuario; the
  // options in PORT_OPCOES when given (the launcher keeps them at the port's root, which a new build leaves alone)
  void OnConfigurePaths(rex::PathConfig& paths) override {
    auto exe_dir = rex::filesystem::GetExecutableFolder();
    if (const char* options = std::getenv("PORT_OPCOES"))
      paths.config_path = std::filesystem::path(reinterpret_cast<const char8_t*>(options));
    if (paths.game_data_root.empty()) paths.game_data_root = exe_dir / "assets";
    if (paths.user_data_root == rex::filesystem::GetUserFolder() / GetName()) {
      paths.user_data_root = exe_dir / "usuario";
      paths.cache_root = paths.user_data_root / "cache";
    }
  }

  // the Xbox 360 GPU (Xenos), unless gpu_plugin names another; the system's prompts (create the save, pick the
  // storage) answered with their default button unless headless says otherwise: they only take keyboard and mouse
  void OnPreSetup(rex::RuntimeConfig& config) override {
    if (config.gpu_plugin.empty() && !config.graphics) config.gpu_plugin = "xenos";
    if (rex::cvar::GetFlagSource("headless") == rex::cvar::Source::kDefault) rex::cvar::SetFlagByName("headless", "true");
    ApplyFrameRate();
    port_options::Apply();
    // development: AW_PAD puts the scripted controller (pad_script.h) in the controllers' place
    if (const char* script = std::getenv("AW_PAD")) {
      config.input_factory = [script = std::string(script)](bool tool_mode)
          -> std::unique_ptr<rex::system::IInputSystem> {
        // the script alone: it is player one, the profile that is signed in (the default inputs' stand-in pad
        // would take player one and leave the script a player with no profile)
        (void)tool_mode;
        auto input = std::make_unique<rex::input::InputSystem>(nullptr);
        input->AddDriver(std::make_unique<ScriptedPad>(script, std::getenv("AW_PAD_LIVE")));
        input->SetDeviceAssignment(std::make_unique<rex::input::SlotAssignment>());
        return input;
      };
    }
  }

  // iso: game: and d: read the disc image instead of the game folder
  void OnLoadXexImage(std::string& xex_image) override {
    (void)xex_image;
    const std::string& iso = REXCVAR_GET(iso);
    if (iso.empty()) return;
    constexpr const char* kMount = "\Device\Cdrom0";
    auto* fs = runtime()->file_system();
    auto disc = std::make_unique<rex::filesystem::DiscImageDevice>(kMount, std::filesystem::path(reinterpret_cast<const char8_t*>(iso.c_str())));
    if (!disc->Initialize() || !fs->RegisterDevice(std::move(disc))) {
      REXLOG_ERROR("iso: could not read {}; playing from the game folder", iso);
      return;
    }
    for (const char* link : {"game:", "d:"}) {
      fs->UnregisterSymbolicLink(link);
      fs->RegisterSymbolicLink(link, kMount);
    }
    REXLOG_INFO("iso: game: and d: read {}", iso);
  }

  // mostrar_fps: the frame rate in a corner
  void OnCreateDialogs(rex::ui::ImGuiDrawer* drawer) override {
    if (REXCVAR_GET(mostrar_fps)) new FpsOverlay(drawer);  // lives as long as the drawer
  }

  // development: AW_DUMP_IMAGE=file writes the loaded image (code and data, decrypted) for the pointer scan
  void OnPostLoadXexImage() override {
    const char* out = std::getenv("AW_DUMP_IMAGE");
    if (!out) return;
    auto* mem = runtime()->memory();
    const auto* image = mem->TranslateVirtual<const uint8_t*>(PPCImageConfig.image_base);
    if (FILE* f = std::fopen(out, "wb")) {
      std::fwrite(image, 1, PPCImageConfig.image_size, f);
      std::fclose(f);
    }
  }
};
