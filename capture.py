import sys
import numpy as np


class ScreenCapture:
    def __init__(self, target_fps=0, monitor_index=0):
        self.backend = "mss" if sys.platform != "win32" else "dxcam"
        self.mon_idx = monitor_index

        if self.backend == "dxcam":
            import dxcam
            try:
                self.cam = dxcam.create(output_idx=monitor_index, output_color="BGRA")
            except:
                self.cam = dxcam.create(output_color="BGRA")
            if not self.cam:
                raise RuntimeError("dxcam init failed")
            self.cam.start(target_fps=target_fps, video_mode=True)
            self.width = self.cam.width
            self.height = self.cam.height
        else:
            import mss
            self.sct = mss.mss()
            idx = min(monitor_index + 1, len(self.sct.monitors) - 1)
            m = self.sct.monitors[idx]
            self.width = m["width"]
            self.height = m["height"]

    def get_frame(self, region):
        l, t, r, b = region
        l = max(0, min(self.width - 1, l))
        r = max(1, min(self.width, r))
        t = max(0, min(self.height - 1, t))
        b = max(1, min(self.height, b))
        if l >= r or t >= b:
            return None

        if self.backend == "dxcam":
            f = self.cam.get_latest_frame()
            return f[t:b, l:r] if f is not None else None
        else:
            import mss
            idx = min(self.mon_idx + 1, len(self.sct.monitors) - 1)
            mon = self.sct.monitors[idx]
            grab = {"top": mon["top"] + t, "left": mon["left"] + l, "width": r - l, "height": b - t}
            return np.array(self.sct.grab(grab))

    def stop(self):
        try:
            if self.backend == "dxcam": self.cam.stop()
            else: self.sct.close()
        except: pass

    def set_fps(self, fps):
        if self.backend == "dxcam":
            try:
                self.cam.stop()
                self.cam.start(target_fps=fps, video_mode=True)
            except: pass

    def set_monitor(self, idx):
        if self.mon_idx == idx: return
        self.mon_idx = idx
        if self.backend == "dxcam":
            try:
                self.cam.stop()
                import dxcam
                self.cam = dxcam.create(output_idx=idx, output_color="BGRA")
                self.width = self.cam.width
                self.height = self.cam.height
                self.cam.start(video_mode=True)
            except: pass
        else:
            i = min(idx + 1, len(self.sct.monitors) - 1)
            m = self.sct.monitors[i]
            self.width = m["width"]
            self.height = m["height"]
