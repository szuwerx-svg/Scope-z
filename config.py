import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_CONFIG = {
    "zoom_level": 2.0,
    "mode": "mouse_following",
    "lens_size": 300,
    "lens_shape": "circle",
    "border_thickness": 2,
    "border_color": [0, 200, 255, 220],
    "crosshair_enabled": True,
    "crosshair_color": [0, 220, 255, 255],
    "crosshair_style": "classic",
    "crosshair_size": 10,
    "crosshair_gap": 5,
    "crosshair_thickness": 2,
    "crosshair_dot": True,
    "crosshair_dot_size": 2,
    "crosshair_outline": True,
    "crosshair_opacity": 255,
    "ch_arm_top": 10,
    "ch_arm_bottom": 10,
    "ch_arm_left": 10,
    "ch_arm_right": 10,
    "zoom_scroll_step": 5,
    "theme": "Scope Dark",
    "center_offset_x": 0,
    "center_offset_y": 0,
    "hotkey_zoom_in": "]",
    "hotkey_zoom_out": "[",
    "hotkey_toggle": "f8",
    "hotkey_hold": "",
    "hotkey_mode_switch": "f9",
    "hotkey_scope_next": "f10",
    "hotkey_scope_prev": "f11",
    "no_delay_mode": False,
    "scope_presets": [1.1, 1.5, 2.0, 2.5, 3.0, 4.0],
    "scope_index": 0,
    "update_rate": 144,
    "interpolation": "linear",
    "contrast": 100,
    "brightness": 0,
    "sharpness": 0,
    "night_vision": False,
    "edge_detect": False,
    "smart_invert_dot": False,
    "trigger_flash": False,
    "monitor_index": 0,
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                saved = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                if k not in saved:
                    saved[k] = v
            return saved
        except Exception as e:
            print(f"Config load error, using defaults: {e}")
    return DEFAULT_CONFIG.copy()


def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Config save error: {e}")
