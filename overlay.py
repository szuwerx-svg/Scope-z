import cv2
import numpy as np
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QImage, QPainter, QColor, QPen, QPainterPath

class OverlayWindow(QWidget):
    def __init__(self, cap, input_hndlr, cfg):
        super().__init__()
        self.cap = cap
        self.inputs = input_hndlr
        self.cfg = cfg
        self.active = False
        self.frame = None
        self.frame_id = 0
        self.painted_id = -1
        self.t_rect = QRect(0, 0, 0, 0)
        self.prev_g = None
        self.trig = False
        self.c_bright = 0

        self._scr = None
        self._dpr = 1.0
        self._sx = 0
        self._sy = 0
        self._sw = 0
        self._sh = 0
        self._ref_scr()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool | Qt.WindowType.WindowTransparentForInput)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self._set_geo()
        self._hide_capture()

        self.tmr = QTimer(self)
        self.tmr.setTimerType(Qt.TimerType.PreciseTimer)
        self.tmr.setInterval(0)
        self.tmr.timeout.connect(self.upd_frame)

    def _ref_scr(self):
        scrs = QApplication.screens()
        i = max(0, min(self.cfg.get("monitor_index", 0), len(scrs) - 1))
        self._scr = scrs[i]
        g = self._scr.geometry()
        self._dpr = self._scr.devicePixelRatio()
        self._sx, self._sy, self._sw, self._sh = g.x(), g.y(), g.width(), g.height()

    def _set_geo(self):
        self.setGeometry(self._sx, self._sy, self._sw, self._sh)

    def _hide_capture(self):
        import sys
        if sys.platform == "win32":
            import ctypes
            try: ctypes.windll.user32.SetWindowDisplayAffinity(int(self.winId()), 0x11)
            except: pass

    def update_config(self, c):
        self.cfg = c
        self._ref_scr()
        self._set_geo()
        t = 0 if c.get("no_delay_mode", False) else max(1, int(1000 / c.get("update_rate", 144)))
        self.tmr.setInterval(t)

    def toggle(self, f=None):
        self.active = f if f is not None else not self.active
        if self.active:
            self.show()
            self.raise_()
            self.tmr.start()
        else:
            self.tmr.stop()
            self.hide()

    def upd_frame(self):
        if not self.active: return
        c = self.cfg
        m = c.get("mode", "mouse_following")
        ls = c.get("lens_size", 300)
        z = max(1.01, c.get("zoom_level", 2.0))
        dpr = self._dpr

        if m in ("center", "custom"):
            ox = c.get("center_offset_x", 0)
            oy = c.get("center_offset_y", 0)
            cxl = self._sw / 2.0 + ox
            cyl = self._sh / 2.0 + oy
            cxp = self.cap.width / 2.0 + ox * dpr
            cyp = self.cap.height / 2.0 + oy * dpr
        elif m == "mouse_following":
            mx, my = self.inputs.get_mouse_pos()
            cxp = mx - self._sx * dpr
            cyp = my - self._sy * dpr
            cxl = cxp / dpr
            cyl = cyp / dpr
        else:
            cxl = self._sw - ls / 2.0
            cyl = ls / 2.0
            cxp = self.cap.width - ls * dpr / 2.0
            cyp = ls * dpr / 2.0

        self.t_rect = QRect(int(cxl - ls / 2), int(cyl - ls / 2), ls, ls)
        shalf = max(1, int((ls * dpr) / z / 2))
        r = (int(cxp - shalf), int(cyp - shalf), int(cxp + shalf), int(cyp + shalf))
        
        f = self.cap.get_frame(r)
        if f is None or f.size == 0: return

        if not hasattr(self, "_ltr") or self._ltr != self.t_rect:
            self._ltr = self.t_rect

        h, w = f.shape[:2]
        self.c_bright = float(np.mean(f[h // 2, w // 2, :3]))

        f = self._fx(f)
        if not f.flags["C_CONTIGUOUS"]: f = np.ascontiguousarray(f)
        h, w, ch = f.shape
        self.frame = QImage(f.data, w, h, ch * w, QImage.Format.Format_ARGB32)
        self.frame_id += 1
        self.update()

    def _fx(self, img):
        c = self.cfg
        cnt = c.get("contrast", 100) / 100.0
        brt = c.get("brightness", 0)
        if cnt != 1.0 or brt != 0:
            img = cv2.convertScaleAbs(img, alpha=cnt, beta=brt)

        shp = c.get("sharpness", 0)
        if shp > 0:
            b = cv2.GaussianBlur(img, (0, 0), 3)
            img = cv2.addWeighted(img, 1 + shp * 0.5, b, -shp * 0.5, 0)

        if c.get("night_vision", False):
            g = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            gn = cv2.applyColorMap(g, cv2.COLORMAP_SUMMER)
            bgra = cv2.cvtColor(gn, cv2.COLOR_BGR2BGRA)
            bgra[:, :, 3] = 255
            img = bgra

        if c.get("edge_detect", False):
            g = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            e = cv2.Canny(g, 80, 160)
            hl = np.zeros_like(img)
            hl[e > 0] = [0, 220, 80, 255]
            img = cv2.addWeighted(img, 1.0, hl, 0.7, 0)

        return img

    def paintEvent(self, e):
        p = QPainter(self)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        p.fillRect(self.rect(), Qt.GlobalColor.transparent)
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)

        if not self.active or self.frame is None:
            p.end()
            return

        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.cfg.get("interpolation") != "nearest":
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        c = self.cfg
        sh = c.get("lens_shape", "circle")

        cp = QPainterPath()
        if sh == "circle": cp.addEllipse(self.t_rect)
        else: cp.addRoundedRect(self.t_rect, 8, 8)

        p.setClipPath(cp)
        p.drawImage(self.t_rect, self.frame)
        p.setClipping(False)

        self._draw_cross(p, c)
        self._draw_bdr(p, c, sh)
        p.end()

    def _draw_cross(self, p, c):
        if c.get("vignette", False):
            from PySide6.QtGui import QRadialGradient
            cx, cy = self.t_rect.center().x(), self.t_rect.center().y()
            r = self.t_rect.width() / 2
            g = QRadialGradient(cx, cy, r)
            g.setColorAt(0.7, QColor(0, 0, 0, 0))
            g.setColorAt(1.0, QColor(0, 0, 0, 200))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(g)
            p.drawEllipse(self.t_rect)

        if not c.get("crosshair_enabled", True): return

        col_raw = c.get("crosshair_color", [168, 85, 247, 255])
        o = c.get("crosshair_opacity", 255)
        t = c.get("crosshair_thickness", 2)
        gp = c.get("crosshair_gap", 5)
        d = c.get("crosshair_dot", True)
        ds = c.get("crosshair_dot_size", 2)
        s = c.get("crosshair_style", "classic")
        out = c.get("crosshair_outline", True)

        da = c.get("crosshair_size", 10)
        a = {
            "t": c.get("ch_arm_top", da),
            "b": c.get("ch_arm_bottom", da),
            "l": c.get("ch_arm_left", da),
            "r": c.get("ch_arm_right", da),
        }

        col = QColor(0, 255, 0, 255) if getattr(self, "trig", False) and c.get("trigger_flash", False) else QColor(col_raw[0], col_raw[1], col_raw[2], o)
        blk = QColor(0, 0, 0, o)
        cx, cy = self.t_rect.center().x(), self.t_rect.center().y()

        def d_arms(pc, ex=0):
            p.setPen(QPen(pc, t + ex, Qt.PenStyle.SolidLine, Qt.PenCapStyle.FlatCap))
            if s in ("classic", "T-shape"):
                if a["l"] > 0: p.drawLine(cx - gp - a["l"], cy, cx - gp, cy)
                if a["r"] > 0: p.drawLine(cx + gp, cy, cx + gp + a["r"], cy)
                if a["t"] > 0: p.drawLine(cx, cy - gp - a["t"], cx, cy - gp)
                if a["b"] > 0 and s == "classic": p.drawLine(cx, cy + gp, cx, cy + gp + a["b"])
            elif s == "circle dot":
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(cx - da, cy - da, da * 2, da * 2)
            elif s == "sniper":
                r = self.t_rect.width() // 2
                if a["l"] > 0: p.drawLine(cx - r, cy, cx - gp, cy)
                if a["r"] > 0: p.drawLine(cx + gp, cy, cx + r, cy)
                if a["t"] > 0: p.drawLine(cx, cy - r, cx, cy - gp)
                if a["b"] > 0: p.drawLine(cx, cy + gp, cx, cy + r)

        if out: d_arms(blk, 2)
        d_arms(col)

        if d or s in ("dot only", "circle dot"):
            dcol = QColor(0, 0, 0, o) if c.get("smart_invert_dot", False) and self.c_bright > 127 else (QColor(255, 255, 255, o) if c.get("smart_invert_dot", False) else col)
            if out:
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(blk)
                p.drawEllipse(cx - ds - 1, cy - ds - 1, (ds + 1) * 2, (ds + 1) * 2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(dcol)
            p.drawEllipse(cx - ds, cy - ds, ds * 2, ds * 2)

    def _draw_bdr(self, p, c, sh):
        bc = c.get("border_color", [124, 58, 237, 220])
        bt = c.get("border_thickness", 2)
        bo = c.get("border_opacity", 255)
        if bt <= 0 or bo <= 0: return
        p.setPen(QPen(QColor(bc[0], bc[1], bc[2], bo), bt))
        p.setBrush(Qt.BrushStyle.NoBrush)
        if sh == "circle": p.drawEllipse(self.t_rect)
        else: p.drawRoundedRect(self.t_rect, 8, 8)
