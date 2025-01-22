import time

class Tween:
    def __init__(self):
        self.tween = "linear"
        self.start_time = 0.0
        self.end_time = 0.0
        self.start_value = (0.0, 0.0)
        self.end_value = (0.0, 0.0)
        self.current_value = (0.0, 0.0)
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
    def ease(self, t):
        if self.tween == "linear":
            return self.ease_linear(t)
        elif self.tween == "ease_in":
            return self.ease_in(t)
        elif self.tween == "ease_out":
            return self.ease_out(t)
        elif self.tween == "ease_in_out":
            return self.ease_in_out(t)
    def ease_linear(self, t):
        return (self.start_value[0] + (self.end_value[0] - self.start_value[0]) * t,
                self.start_value[1] + (self.end_value[1] - self.start_value[1]) * t)
    def ease_in(self, t):
        return (self.start_value[0] + (self.end_value[0] - self.start_value[0]) * t * t,
                self.start_value[1] + (self.end_value[1] - self.start_value[1]) * t * t)
    def ease_out(self, t):
        return (self.start_value[0] + (self.end_value[0] - self.start_value[0]) * (1 - (1 - t) * (1 - t)),
                self.start_value[1] + (self.end_value[1] - self.start_value[1]) * (1 - (1 - t) * (1 - t)))
    def ease_in_out(self, t):
        if t < 0.5:
            return (self.start_value[0] + (self.end_value[0] - self.start_value[0]) * 2 * t * t,
                    self.start_value[1] + (self.end_value[1] - self.start_value[1]) * 2 * t * t)
        else:
            return (self.start_value[0] + (self.end_value[0] - self.start_value[0]) * (1 - 2 * (1 - t) * (1 - t)),
                    self.start_value[1] + (self.end_value[1] - self.start_value[1]) * (1 - 2 * (1 - t) * (1 - t)))
    def get_value(self):
        return self.current_value
    def is_running(self):
        return self.running
    def stop(self):
        self.running = False
        self.current_value = self.end_value
        if self.on_complete:
            self.on_complete()
    def reset(self):
        self.running = False
        self.current_value = self.start_value
        self.on_complete = None