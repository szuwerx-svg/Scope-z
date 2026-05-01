import base64
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QComboBox,
    QCheckBox, QPushButton, QColorDialog, QLineEdit, QSpinBox,
    QTabWidget, QGroupBox, QFrame, QInputDialog, QMessageBox, QApplication,
    QListWidget, QStackedWidget
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QPixmap, QIcon
import config as config_mod

THEMES = {
    "Scope Dark": {"bg": "#101010", "surface": "#1a1a1a", "border": "#2c2c2c", "accent": "#ff6a00", "text": "#ffffff", "text_dim": "#8e8e8e", "tab_active": "#ff6a00"},
    "Aether Dark": {"bg": "#0d1117", "surface": "#161b22", "border": "#30363d", "accent": "#58a6ff", "text": "#c9d1d9", "text_dim": "#8b949e", "tab_active": "#1f6feb"},
    "Midnight Purple": {"bg": "#0e0e1a", "surface": "#16162a", "border": "#2e2e4f", "accent": "#a78bfa", "text": "#e2e8f0", "text_dim": "#94a3b8", "tab_active": "#7c3aed"},
    "Tactical Green": {"bg": "#0a0f0a", "surface": "#111811", "border": "#1f3a1f", "accent": "#4ade80", "text": "#dcfce7", "text_dim": "#86efac", "tab_active": "#16a34a"},
    "Crimson": {"bg": "#0f0a0a", "surface": "#1a0f0f", "border": "#3f1515", "accent": "#f87171", "text": "#fecaca", "text_dim": "#fca5a5", "tab_active": "#b91c1c"},
}

def apply_theme(w, t_name):
    t = THEMES.get(t_name, THEMES["Aether Dark"])
    qss = f"""
    QWidget {{ background-color: {t['bg']}; color: {t['text']}; font-family: 'Segoe UI Variable Display', 'Segoe UI', sans-serif; font-size: 13px; }}
    
    QListWidget {{ background: {t['surface']}; border: none; outline: none; border-right: 1px solid {t['border']}; padding-top: 8px; }}
    QListWidget::item {{ color: {t['text_dim']}; padding: 14px 28px; border-left: 3px solid transparent; font-weight: 600; font-size: 13px; }}
    QListWidget::item:selected {{ color: {t['accent']}; border-left: 3px solid {t['accent']}; background: {t['bg']}; }}
    QListWidget::item:hover:!selected {{ color: {t['text']}; background: rgba(255,255,255,0.03); }}
    
    QStackedWidget {{ background: {t['bg']}; }}
    
    QGroupBox {{ border: none; background: {t['surface']}; border-radius: 8px; margin-top: 20px; padding: 16px 18px; padding-top: 32px; font-weight: 700; font-size: 11px; text-transform: uppercase; color: {t['text_dim']}; letter-spacing: 1px; }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 18px; padding: 0 6px; top: 6px; background: transparent; }}
    
    QLabel {{ background: transparent; }}
    
    QSlider::groove:horizontal {{ height: 4px; background: {t['border']}; border-radius: 2px; }}
    QSlider::handle:horizontal {{ background: {t['accent']}; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; border: 2px solid {t['bg']}; }}
    QSlider::sub-page:horizontal {{ background: {t['accent']}; border-radius: 2px; }}
    
    QComboBox {{ background: {t['surface']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 7px 14px; color: {t['text']}; min-height: 22px; }}
    QComboBox:hover {{ border: 1px solid {t['accent']}; }}
    QComboBox QAbstractItemView {{ background: {t['surface']}; border: 1px solid {t['border']}; selection-background-color: {t['accent']}; selection-color: #000; padding: 4px; outline: none; border-radius: 6px; }}
    QSpinBox, QLineEdit {{ background: {t['surface']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 7px 14px; color: {t['text']}; min-height: 22px; }}
    QSpinBox:hover, QLineEdit:hover {{ border: 1px solid {t['accent']}; }}
    
    QPushButton {{ background: {t['surface']}; color: {t['text']}; border: 1px solid {t['border']}; border-radius: 6px; padding: 9px 20px; font-weight: 600; min-height: 20px; }}
    QPushButton:hover {{ border: 1px solid {t['accent']}; color: {t['accent']}; }}
    QPushButton:pressed {{ background: {t['accent']}; color: #000; border: 1px solid {t['accent']}; }}
    
    QCheckBox {{ spacing: 10px; padding: 4px 0; }}
    QCheckBox::indicator {{ width: 36px; height: 20px; border-radius: 10px; background: {t['border']}; }}
    QCheckBox::indicator:checked {{ background: {t['accent']}; }}
    
    QScrollArea {{ border: none; background: transparent; }}
    QScrollBar:vertical {{ background: {t['bg']}; width: 6px; border: none; border-radius: 3px; }}
    QScrollBar::handle:vertical {{ background: {t['border']}; border-radius: 3px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {t['text_dim']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """
    w.setStyleSheet(qss)

