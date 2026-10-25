// mostrar_fps: the game's frame rate in the top-left corner, counted at each frame the game hands to the GPU (right
// after its VdSwap, the midasm hook AwFrame in config/asuraswrath.toml) and shown twice a second.

#pragma once

#include <atomic>
#include <chrono>
#include <cstdint>

#include <imgui.h>
#include <rex/cvar.h>
#include <rex/ui/imgui_dialog.h>

REXCVAR_DEFINE_BOOL(mostrar_fps, false, "Port", "Show the frame rate in the top-left corner");

inline std::atomic<uint64_t> g_guest_frames{0};

void AwFrame() { g_guest_frames.fetch_add(1, std::memory_order_relaxed); }

class FpsOverlay final : public rex::ui::ImGuiDialog {
 public:
  explicit FpsOverlay(rex::ui::ImGuiDrawer* drawer) : ImGuiDialog(drawer), last_time_(Clock::now()) {}

 protected:
  void OnDraw(ImGuiIO& io) override {
    (void)io;
    auto now = Clock::now();
    double seconds = std::chrono::duration<double>(now - last_time_).count();
    if (seconds >= 0.5) {
      uint64_t frames = g_guest_frames.load(std::memory_order_relaxed);
      fps_ = double(frames - last_frames_) / seconds;
      last_frames_ = frames;
      last_time_ = now;
    }
    ImGui::SetNextWindowPos(ImVec2(8, 8));
    ImGui::SetNextWindowBgAlpha(0.45f);
    constexpr ImGuiWindowFlags kFlags = ImGuiWindowFlags_NoDecoration | ImGuiWindowFlags_NoInputs |
                                        ImGuiWindowFlags_AlwaysAutoResize | ImGuiWindowFlags_NoSavedSettings |
                                        ImGuiWindowFlags_NoFocusOnAppearing | ImGuiWindowFlags_NoNav;
    if (ImGui::Begin("##fps", nullptr, kFlags)) {
      if (fps_ > 0)
        ImGui::Text("%.0f fps  %.1f ms", fps_, 1000.0 / fps_);
      else
        ImGui::Text("-- fps");
    }
    ImGui::End();
  }

 private:
  using Clock = std::chrono::steady_clock;
  Clock::time_point last_time_;
  uint64_t last_frames_ = 0;
  double fps_ = 0;
};
