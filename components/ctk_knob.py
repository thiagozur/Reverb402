import math
import customtkinter as ctk

class CTkKnob(ctk.CTkCanvas):
    def __init__(self, master, from_ = 0.0, to = 1.0, value = 0.0, command = None, step = None, text = '', size = 70, fg_color = '#1f538d', **kwargs):
        super().__init__(master, width = size, height = size, bg ='#242424', highlightthickness = 0, **kwargs)

        self.from_ = from_
        self.to = to
        self.value = value
        self.command = command
        self.step = step
        self.text = text
        self.size = size
        self.fg_color = fg_color

        self.bind('<B1-Motion>', self._on_motion)
        self.bind('<Button-1>', self._on_button_1)
        self._last_y = 0

        self.update_knob()

    def _on_button_1(self, event):
        self._last_y = event.y

    def _on_motion(self, event):
        delta_y = self._last_y - event.y
        self._last_y = event.y

        sens = 150.0
        parameter_range = self.to - self.from_

        new_value = self.value + (delta_y * (parameter_range / sens))
        new_value = max(self.from_, min(self.to, new_value))

        if self.step is not None:
            new_value = self.from_ + round((new_value - self.from_) / self.step) * self.step
            new_value = max(self.from_, min(self.to, new_value))

        if new_value != self.value:
            self.value = new_value
            self.update_knob()

            if self.command:
                self.command(self.value)

    def get(self):
        return self.value
    
    def set(self, val):
        self.value = max(self.from_, min(self.to, val))
        self.update_knob()

    def update_knob(self):
        self.delete('all')
        cx = self.size / 2
        cy = self.size / 2
        r = (self.size / 2) - 8

        percentage = (self.value - self.from_) / (self.to - self.from_)
        angle_deg = -135 + (percentage * 270)
        angle_rad = math.radians(angle_deg - 90)

        self.create_oval(cx - r, cy - r, cx + r, cy + r, fill = '#1a1a1a', outline = '#333333', width = 2)

        arc_angle_start = 225
        extension = angle_deg - arc_angle_start

        self.create_arc(cx - r + 3, cy - r + 3, cx + r -3, cy + r - 3, start = arc_angle_start, extent = extension, style = 'arc', outline = self.fg_color, width = 4)

        ix = cx + (r - 4) * math.cos(angle_rad)
        iy = cy + (r - 4) * math.sin(angle_rad)
        self.create_line(cx, cy, ix, iy, fill = '#FFFFFF', width = 3, capstyle = 'round')