def make_scope_icon(accent_hex, size=64):
    pix = QPixmap(size, size)
    pix.fill(QColor(0, 0, 0, 0))
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    c = QColor(accent_hex)
    mid = size // 2
    r = size // 2 - 4
    p.setPen(QPen(c, 3))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawEllipse(mid - r, mid - r, r * 2, r * 2)
    p.drawLine(mid, 2, mid, mid - r + 6)
    p.drawLine(mid, mid + r - 6, mid, size - 2)
    p.drawLine(2, mid, mid - r + 6, mid)
    p.drawLine(mid + r - 6, mid, size - 2, mid)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(c)
    p.drawEllipse(mid - 3, mid - 3, 6, 6)
    p.end()
    return QIcon(pix)

def make_row(lbl_text, w, val_lbl=None):
    r = QHBoxLayout()
    lbl = QLabel(lbl_text)
    lbl.setMinimumWidth(140)
    r.addWidget(lbl)
    r.addWidget(w, 1)
    if val_lbl:
        val_lbl.setMinimumWidth(55)
        r.addWidget(val_lbl)
    return r

def make_slider(vmin, vmax, cur, cb):
    s = QSlider(Qt.Orientation.Horizontal)
    s.setRange(vmin, vmax)
    s.setValue(cur)
    s.valueChanged.connect(cb)
    return s

