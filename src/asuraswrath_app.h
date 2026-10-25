// asuraswrath - ReXGlue Recompiled Project
//
// The port's app: paths beside the executable (the game in assets, saves in usuario), the Xenos GPU by default.

#pragma once

#include <cstdio>
#include <cstdlib>
#include <filesystem>

#include <rex/filesystem.h>
#include <rex/rex_app.h>
#include <rex/system/xmemory.h>

class AsurasWrathApp : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(
      rex::ui::WindowedAppContext& ctx) {
    return std::unique_ptr<AsurasWrathApp>(new AsurasWrathApp(ctx, "asuraswrath",
        PPCImageConfig));
  }

  // the game in assets beside the executable unless game_data_root says otherwise; saves and caches in usuario
  void OnConfigurePaths(rex::PathConfig& paths) override {
    auto exe_dir = rex::filesystem::GetExecutableFolder();
    if (paths.game_data_root.empty()) paths.game_data_root = exe_dir / "assets";
    if (paths.user_data_root == rex::filesystem::GetUserFolder() / GetName()) {
      paths.user_data_root = exe_dir / "usuario";
      paths.cache_root = paths.user_data_root / "cache";
    }
  }

  // the Xbox 360 GPU (Xenos), unless gpu_plugin names another
  void OnPreSetup(rex::RuntimeConfig& config) override {
    if (config.gpu_plugin.empty() && !config.graphics) config.gpu_plugin = "xenos";
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
