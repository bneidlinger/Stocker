# gui/widgets/vintage_indicators.py
# Contains custom vintage-style indicator widgets like WornLED and NeonLight

import customtkinter as ctk
import math
import random
# --- Added tkinter import for TclError handling ---
import tkinter as tk


class WornLED(ctk.CTkFrame):
    """
    A CustomTkinter widget simulating a worn, flickering LED indicator.
    """
    def __init__(self, master, color="#ff0000", size=30, explicit_canvas_bg=None, **kwargs):
        """
        Initializes the WornLED widget.

        Args:
            master: The parent widget.
            color (str): The base hex color for the LED when 'on'.
            size (int): The diameter of the LED widget.
            explicit_canvas_bg (str | None): Explicit hex color for the canvas background.
                                            If None, uses theme default.
            **kwargs: Additional arguments for the CTkFrame.
        """
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)

        self.size = size
        self.original_color = color
        self.color = self._dull_color(color)
        self._state = "off"
        self.wear_level = 0.7
        self.flicker_enabled = False
        self.flicker_job = None
        self.led_obj = None

        if explicit_canvas_bg is not None:
            canvas_bg_color = explicit_canvas_bg
        else:
            default_bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            canvas_bg_color = self._apply_appearance_mode(default_bg_color)

        self.canvas = ctk.CTkCanvas(self, width=size, height=size,
                                    highlightthickness=0,
                                    borderwidth=0,
                                    bg=canvas_bg_color)
        self.canvas.pack(fill="both", expand=True)
        self.draw()

    def _dull_color(self, hex_color):
        """ Makes the input hex color more dull by mixing it with gray. """
        try:
            r = int(hex_color[1:3], 16)
            g = int(hex_color[3:5], 16)
            b = int(hex_color[5:7], 16)
            gray = 128; mix_factor = 0.6
            r = int(r * (1 - mix_factor) + gray * mix_factor)
            g = int(g * (1 - mix_factor) + gray * mix_factor)
            b = int(b * (1 - mix_factor) + gray * mix_factor)
            r = max(0, min(255, r)); g = max(0, min(255, g)); b = max(0, min(255, b))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#808080"

    def _darken_color(self, hex_color, factor=0.5):
        """ Darkens the input hex color by a given factor. """
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = max(0, min(255, int(r * factor))); g = max(0, min(255, int(g * factor))); b = max(0, min(255, int(b * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#333333"

    def _lighten_color(self, hex_color, factor=0.5):
        """ Lightens the input hex color by mixing it with white. """
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#cccccc"

    def draw(self):
        """ Clears the canvas and redraws the LED based on its current state. """
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")

        cx, cy = self.size / 2, self.size / 2
        casing_fill = self._apply_appearance_mode("#333333")
        casing_outline = self._apply_appearance_mode("#222222")
        ring_outline = self._apply_appearance_mode("#555555")
        off_indent_outline = self._apply_appearance_mode("#222222")

        self.canvas.create_oval(2, 2, self.size - 2, self.size - 2, fill=casing_fill, outline=casing_outline, width=2)
        self.canvas.create_oval(4, 4, self.size - 4, self.size - 4, fill="", outline=ring_outline, width=1)
        if self.wear_level > 0.3: self._add_wear_marks()

        light_size = self.size * 0.6
        x0, y0 = cx - light_size / 2, cy - light_size / 2
        x1, y1 = cx + light_size / 2, cy + light_size / 2

        if self._state == "on":
            # --- Draw 'On' State ---
            # --- FURTHER MODIFIED Glow Effect ---
            for i in range(1, 3): # Reduced layers from 3 to 2
                expand = i * 1.5 # Reduced expansion from i*2
                stipple_pattern = "gray75" if i == 1 else "gray50"
                # Use even dimmer lighter versions of the original color for outer glow
                glow_color = self._lighten_color(self.original_color, 0.10 * i) # Further reduced lightening factor
                self.canvas.create_oval(x0 - expand, y0 - expand, x1 + expand, y1 + expand,
                                        fill="", outline=glow_color, width=1.0, # Thinner glow line
                                        stipple=stipple_pattern)
            # --- End FURTHER MODIFIED Glow Effect ---

            self.led_obj = self.canvas.create_oval(x0, y0, x1, y1, fill=self.color, outline="")
            self._add_led_texture(x0, y0, x1, y1)
            spot_size = light_size * 0.25
            self.canvas.create_oval(x0 + light_size * 0.15, y0 + light_size * 0.15,
                                    x0 + light_size * 0.15 + spot_size, y0 + light_size * 0.15 + spot_size,
                                    fill="white", outline="", stipple="gray50")
            if self.flicker_enabled: self._start_flicker()
        else:
            # --- Draw 'Off' State ---
            dark_color = self._darken_color(self.color, 0.3)
            self.led_obj = self.canvas.create_oval(x0, y0, x1, y1, fill=dark_color, outline="")
            self.canvas.create_oval(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill="", outline=off_indent_outline, width=1)
            if self.flicker_job:
                self.after_cancel(self.flicker_job)
                self.flicker_job = None

    def _add_led_texture(self, x0, y0, x1, y1):
        """ Adds small specks inside the lit LED area to simulate dust/imperfections. """
        width = x1 - x0; height = y1 - y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        radius_squared = (width / 2) ** 2
        texture_color = self._apply_appearance_mode("#444444")
        for _ in range(int(5 * self.wear_level)):
            x = x0 + random.uniform(0, width); y = y0 + random.uniform(0, height)
            if (x - cx) ** 2 + (y - cy) ** 2 <= radius_squared:
                speck_size = random.uniform(0.5, 1.5)
                self.canvas.create_oval(x, y, x + speck_size, y + speck_size, fill=texture_color, outline="")

    def _add_wear_marks(self):
        """ Adds dust specks and scratches to the LED casing. """
        speck_colors = [self._apply_appearance_mode(c) for c in ["#555555", "#666666", "#777777"]]
        for _ in range(int(10 * self.wear_level)):
            x = random.uniform(3, self.size - 3); y = random.uniform(3, self.size - 3)
            speck_size = random.uniform(1, 2); color = random.choice(speck_colors)
            self.canvas.create_oval(x, y, x + speck_size, y + speck_size, fill=color, outline="")
        scratch_color = self._apply_appearance_mode("#333333")
        for _ in range(int(5 * self.wear_level)):
            x1 = random.uniform(3, self.size - 3); y1 = random.uniform(3, self.size - 3)
            length = random.uniform(2, 8); angle = random.uniform(0, math.pi * 2)
            x2 = x1 + length * math.cos(angle); y2 = y1 + length * math.sin(angle)
            x2 = max(3, min(self.size - 3, x2)); y2 = max(3, min(self.size - 3, y2))
            self.canvas.create_line(x1, y1, x2, y2, fill=scratch_color, width=0.5, dash=(2, 2))

    def _start_flicker(self):
        """ Initiates the flickering effect if the LED is 'on'. """
        if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
        if self._state != "on" or not self.flicker_enabled:
            if self.led_obj and self.canvas.winfo_exists():
                 try:
                     current_fill = self.canvas.itemcget(self.led_obj, "fill")
                     if current_fill != self.color: self.canvas.itemconfig(self.led_obj, fill=self.color)
                 except tk.TclError: pass
            return
        intensity = random.uniform(0.75, 1.0); flicker_color = self._darken_color(self.color, intensity)
        if self.led_obj and self.canvas.winfo_exists():
            try: self.canvas.itemconfig(self.led_obj, fill=flicker_color)
            except tk.TclError: pass
        base_delay = 400 if random.random() < 0.8 else 100; jitter = random.randint(0, 500); delay = base_delay + jitter
        if self.winfo_exists(): self.flicker_job = self.after(delay, self._start_flicker)
        else: self.flicker_job = None

    def set_state(self, state: str):
        """ Sets the state of the LED ('on' or 'off'). """
        new_state = state.lower()
        if new_state not in ["on", "off"]: return
        old_state = self._state
        self._state = new_state
        if old_state != self._state: self.draw()

    def get_state(self) -> str:
        """ Returns the current state ('on' or 'off') of the LED. """
        return self._state

    def toggle(self):
        """ Toggles the LED state between 'on' and 'off'. """
        self.set_state("off" if self._state == "on" else "on")

    def set_wear_level(self, level: float):
        """ Sets the wear level, affecting dust and scratches. """
        self.wear_level = max(0.0, min(1.0, level))
        self.draw()

    def enable_flicker(self, enabled: bool = True):
        """ Enables or disables the flickering effect. """
        flicker_state_changed = self.flicker_enabled != enabled
        self.flicker_enabled = enabled
        if flicker_state_changed or self._state == "on":
            if enabled and self._state == "on": self._start_flicker()
            elif not enabled:
                if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
                self.draw()

# --- NeonLight Class (Remains the same as previous version) ---
class NeonLight(ctk.CTkFrame):
    """
    A CustomTkinter widget simulating a flickering neon tube light.
    (Provided by user, not integrated into the main trading app currently)
    """
    def __init__(self, master, color="#ff00ff", width=100, height=30, explicit_canvas_bg=None, **kwargs):
        super().__init__(master, width=width, height=height, fg_color="transparent", **kwargs)
        self.width = width; self.height = height; self.original_color = color; self.color = color
        self._state = "off"; self.wear_level = 0.7; self.flicker_enabled = False
        self.flicker_job = None; self.tube_obj = None
        if explicit_canvas_bg is not None: canvas_bg_color = explicit_canvas_bg
        else:
            default_bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
            canvas_bg_color = self._apply_appearance_mode(default_bg_color)
        self.canvas = ctk.CTkCanvas(self, width=width, height=height, highlightthickness=0, borderwidth=0, bg=canvas_bg_color)
        self.canvas.pack(fill="both", expand=True)
        self.draw()
    def _darken_color(self, hex_color, factor=0.5):
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = max(0, min(255, int(r * factor))); g = max(0, min(255, int(g * factor))); b = max(0, min(255, int(b * factor)))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#333333"
    def _lighten_color(self, hex_color, factor=0.5):
        try:
            r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
            r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
            return f"#{r:02x}{g:02x}{b:02x}"
        except ValueError: return "#cccccc"
    def draw(self):
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        tube_width = self.width * 0.8; tube_height = self.height * 0.4
        cx, cy = self.width / 2, self.height / 2
        bracket_width = self.width * 0.08; bracket_height = self.height * 0.7
        bracket_fill = self._apply_appearance_mode("#555555"); bracket_outline = self._apply_appearance_mode("#333333")
        self.canvas.create_rectangle(cx - tube_width / 2 - bracket_width, cy - bracket_height / 2, cx - tube_width / 2, cy + bracket_height / 2, fill=bracket_fill, outline=bracket_outline)
        self.canvas.create_rectangle(cx + tube_width / 2, cy - bracket_height / 2, cx + tube_width / 2 + bracket_width, cy + bracket_height / 2, fill=bracket_fill, outline=bracket_outline)
        self._add_wear_marks()
        tube_left = cx - tube_width / 2; tube_right = cx + tube_width / 2; tube_top = cy - tube_height / 2; tube_bottom = cy + tube_height / 2
        cap_width = tube_height * 1.2; cap_fill = self._apply_appearance_mode("#777777"); cap_outline = self._apply_appearance_mode("#333333")
        self.canvas.create_rectangle(tube_left - cap_width, tube_top, tube_left, tube_bottom, fill=cap_fill, outline=cap_outline)
        self.canvas.create_rectangle(tube_right, tube_top, tube_right + cap_width, tube_bottom, fill=cap_fill, outline=cap_outline)
        if self._state == "on":
            for i in range(1, 5):
                expand_x = i * 2.0; expand_y = i * 1.0; glow_color = self._lighten_color(self.original_color, 0.15 * i)
                stipple_pattern = "";
                if i == 1: stipple_pattern = "gray75"
                elif i == 2: stipple_pattern = "gray50"
                elif i == 3: stipple_pattern = "gray25"
                else: stipple_pattern = "gray12"
                self.canvas.create_rectangle(tube_left - expand_x, tube_top - expand_y, tube_right + expand_x, tube_bottom + expand_y, fill="", outline=glow_color, width=1, stipple=stipple_pattern)
            self.tube_obj = self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom, fill=self.color, outline="")
            highlight_height = tube_height * 0.3; highlight_color = self._lighten_color(self.color, 0.6)
            self.canvas.create_rectangle(tube_left, tube_top + tube_height*0.1, tube_right, tube_top + tube_height*0.1 + highlight_height, fill=highlight_color, outline="", stipple="gray75")
            if self.flicker_enabled: self._start_flicker()
        else:
            dark_color = self._darken_color(self.color, 0.15)
            self.tube_obj = self.canvas.create_rectangle(tube_left, tube_top, tube_right, tube_bottom, fill=dark_color, outline=self._apply_appearance_mode("#222222"))
            reflection_color = self._apply_appearance_mode("#AAAAAA")
            self.canvas.create_rectangle(tube_left + tube_width*0.1, tube_top + tube_height*0.1, tube_right - tube_width*0.1, tube_top + tube_height * 0.4, fill=reflection_color, outline="", stipple="gray50")
            if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
    def _add_wear_marks(self):
        speck_colors = [self._apply_appearance_mode(c) for c in ["#444444", "#555555", "#666666"]]
        for _ in range(int(15 * self.wear_level)):
            x = random.uniform(0, self.width); y = random.uniform(0, self.height); speck_size = random.uniform(1, 3); color = random.choice(speck_colors)
            self.canvas.create_oval(x, y, x + speck_size, y + speck_size, fill=color, outline="")
        scratch_color = self._apply_appearance_mode("#333333")
        for _ in range(int(6 * self.wear_level)):
            x1 = random.uniform(0, self.width); y1 = random.uniform(0, self.height); length = random.uniform(3, 10); angle = random.uniform(0, math.pi*2)
            x2 = x1 + length * math.cos(angle); y2 = y1 + length * math.sin(angle); x2 = max(0, min(self.width, x2)); y2 = max(0, min(self.height, y2))
            self.canvas.create_line(x1, y1, x2, y2, fill=scratch_color, width=0.5, dash=(3, 3))
    def _start_flicker(self):
        if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
        if self._state != "on" or not self.flicker_enabled:
            if self.tube_obj and self.canvas.winfo_exists():
                 try:
                     current_fill = self.canvas.itemcget(self.tube_obj, "fill")
                     if current_fill != self.color: self.canvas.itemconfig(self.tube_obj, fill=self.color)
                 except tk.TclError: pass
            return
        flicker_type = random.choices(["minor", "major", "off", "normal"], weights=[0.6, 0.25, 0.1, 0.05], k=1)[0]
        flicker_color = self.color
        if flicker_type == "minor": intensity = random.uniform(0.75, 0.9); flicker_color = self._darken_color(self.color, intensity)
        elif flicker_type == "major": intensity = random.uniform(0.4, 0.65); flicker_color = self._darken_color(self.color, intensity)
        elif flicker_type == "off": flicker_color = self._darken_color(self.color, 0.1)
        if self.tube_obj and self.canvas.winfo_exists():
            try: self.canvas.itemconfig(self.tube_obj, fill=flicker_color)
            except tk.TclError: pass
        if flicker_type in ["major", "off"]: delay = random.randint(40, 120)
        else: base = 800 if random.random() < 0.6 else 250; jitter = random.randint(0, 600); delay = base + jitter
        if self.winfo_exists(): self.flicker_job = self.after(delay, self._start_flicker)
        else: self.flicker_job = None
    def set_state(self, state: str):
        new_state = state.lower();
        if new_state not in ["on", "off"]: return
        old_state = self._state; self._state = new_state
        if old_state != self._state: self.draw()
    def get_state(self) -> str: return self._state
    def toggle(self): self.set_state("off" if self._state == "on" else "on")
    def set_wear_level(self, level: float): self.wear_level = max(0.0, min(1.0, level)); self.draw()
    def enable_flicker(self, enabled: bool = True):
        flicker_state_changed = self.flicker_enabled != enabled; self.flicker_enabled = enabled
        if flicker_state_changed or self._state == "on":
            if enabled and self._state == "on": self._start_flicker()
            elif not enabled:
                if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
                self.draw()

# --- Example Usage (Remains the same) ---
if __name__ == "__main__":
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    app = ctk.CTk(); app.title("Vintage Indicators Demo"); app.geometry("600x450")
    title_label = ctk.CTkLabel(app, text="Vintage Indicators Demo", font=("Roboto", 20)); title_label.pack(pady=20)
    led_frame = ctk.CTkFrame(app); led_frame.pack(pady=10)
    led_label_title = ctk.CTkLabel(led_frame, text="Worn LEDs", font=("Roboto", 14)); led_label_title.pack(pady=(0, 5))
    led_indicators_frame = ctk.CTkFrame(led_frame, fg_color="transparent"); led_indicators_frame.pack()
    leds = []; led_colors = ["#ff0000", "#00ff00", "#0088ff", "#ffff00", "#ff00ff"]
    app_bg = app.cget("fg_color")
    for i, color in enumerate(led_colors):
        wear = random.uniform(0.6, 0.9)
        led = WornLED(led_indicators_frame, color=color, size=40, explicit_canvas_bg=app_bg); led.pack(side="left", padx=10)
        led.set_wear_level(wear)
        if i % 2 == 0: led.set_state("on")
        if i % 3 != 1: led.enable_flicker(True)
        leds.append(led)
    neon_frame = ctk.CTkFrame(app); neon_frame.pack(pady=20)
    neon_label_title = ctk.CTkLabel(neon_frame, text="Neon Lights", font=("Roboto", 14)); neon_label_title.pack(pady=(0, 5))
    neon_indicators_frame = ctk.CTkFrame(neon_frame, fg_color="transparent"); neon_indicators_frame.pack()
    neons = []; neon_colors = ["#ff00ff", "#00ffff", "#ff6600", "#39ff14"]
    for i, color in enumerate(neon_colors):
        neon = NeonLight(neon_indicators_frame, color=color, width=120, height=30, explicit_canvas_bg=app_bg); neon.pack(side="top", pady=8)
        neon.set_wear_level(random.uniform(0.5, 0.8))
        if i % 2 == 0: neon.set_state("on"); neon.enable_flicker(True)
        neons.append(neon)
    control_frame = ctk.CTkFrame(app); control_frame.pack(pady=10, fill="x", padx=20); control_frame.grid_columnconfigure((0, 1, 2), weight=1)
    led_control = ctk.CTkFrame(control_frame, fg_color="transparent"); led_control.grid(row=0, column=0, padx=10)
    def toggle_leds():
        for led in leds: led.toggle()
    led_toggle = ctk.CTkButton(led_control, text="Toggle LEDs", command=toggle_leds); led_toggle.pack(pady=5)
    neon_control = ctk.CTkFrame(control_frame, fg_color="transparent"); neon_control.grid(row=0, column=1, padx=10)
    def toggle_neons():
        for neon in neons: neon.toggle()
    neon_toggle = ctk.CTkButton(neon_control, text="Toggle Neons", command=toggle_neons); neon_toggle.pack(pady=5)
    flicker_control = ctk.CTkFrame(control_frame, fg_color="transparent"); flicker_control.grid(row=0, column=2, padx=10)
    flicker_var = ctk.BooleanVar(value=True)
    def toggle_all_flicker():
        enabled = flicker_var.get()
        for led in leds: led.enable_flicker(enabled)
        for neon in neons: neon.enable_flicker(enabled)
    flicker_switch = ctk.CTkSwitch(flicker_control, text="Flicker", variable=flicker_var, command=toggle_all_flicker); flicker_switch.pack(pady=5)
    toggle_all_flicker()
    app.mainloop()

