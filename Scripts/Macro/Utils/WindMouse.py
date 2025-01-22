import numpy as np
import time;

class WindMouse:
    def __init__(self):
        self.tween = "Wind"
        self.start_time = 0.0
        self.end_time = 0.0
        self.start_value = 0.0
        self.end_value = 0.0
        self.current_value = 0.0
        self.running = False
        self.duration = 1.0
        self.on_complete = None
        
    def set_tween(self, tween):
        self.tween = tween
    def set_duration(self, duration):
        self.duration = duration
    def set_on_complete(self, on_complete):
        self.on_complete = on_complete
    def start(self, start_value, end_value):
        self.start_value = start_value
        self.end_value = end_value
        self.start_time = time.time()
        self.end_time = self.start_time + self.duration
        self.running = True
        
    def update(self):
        if not self.running:
            return
        t = time.time()
        if t >= self.end_time:
            self.running = False
            self.current_value = self.end_value
            if self.on_complete:
                self.on_complete()
        else:
            progress = (t - self.start_time) / self.duration
            self.current_value = self.ease(progress)

    def wind_mouse(self, start_x, start_y, dest_x, dest_y, move_mouse, G_0=9, W_0=3, M_0=15, D_0=12):

        sqrt3 = np.sqrt(3)
        sqrt5 = np.sqrt(5)
        current_x, current_y = start_x, start_y
        v_x = v_y = W_x = W_y = 0
        while (dist := np.hypot(dest_x - start_x, dest_y - start_y)) >= 1:
            W_mag = min(W_0, dist)
            if dist >= D_0:
                W_x = W_x / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
                W_y = W_y / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
            else:
                W_x /= sqrt3
                W_y /= sqrt3
                if M_0 < 3:
                    M_0 = np.random.random() * 3 + 3
                else:
                    M_0 /= sqrt5
            v_x += W_x + G_0 * (dest_x - start_x) / dist
            v_y += W_y + G_0 * (dest_y - start_y) / dist
            v_mag = np.hypot(v_x, v_y)
            if v_mag > M_0:
                v_clip = M_0 / 2 + np.random.random() * M_0 / 2
                v_x = (v_x / v_mag) * v_clip
                v_y = (v_y / v_mag) * v_clip
            start_x += v_x
            start_y += v_y
            move_x = int(np.round(start_x))
            move_y = int(np.round(start_y))
            if current_x != move_x or current_y != move_y:
                # This should wait for the mouse polling interval
                move_mouse(current_x := move_x, current_y := move_y)