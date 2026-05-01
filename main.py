import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from capture import ScreenCapture
from input_handler import InputHandler
from overlay import OverlayWindow
from ui import SettingsWindow
import config

class EventBridge(QObject):
    t_overlay = Signal(object)
    m_switch = Signal()
    z_change = Signal(float, bool)
    s_next = Signal()
    s_prev = Signal()

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    cfg = config.load_config()

    try:
        t_fps = 0 if cfg.get("no_delay_mode", False) else cfg.get("update_rate", 144)
        cap = ScreenCapture(target_fps=t_fps)
    except Exception as e:
        print(f"Cap init fail: {e}")
        sys.exit(1)

    ovl = None
    inp = None
    ui = None

    def on_cfg_chg():
        if ovl: ovl.update_config(cfg)
        if inp:
            inp.config = cfg
            inp.setup_hotkeys()
        if cap and hasattr(cap, "set_fps"):
            try: cap.set_fps(0 if cfg.get("no_delay_mode", False) else cfg.get("update_rate", 144))
            except: pass
        if cap and hasattr(cap, "set_monitor"):
            try: cap.set_monitor(cfg.get("monitor_index", 0))
            except: pass

    def d_tog(f_state):
        if ovl: ovl.toggle(f_state)

    def d_mode():
        m = ["mouse_following", "center", "fixed"]
        c = cfg.get("mode", "mouse_following")
        try:
            i = m.index(c)
            cfg["mode"] = m[(i + 1) % len(m)]
        except:
            cfg["mode"] = "mouse_following"
        if ui: ui.mode_combo.setCurrentText(cfg["mode"])
        on_cfg_chg()

    def d_zoom(nz):
        cfg["zoom_level"] = nz
        p = cfg.get("scope_presets", [1.1, 1.5, 2.0, 2.5, 3.0, 4.0])
        if nz in p: cfg["scope_index"] = p.index(nz)
        if ui:
            ui.zoom_slider.setValue(int(nz * 10))
            ui.zoom_label.setText(f"{nz}x")
        on_cfg_chg()

    def d_next():
        p = cfg.get("scope_presets", [1.1, 1.5, 2.0, 2.5, 3.0, 4.0])
        i = (cfg.get("scope_index", 0) + 1) % len(p)
        cfg["scope_index"] = i
        d_zoom(p[i])

    def d_prev():
        p = cfg.get("scope_presets", [1.1, 1.5, 2.0, 2.5, 3.0, 4.0])
        i = (cfg.get("scope_index", 0) - 1) % len(p)
        cfg["scope_index"] = i
        d_zoom(p[i])

    def d_zc(delta, is_scrl):
        if is_scrl and not ovl.active: return
        cz = cfg.get("zoom_level", 2.0)
        nz = max(1.1, min(40.0, cz + delta))
        cfg["zoom_level"] = nz
        if ui:
            ui.zoom_slider.setValue(int(nz * 10))
            ui.zoom_label.setText(f"{nz}x")
        on_cfg_chg()

    b = EventBridge()
    b.t_overlay.connect(d_tog)
    b.m_switch.connect(d_mode)
    b.z_change.connect(d_zc)
    b.s_next.connect(d_next)
    b.s_prev.connect(d_prev)

    def t_ovl_bg(fs=None): b.t_overlay.emit(fs)
    def m_sw_bg(): b.m_switch.emit()
    def z_ch_bg(d, s): b.z_change.emit(d, s)
    def s_nx_bg(): b.s_next.emit()
    def s_pv_bg(): b.s_prev.emit()

    inp = InputHandler(cfg, t_ovl_bg, m_sw_bg, z_ch_bg, s_nx_bg, s_pv_bg)
    ovl = OverlayWindow(cap, inp, cfg)

    ui = SettingsWindow(cfg, on_cfg_chg)
    ui.show()

    def on_close(e): app.quit()
    ui.closeEvent = on_close

    r = app.exec()
    inp.stop()
    cap.stop()
    sys.exit(r)

if __name__ == "__main__":
    main()
