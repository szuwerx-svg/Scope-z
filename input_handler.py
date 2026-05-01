import keyboard
import win32api
import threading
import time
import mouse


class InputHandler:
    def __init__(self, cfg, on_toggle, on_mode, on_zoom=None, on_next=None, on_prev=None):
        self.cfg = cfg
        self.on_toggle = on_toggle
        self.on_mode = on_mode
        self.on_zoom = on_zoom
        self.on_next = on_next
        self.on_prev = on_prev
        self.alive = True
        self.holding = False
        self._hks = []
        self._mhook = None
        self.setup_hotkeys()
        self._thread = threading.Thread(target=self._hold_loop, daemon=True)
        self._thread.start()

    @property
    def config(self):
        return self.cfg

    @config.setter
    def config(self, val):
        self.cfg = val

    def _mouse_cb(self, ev):
        if isinstance(ev, mouse.WheelEvent) and self.on_zoom:
            step = self.cfg.get("zoom_scroll_step", 5) * 0.1
            self.on_zoom(step if ev.delta > 0 else -step, True)
            return

        if isinstance(ev, mouse.ButtonEvent) and ev.event_type == 'down':
            b = str(ev.button).lower()
            names = [b]
            if b == 'x': names.append('mouse4')
            elif b == 'x2': names.append('mouse5')
            elif b == 'mouse4': names.append('x')
            elif b == 'mouse5': names.append('x2')

            def chk(k):
                return str(self.cfg.get(k, "")).lower() in names

            if chk("hotkey_toggle"): self.on_toggle()
            elif chk("hotkey_mode_switch"): self.on_mode()
            elif chk("hotkey_zoom_in") and self.on_zoom: self.on_zoom(0.5, False)
            elif chk("hotkey_zoom_out") and self.on_zoom: self.on_zoom(-0.5, False)
            elif chk("hotkey_scope_next") and self.on_next: self.on_next()
            elif chk("hotkey_scope_prev") and self.on_prev: self.on_prev()

    def setup_hotkeys(self):
        for h in self._hks:
            try: keyboard.remove_hotkey(h)
            except: pass
        self._hks.clear()

        if self._mhook:
            try: mouse.unhook(self._mhook)
            except: pass
            self._mhook = None

        try:
            c = self.cfg
            binds = [
                (c.get("hotkey_toggle"), self.on_toggle),
                (c.get("hotkey_mode_switch"), self.on_mode),
                (c.get("hotkey_zoom_in"), lambda: self.on_zoom(0.5, False) if self.on_zoom else None),
                (c.get("hotkey_zoom_out"), lambda: self.on_zoom(-0.5, False) if self.on_zoom else None),
                (c.get("hotkey_scope_next"), self.on_next),
                (c.get("hotkey_scope_prev"), self.on_prev),
            ]
            mbtns = ['left', 'right', 'middle', 'x', 'x2', 'mouse4', 'mouse5']
            for key, cb in binds:
                if not key or not cb: continue
                if str(key).lower() in mbtns: continue
                try:
                    self._hks.append(keyboard.add_hotkey(key, cb))
                except:
                    pass

            self._mhook = mouse.hook(self._mouse_cb)
        except:
            pass

    VK = {
        'left': 0x01, 'right': 0x02, 'middle': 0x04,
        'x': 0x05, 'x2': 0x06, 'mouse4': 0x05, 'mouse5': 0x06
    }

    def _hold_loop(self):
        while self.alive:
            hk = self.cfg.get("hotkey_hold", "")
            if hk:
                try:
                    k = str(hk).lower()
                    if k in self.VK:
                        pressed = (win32api.GetAsyncKeyState(self.VK[k]) & 0x8000) != 0
                    else:
                        pressed = keyboard.is_pressed(hk)
                    if pressed and not self.holding:
                        self.holding = True
                        self.on_toggle(True)
                    elif not pressed and self.holding:
                        self.holding = False
                        self.on_toggle(False)
                except:
                    pass
            time.sleep(0.01)

    def get_mouse_pos(self):
        return win32api.GetCursorPos()

    def stop(self):
        self.alive = False
        for h in self._hks:
            try: keyboard.remove_hotkey(h)
            except: pass
        self._hks.clear()
        if self._mhook:
            try: mouse.unhook(self._mhook)
            except: pass