class CrosshairPreview(QLabel):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setFixedSize(150, 150)
        self.setStyleSheet("background-color: #1a1a1a; border: 1px solid #333; border-radius: 4px;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_preview(self):
        pix = QPixmap(150, 150)
        pix.fill(QColor("#1a1a1a"))
        p = QPainter(pix)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.config.get("crosshair_enabled", True):
            c = self.config.get("crosshair_color", [0, 255, 100, 255])
            op = self.config.get("crosshair_opacity", 255)
            t = self.config.get("crosshair_thickness", 2)
            g = self.config.get("crosshair_gap", 5)
            d = self.config.get("crosshair_dot", True)
            ds = self.config.get("crosshair_dot_size", 2)
            style = self.config.get("crosshair_style", "classic")
            outline = self.config.get("crosshair_outline", True)
            
            def_a = self.config.get("crosshair_size", 10)
            a_top = self.config.get("ch_arm_top", def_a)
            a_bot = self.config.get("ch_arm_bottom", def_a)
            a_l = self.config.get("ch_arm_left", def_a)
            a_r = self.config.get("ch_arm_right", def_a)

            col = QColor(c[0], c[1], c[2], op)
            blk = QColor(0, 0, 0, op)
            cx, cy = 75, 75

            def draw_arms(pc, ext):
                pen = QPen(pc, t + ext, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap)
                p.setPen(pen)
                if style in ("classic", "T-shape"):
                    if a_l > 0: p.drawLine(cx - g - a_l, cy, cx - g, cy)
                    if a_r > 0: p.drawLine(cx + g, cy, cx + g + a_r, cy)
                    if a_top > 0: p.drawLine(cx, cy - g - a_top, cx, cy - g)
                    if a_bot > 0 and style == "classic": p.drawLine(cx, cy + g, cx, cy + g + a_bot)
                elif style == "circle dot":
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawEllipse(cx - def_a, cy - def_a, def_a * 2, def_a * 2)

            if outline: draw_arms(blk, 2)
            draw_arms(col, 0)

            if d or style in ("dot only", "circle dot"):
                if outline:
                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(blk)
                    r = ds + 1
                    p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(col)
                p.drawEllipse(cx - ds, cy - ds, ds * 2, ds * 2)

        p.end()
        self.setPixmap(pix)

class HotkeySignaler(QObject):
    resolved = Signal(str)

class HotkeyButton(QPushButton):
    current_listening = None  # Class variable to track which button is listening

    def __init__(self, current_val, callback):
        super().__init__(str(current_val) if current_val else "Click to Bind")
        self.callback = callback
        self.listening = False
        self.clicked.connect(self.start_listen)
        self.kb_hook = None
        self.ms_hook = None
        self.signaler = HotkeySignaler()
        self.signaler.resolved.connect(self.finish)

    def __del__(self):
        self.stop_listen()

    def start_listen(self):
        if self.listening: return
        if HotkeyButton.current_listening and HotkeyButton.current_listening != self:
            HotkeyButton.current_listening.stop_listen()
        HotkeyButton.current_listening = self
        self.setText("Listening... (Press Esc to clear)")
        self.listening = True
        import keyboard, mouse
        self.kb_hook = keyboard.hook(self.on_kb)
        self.ms_hook = mouse.hook(self.on_ms)

    def stop_listen(self):
        if not self.listening: return
        self.listening = False
        import keyboard, mouse
        try: keyboard.unhook(self.kb_hook)
        except: pass
        try: mouse.unhook(self.ms_hook)
        except: pass
        self.kb_hook = None
        self.ms_hook = None
        self.setText("Click to Bind")
        if HotkeyButton.current_listening == self:
            HotkeyButton.current_listening = None

    def on_kb(self, event):
        if not self.listening or event.event_type != 'down': return
        self.listening = False
        self.signaler.resolved.emit(event.name)

    def on_ms(self, event):
        import mouse
        if not self.listening or not isinstance(event, mouse.ButtonEvent) or event.event_type != 'down': return
        if event.button == 'left': return
        self.listening = False
        self.signaler.resolved.emit(event.button)

    def finish(self, val):
        import keyboard, mouse
        try: keyboard.unhook(self.kb_hook)
        except: pass
        try: mouse.unhook(self.ms_hook)
        except: pass
        self.kb_hook = None
        self.ms_hook = None
        
        if val == 'esc':
            val = ""
            self.setText("Click to Bind")
        else:
            self.setText(str(val))
        self.callback(val)
        HotkeyButton.current_listening = None

class SettingsWindow(QWidget):
    def __init__(self, config, on_config_changed):
        super().__init__()
        self.config = config
        self.on_config_changed = on_config_changed
        self.current_theme = config.get("theme", "Scope Dark")
        self.setWindowTitle("Scope Z")
        self.setMinimumSize(700, 600)
        self.resize(800, 700)
        t = THEMES.get(self.current_theme, THEMES["Scope Dark"])
        self.setWindowIcon(make_scope_icon(t['accent']))
        self.setup_ui()
        apply_theme(self, self.current_theme)

    def setup_ui(self):
        if self.layout():
            QWidget().setLayout(self.layout())
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QFrame()
        header.setFixedHeight(56)
        header.setStyleSheet("background: #0c0c0c; border-bottom: 1px solid #1e1e1e;")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 20, 0)
        
        # Draw scope reticle logo
        logo_pix = QPixmap(28, 28)
        logo_pix.fill(QColor(0, 0, 0, 0))
        lp = QPainter(logo_pix)
        lp.setRenderHint(QPainter.RenderHint.Antialiasing)
        t = THEMES.get(self.current_theme, THEMES["Scope Dark"])
        accent = QColor(t['accent'])
        lp.setPen(QPen(accent, 2))
        lp.setBrush(Qt.BrushStyle.NoBrush)
        lp.drawEllipse(4, 4, 20, 20)
        lp.drawLine(14, 1, 14, 10)
        lp.drawLine(14, 18, 14, 27)
        lp.drawLine(1, 14, 10, 14)
        lp.drawLine(18, 14, 27, 14)
        lp.setPen(Qt.PenStyle.NoPen)
        lp.setBrush(accent)
        lp.drawEllipse(12, 12, 4, 4)
        lp.end()
        logo_label = QLabel()
        logo_label.setPixmap(logo_pix)
        logo_label.setFixedSize(28, 28)
        logo_label.setStyleSheet("background: transparent;")
        
        brand = QLabel("Scope")
        brand.setFont(QFont("Segoe UI Variable Display", 16, QFont.Weight.DemiBold))
        brand.setStyleSheet("color: #fff; background: transparent;")
        accent_x = QLabel("Z")
        accent_x.setFont(QFont("Segoe UI Variable Display", 16, QFont.Weight.ExtraBold))
        accent_x.setStyleSheet(f"color: {t['accent']}; background: transparent;")
        title_row = QHBoxLayout()
        title_row.setSpacing(6)
        title_row.addWidget(logo_label)
        title_row.addWidget(brand)
        title_row.addWidget(accent_x)
        title_row.addStretch()
        hl.addLayout(title_row)
        
        self.status_label = QLabel("  By szuwer  ")
        self.status_label.setStyleSheet(f"background: {t['accent']}; color: #000; border-radius: 10px; font-size: 10px; font-weight: 800; padding: 5px 14px; letter-spacing: 1px;")
        hl.addWidget(self.status_label)
        root.addWidget(header)

        main_layout = QHBoxLayout()
        root.addLayout(main_layout, 1)

        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(160)
        self.stack = QStackedWidget()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack, 1)

        def add_tab(widget, name):
            from PySide6.QtWidgets import QScrollArea
            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setContentsMargins(24, 16, 24, 16)
            cl.addWidget(widget)
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFrameShape(QFrame.Shape.NoFrame)
            scroll.setWidget(container)
            self.stack.addWidget(scroll)
            self.sidebar.addItem(name)

        add_tab(self.build_lens(), "Zoom")
        add_tab(self.build_crosshair(), "Focus Shape")
        add_tab(self.build_hotkeys(), "Control")
        add_tab(self.build_gamer(), "Effects")
        add_tab(self.build_presets(), "Presets")
        add_tab(self.build_themes(), "Themes")
        
        self.sidebar.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        footer = QFrame()
        footer.setFixedHeight(56)
        footer.setStyleSheet("background: #0c0c0c; border-top: 1px solid #2c2c2c;")
        btn_row = QHBoxLayout(footer)
        btn_row.setContentsMargins(20, 8, 20, 8)
        save_btn = QPushButton(">.<  Save")
        save_btn.clicked.connect(lambda: config_mod.save_config(self.config))
        t = THEMES.get(self.current_theme, THEMES["Scope Dark"])
        save_btn.setStyleSheet(f"background: {t['accent']}; color: #000; font-weight: 700; border: none; border-radius: 6px; padding: 10px 24px;")
        reset_btn = QPushButton("Reset Defaults")
        btn_row.addStretch()
        btn_row.addWidget(reset_btn)
        btn_row.addWidget(save_btn)
        reset_btn.clicked.connect(self.reset_defaults)
        root.addWidget(footer)

    def update_cfg(self, k, v, lbl=None, fmt="{}"):
        self.config[k] = v
        if lbl: lbl.setText(fmt.format(v))
        self.on_config_changed()
        if hasattr(self, "preview"): self.preview.update_preview()

    def build_lens(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        zg = QGroupBox("Zoom")
        z_lay = QVBoxLayout(zg)
        self.zoom_label = QLabel(f"{self.config.get('zoom_level', 2.0):.1f}x")
        self.zoom_slider = make_slider(11, 400, int(self.config.get("zoom_level", 2.0) * 10), lambda v: self.update_cfg("zoom_level", v/10.0, self.zoom_label, "{:.1f}x"))
        z_lay.addLayout(make_row("Zoom Level", self.zoom_slider, self.zoom_label))
        zsp = QSpinBox(); zsp.setRange(1, 20); zsp.setValue(self.config.get("zoom_scroll_step", 5))
        zsp.valueChanged.connect(lambda v: self.update_cfg("zoom_scroll_step", v))
        z_lay.addLayout(make_row("Scroll Step", zsp))
        l.addWidget(zg)

        pg = QGroupBox("Position & Monitor")
        p_lay = QVBoxLayout(pg)

        self.mon_combo = QComboBox()
        import PySide6.QtGui as QtGui
        screens = QtGui.QGuiApplication.screens()
        for i, s in enumerate(screens):
            self.mon_combo.addItem(f"Monitor {i} ({s.geometry().width()}x{s.geometry().height()})", i)
        
        idx = min(max(0, self.config.get("monitor_index", 0)), len(screens) - 1)
        self.mon_combo.setCurrentIndex(idx)
        self.mon_combo.currentIndexChanged.connect(lambda v: self.update_cfg("monitor_index", v))
        p_lay.addLayout(make_row("Monitor", self.mon_combo))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["center", "mouse_following", "fixed", "custom"])
        self.mode_combo.setCurrentText(self.config.get("mode", "center"))
        self.mode_combo.currentTextChanged.connect(lambda v: self.update_cfg("mode", v))
        p_lay.addLayout(make_row("Mode", self.mode_combo))
        ox = QSpinBox(); ox.setRange(-3840, 3840); ox.setValue(self.config.get("center_offset_x", 0))
        ox.valueChanged.connect(lambda v: (self.update_cfg("center_offset_x", v), self.mode_combo.setCurrentText("custom") if v != 0 else None))
        oy = QSpinBox(); oy.setRange(-2160, 2160); oy.setValue(self.config.get("center_offset_y", 0))
        oy.valueChanged.connect(lambda v: (self.update_cfg("center_offset_y", v), self.mode_combo.setCurrentText("custom") if v != 0 else None))
        p_lay.addLayout(make_row("Offset X", ox)); p_lay.addLayout(make_row("Offset Y", oy))
        l.addWidget(pg)

        lg = QGroupBox("Appearance")
        l_lay = QVBoxLayout(lg)
        szl = QLabel(f"{self.config.get('lens_size', 300)}px")
        szs = make_slider(25, 4000, self.config.get("lens_size", 300), lambda v: self.update_cfg("lens_size", v, szl, "{}px"))
        l_lay.addLayout(make_row("Size", szs, szl))
        sc = QComboBox(); sc.addItems(["circle", "rectangle"]); sc.setCurrentText(self.config.get("lens_shape", "circle"))
        sc.currentTextChanged.connect(lambda v: self.update_cfg("lens_shape", v))
        l_lay.addLayout(make_row("Shape", sc))
        ic = QComboBox(); ic.addItems(["linear", "cubic", "nearest"]); ic.setCurrentText(self.config.get("interpolation", "linear"))
        ic.currentTextChanged.connect(lambda v: self.update_cfg("interpolation", v))
        l_lay.addLayout(make_row("Quality", ic))
        btl = QLabel(f"{self.config.get('border_thickness', 2)}px")
        bts = make_slider(0, 20, self.config.get("border_thickness", 2), lambda v: self.update_cfg("border_thickness", v, btl, "{}px"))
        l_lay.addLayout(make_row("Border Width", bts, btl))
        cb = QPushButton("Color")
        c = self.config.get("border_color", [0,220,255,220])
        cb.setStyleSheet(f"background: rgba({c[0]},{c[1]},{c[2]},{c[3]})")
        cb.clicked.connect(lambda: self.pick_color("border_color", cb))
        l_lay.addLayout(make_row("Border Color", cb))
        
        bol = QLabel(f"{self.config.get('border_opacity', 255)}")
        bos = make_slider(0, 255, self.config.get("border_opacity", 255), lambda v: self.update_cfg("border_opacity", v, bol, "{}"))
        l_lay.addLayout(make_row("Border Opacity", bos, bol))
        l.addWidget(lg)
        
        l.addStretch()
        return w

    def build_crosshair(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        prev_lay = QHBoxLayout()
        self.preview = CrosshairPreview(self.config)
        self.preview.update_preview()
        prev_lay.addWidget(self.preview)
        
        code_lay = QVBoxLayout()
        imp_btn = QPushButton("Import Valorant Code")
        exp_btn = QPushButton("Copy to Clipboard")
        imp_btn.clicked.connect(self.import_code)
        exp_btn.clicked.connect(self.export_code)
        code_lay.addWidget(imp_btn)
        code_lay.addWidget(exp_btn)
        code_lay.addStretch()
        prev_lay.addLayout(code_lay)
        l.addLayout(prev_lay)

        eg = QGroupBox("Main")
        el = QVBoxLayout(eg)
        cb1 = QCheckBox("Enable"); cb1.setChecked(self.config.get("crosshair_enabled", True))
        cb1.stateChanged.connect(lambda v: self.update_cfg("crosshair_enabled", bool(v)))
        el.addWidget(cb1)
        cb2 = QCheckBox("Center Dot"); cb2.setChecked(self.config.get("crosshair_dot", True))
        cb2.stateChanged.connect(lambda v: self.update_cfg("crosshair_dot", bool(v)))
        el.addWidget(cb2)
        cb3 = QCheckBox("Outline"); cb3.setChecked(self.config.get("crosshair_outline", True))
        cb3.stateChanged.connect(lambda v: self.update_cfg("crosshair_outline", bool(v)))
        el.addWidget(cb3)
        st = QComboBox(); st.addItems(["classic", "T-shape", "dot only", "circle dot", "sniper"])
        st.setCurrentText(self.config.get("crosshair_style", "classic"))
        st.currentTextChanged.connect(lambda v: self.update_cfg("crosshair_style", v))
        el.addLayout(make_row("Style", st))
        l.addWidget(eg)

        dg = QGroupBox("Dimensions")
        dl = QVBoxLayout(dg)
        gl = QLabel(); gs = make_slider(0, 60, self.config.get("crosshair_gap", 5), lambda v: self.update_cfg("crosshair_gap", v, gl, "{}px"))
        dl.addLayout(make_row("Gap", gs, gl)); self.update_cfg("crosshair_gap", self.config.get("crosshair_gap", 5), gl, "{}px")
        tl = QLabel(); ts = make_slider(1, 12, self.config.get("crosshair_thickness", 2), lambda v: self.update_cfg("crosshair_thickness", v, tl, "{}px"))
        dl.addLayout(make_row("Thickness", ts, tl)); self.update_cfg("crosshair_thickness", self.config.get("crosshair_thickness", 2), tl, "{}px")
        dsl = QLabel(); dss = make_slider(1, 20, self.config.get("crosshair_dot_size", 2), lambda v: self.update_cfg("crosshair_dot_size", v, dsl, "{}px"))
        dl.addLayout(make_row("Dot Size", dss, dsl)); self.update_cfg("crosshair_dot_size", self.config.get("crosshair_dot_size", 2), dsl, "{}px")
        l.addWidget(dg)

        ag = QGroupBox("Arms")
        al = QVBoxLayout(ag)
        for k, n in [("ch_arm_top", "Top"), ("ch_arm_bottom", "Bottom"), ("ch_arm_left", "Left"), ("ch_arm_right", "Right")]:
            lbl = QLabel()
            s = make_slider(0, 200, self.config.get(k, 10), lambda v, key=k, lb=lbl: self.update_cfg(key, v, lb, "{}px"))
            al.addLayout(make_row(n, s, lbl))
            self.update_cfg(k, self.config.get(k, 10), lbl, "{}px")
        l.addWidget(ag)

        cg = QGroupBox("Color")
        cl = QVBoxLayout(cg)
        cbtn = QPushButton("Color")
        c = self.config.get("crosshair_color", [0,255,100,255])
        cbtn.setStyleSheet(f"background: rgba({c[0]},{c[1]},{c[2]},{c[3]})")
        cbtn.clicked.connect(lambda: self.pick_color("crosshair_color", cbtn))
        cl.addLayout(make_row("Crosshair Color", cbtn))
        opl = QLabel(); ops = make_slider(10, 255, self.config.get("crosshair_opacity", 255), lambda v: self.update_cfg("crosshair_opacity", v, opl, "{}"))
        cl.addLayout(make_row("Opacity", ops, opl)); self.update_cfg("crosshair_opacity", self.config.get("crosshair_opacity", 255), opl, "{}")
        l.addWidget(cg)
        
        return w

    def build_hotkeys(self):
        w = QWidget(); l = QVBoxLayout(w)
        g = QGroupBox("Keys"); gl = QVBoxLayout(g)
        for k, n in [("hotkey_toggle", "Toggle"), ("hotkey_hold", "Hold to Show"), ("hotkey_mode_switch", "Switch Mode"), ("hotkey_zoom_in", "Zoom In"), ("hotkey_zoom_out", "Zoom Out"), ("hotkey_scope_next", "Scope Next"), ("hotkey_scope_prev", "Scope Prev")]:
            btn = HotkeyButton(self.config.get(k, ""), lambda v, key=k: self.update_cfg(key, v))
            gl.addLayout(make_row(n, btn))
        l.addWidget(g)
        pg = QGroupBox("Engine"); pl = QVBoxLayout(pg)
        fc = QComboBox(); fc.addItems(["60", "120", "144", "165", "240", "360", "1000"])
        fc.setCurrentText(str(self.config.get("update_rate", 144)))
        fc.currentTextChanged.connect(lambda v: self.update_cfg("update_rate", int(v)))
        pl.addLayout(make_row("FPS", fc))
        ndc = QCheckBox("No Delay Mode"); ndc.setChecked(self.config.get("no_delay_mode", False))
        ndc.stateChanged.connect(lambda v: self.update_cfg("no_delay_mode", bool(v)))
        pl.addWidget(ndc)
        l.addWidget(pg); l.addStretch()
        return w

    def build_gamer(self):
        w = QWidget(); l = QVBoxLayout(w)
        vg = QGroupBox("Visual Enhancements"); vl = QVBoxLayout(vg)
        cl = QLabel(); cs = make_slider(50, 200, self.config.get("contrast", 100), lambda v: self.update_cfg("contrast", v, cl, "{}%"))
        vl.addLayout(make_row("Contrast", cs, cl)); self.update_cfg("contrast", self.config.get("contrast", 100), cl, "{}%")
        bl = QLabel(); bs = make_slider(-80, 80, self.config.get("brightness", 0), lambda v: self.update_cfg("brightness", v, bl, "{:+d}"))
        vl.addLayout(make_row("Brightness", bs, bl)); self.update_cfg("brightness", self.config.get("brightness", 0), bl, "{:+d}")
        sl = QLabel(); ss = make_slider(0, 5, self.config.get("sharpness", 0), lambda v: self.update_cfg("sharpness", v, sl, "{}"))
        vl.addLayout(make_row("Sharpness", ss, sl)); self.update_cfg("sharpness", self.config.get("sharpness", 0), sl, "{}")

        nc = QCheckBox("Night Vision"); nc.setChecked(self.config.get("night_vision", False))
        nc.stateChanged.connect(lambda v: self.update_cfg("night_vision", bool(v)))
        vl.addWidget(nc)
        ec = QCheckBox("Edge Detect"); ec.setChecked(self.config.get("edge_detect", False))
        ec.stateChanged.connect(lambda v: self.update_cfg("edge_detect", bool(v)))
        vl.addWidget(ec)
        l.addWidget(vg)
        
        og = QGroupBox("Sniper Lens Optics"); ol = QVBoxLayout(og)
        vc = QCheckBox("Vignette Blackout Mask"); vc.setChecked(self.config.get("vignette", False))
        vc.stateChanged.connect(lambda v: self.update_cfg("vignette", bool(v)))
        ol.addWidget(vc)
        l.addWidget(og)
        
        l.addStretch()
        return w

    def build_presets(self):
        w = QWidget(); l = QVBoxLayout(w)
        sg = QGroupBox("Quick Setup Profiles")
        sg_lay = QVBoxLayout(sg)
        
        btn_sniper = QPushButton("Sniper (3.0x Zoom, Dot)")
        btn_sniper.clicked.connect(lambda: self.apply_preset(3.0, "dot only", 3))
        btn_ar = QPushButton("Assault Rifle (1.5x Zoom, Cross)")
        btn_ar.clicked.connect(lambda: self.apply_preset(1.5, "classic", 2))
        btn_scout = QPushButton("Scout (2.0x Zoom, Circle)")
        btn_scout.clicked.connect(lambda: self.apply_preset(2.0, "circle dot", 2))
        btn_cs2 = QPushButton("CS2 AWP (2.2x Zoom, Cross)")
        btn_cs2.clicked.connect(lambda: self.apply_preset(2.2, "classic", 2))
        btn_valorant = QPushButton("Valorant OP (2.5x Zoom, Dot)")
        btn_valorant.clicked.connect(lambda: self.apply_preset(2.5, "dot only", 3))
        btn_apex = QPushButton("Apex Kraber (3.0x Zoom, Circle)")
        btn_apex.clicked.connect(lambda: self.apply_preset(3.0, "circle dot", 2))
        btn_pubg = QPushButton("PUBG 8x (4.0x Zoom, Sniper)")
        btn_pubg.clicked.connect(lambda: self.apply_preset(4.0, "sniper", 2))

        sg_lay.addWidget(btn_sniper)
        sg_lay.addWidget(btn_ar)
        sg_lay.addWidget(btn_scout)
        sg_lay.addWidget(btn_cs2)
        sg_lay.addWidget(btn_valorant)
        sg_lay.addWidget(btn_apex)
        sg_lay.addWidget(btn_pubg)
        l.addWidget(sg)
        l.addStretch()
        return w

    def build_themes(self):
        w = QWidget(); l = QVBoxLayout(w)
        g = QGroupBox("Colors"); gl = QVBoxLayout(g)
        tc = QComboBox(); tc.addItems(list(THEMES.keys())); tc.setCurrentText(self.current_theme)
        tc.currentTextChanged.connect(self.change_theme)
        gl.addLayout(make_row("Theme", tc))
        l.addWidget(g); l.addStretch()
        return w

    def change_theme(self, name):
        self.config["theme"] = name
        self.current_theme = name
        apply_theme(self, name)
        self.on_config_changed()

    def pick_color(self, key, btn):
        c = self.config.get(key, [255, 255, 255, 255])
        col = QColorDialog.getColor(QColor(*c), self, "Pick", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if col.isValid():
            self.update_cfg(key, [col.red(), col.green(), col.blue(), col.alpha()])
            btn.setStyleSheet(f"background: rgba({col.red()},{col.green()},{col.blue()},{col.alpha()})")

    def export_code(self):
        keys = ["crosshair_enabled", "crosshair_color", "crosshair_opacity", "crosshair_thickness", "crosshair_gap", "crosshair_dot", "crosshair_dot_size", "crosshair_style", "crosshair_outline", "ch_arm_top", "ch_arm_bottom", "ch_arm_left", "ch_arm_right"]
        data = {k: self.config.get(k) for k in keys}
        code = base64.b64encode(json.dumps(data).encode()).decode()
        QApplication.clipboard().setText(f"AETHER-{code}")
        QMessageBox.information(self, "Exported", "Crosshair code copied to clipboard!")

    def import_code(self):
        code, ok = QInputDialog.getText(self, "Import", "Paste code:")
        if not ok or not code: return
        
        if code.startswith("AETHER-"):
            try:
                d = json.loads(base64.b64decode(code[7:]).decode())
                for k, v in d.items(): self.config[k] = v
                self.on_config_changed()
                self.setup_ui()
                QMessageBox.information(self, "Success", "Imported!")
            except:
                QMessageBox.warning(self, "Error", "Invalid Aether code.")
        elif code.startswith("0;"):
            try:
                p = code.split(';')
                vmap = {p[i]: p[i+1] for i in range(len(p)-1)}
                
                clrs = {
                    '0': [255, 255, 255, 255],
                    '1': [0, 255, 0, 255],
                    '2': [173, 255, 47, 255],
                    '3': [255, 255, 0, 255],
                    '4': [0, 255, 255, 255],
                    '5': [255, 0, 255, 255],
                    '6': [255, 0, 0, 255],
                    '7': [255, 255, 255, 255],
                    '8': [255, 255, 255, 255],
                }
                c = vmap.get('c', '1')
                self.config["crosshair_color"] = clrs.get(c, [0, 255, 0, 255])
                self.config["crosshair_dot"] = vmap.get('d', '0') == '1'
                self.config["crosshair_dot_size"] = int(vmap.get('z', '2'))
                self.config["crosshair_outline"] = vmap.get('h', '0') == '1' or vmap.get('o', '0') != '0'
                self.config["crosshair_style"] = "classic"
                self.config["crosshair_thickness"] = int(vmap.get('0t', '2'))
                self.config["crosshair_gap"] = int(vmap.get('0o', '2'))
                
                al = int(vmap.get('0l', '5'))
                self.config["ch_arm_top"] = al
                self.config["ch_arm_bottom"] = al
                self.config["ch_arm_left"] = al
                self.config["ch_arm_right"] = al
                
                self.on_config_changed()
                self.setup_ui()
                QMessageBox.information(self, "Success", "Valorant code imported!")
            except:
                QMessageBox.warning(self, "Error", "Invalid Valorant code.")
        else:
            QMessageBox.warning(self, "Error", "Unknown format.")

    def reset_defaults(self):
        self.config.clear()
        self.config.update(config_mod.DEFAULT_CONFIG)
        self.setup_ui()
        self.on_config_changed()

    def apply_preset(self, zoom, style, dot_size):
        self.update_cfg("zoom_level", zoom, self.zoom_label, "{:.1f}x")
        self.zoom_slider.setValue(int(zoom * 10))
        self.update_cfg("crosshair_style", style)
        self.update_cfg("crosshair_dot_size", dot_size)
        self.setup_ui()
        QMessageBox.information(self, "Preset Applied", f"Applied {style} preset with {zoom}x zoom.")
