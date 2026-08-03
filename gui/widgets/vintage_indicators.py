# gui/widgets/vintage_indicators.py
# Custom vintage-style indicator widgets: WornLED (panel LED) and NeonLight.

import customtkinter as ctk
import math
import random
import tkinter as tk


# --- Pure color helpers (no Tk required) ---

def _hex_to_rgb(hex_color):
    try:
        h = hex_color.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except (ValueError, IndexError):
        return 128, 128, 128


def _rgb_to_hex(rgb):
    r, g, b = (max(0, min(255, int(round(c)))) for c in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def _mix(c1, c2, t):
    """Linear blend between two hex colors; t=0 -> c1, t=1 -> c2."""
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    return _rgb_to_hex((r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t))


def _scale(color, f):
    r, g, b = _hex_to_rgb(color)
    return _rgb_to_hex((r * f, g * f, b * f))


class WornLED(ctk.CTkFrame):
    """
    A worn hardware-panel LED: recessed metal bezel, domed epoxy die with a
    hot center and a specular glint, and a light pool that spills onto the
    panel around the bezel. Brightness is animated -- capacitor warm-up when
    switched on, ember afterglow when switched off, and electrical flicker
    that modulates the die and the halo together. Every instance gets a
    frozen wear pattern and slightly different electrical characteristics,
    like a hand-stuffed 1990 board.

    Public API (unchanged): set_state, get_state, toggle, set_wear_level,
    enable_flicker, draw.
    """

    FRAME_MS = 30  # animation tick during brightness ramps

    def __init__(self, master, color="#ff0000", size=30, explicit_canvas_bg=None, **kwargs):
        """
        Args:
            master: The parent widget.
            color (str): The base hex color for the LED when 'on'.
            size (int): The bezel diameter. The widget itself is slightly
                larger to leave room for the glow to spill onto the panel.
            explicit_canvas_bg (str | None): Explicit color for the canvas
                background (the "panel"). If None, uses the theme default.
            **kwargs: Additional arguments for the CTkFrame.
        """
        self._margin = max(4, round(size * 0.30))
        canvas_px = size + 2 * self._margin
        super().__init__(master, width=canvas_px, height=canvas_px,
                         fg_color="transparent", **kwargs)

        self.size = size
        self.original_color = color
        self._state = "off"
        self.wear_level = 0.7
        self.flicker_enabled = False

        # Per-instance electrical personality and frozen wear pattern.
        self._rng = random.Random(random.getrandbits(32))
        rng = self._rng
        self._base_brightness = rng.uniform(0.90, 1.0)
        self._flicker_depth = rng.uniform(0.55, 1.10)
        self._attack_ms = rng.uniform(45, 100)   # warm-up ramp time
        self._decay_tau = rng.uniform(70, 130)   # afterglow time constant
        self._die_dx = rng.uniform(-0.05, 0.05) * size  # die sits a bit crooked
        self._die_dy = rng.uniform(-0.05, 0.05) * size
        self._glint_jitter = rng.uniform(-0.08, 0.08)
        self._wear_seed = rng.getrandbits(32)

        if explicit_canvas_bg is not None:
            bg_pref = explicit_canvas_bg
        else:
            bg_pref = ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        canvas_bg = self._apply_appearance_mode(bg_pref)

        self.canvas = ctk.CTkCanvas(self, width=canvas_px, height=canvas_px,
                                    highlightthickness=0,
                                    borderwidth=0,
                                    bg=canvas_bg)
        self.canvas.pack(fill="both", expand=True)
        self._panel_bg = self._resolve_color(canvas_bg)

        self._b = 0.0        # current brightness 0..1
        self._noise = 1.0    # flicker multiplier on top of base brightness
        self._anim_job = None

        self.draw()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _resolve_color(self, color):
        """Return a '#rrggbb' version of any Tk color name."""
        try:
            r, g, b = self.winfo_rgb(color)
            return f"#{r // 257:02x}{g // 257:02x}{b // 257:02x}"
        except tk.TclError:
            return "#1a1a2e"

    def draw(self):
        """Full rebuild of the canvas items. State changes animate instead."""
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            return
        c = self.canvas
        c.delete("all")

        S = self.size
        C = S + 2 * self._margin
        cx = cy = C / 2
        bezel_r = S / 2 - 1
        well_r = S * 0.34
        die_r = S * 0.28
        dcx, dcy = cx + self._die_dx, cy + self._die_dy
        col = self.original_color
        bg = self._panel_bg

        # Palette shared by _render(). "epoxy" colors are the unlit tinted
        # plastic; "lit" colors are the powered die from rim to hot core.
        self._pal = {
            "glow": _mix(col, "#ffffff", 0.30),
            "epoxy_rim": _mix(col, "#0d0d10", 0.85),
            "epoxy_mid": _mix(col, "#141417", 0.80),
            "epoxy_core": _mix(col, "#1b1b1f", 0.74),
            "lit_rim": _scale(col, 0.62),
            "lit_mid": col,
            "lit_core": _mix(col, "#ffffff", 0.55),
            "glint_amb": _mix(_mix(col, "#1b1b1f", 0.74), "#a8b0ba", 0.40),
            "glint_hot": _mix(col, "#ffffff", 0.85),
            "lip_off": "#26262c",
            "lip_on": _mix(col, "#ffffff", 0.28),
            "well_lit": _scale(col, 0.30),
        }

        # Light pool on the panel around the bezel. Filled rings blended
        # toward the actual panel color; drawn first so the bezel sits on
        # top and only the spill outside it shows. The outermost ring is
        # exactly the panel color, so the halo has no visible edge.
        self._halo_items = []
        n_halo = 8
        outer_r = C / 2 - 0.5
        inner_r = bezel_r - 1
        for i in range(n_halo):
            f = i / (n_halo - 1)          # 0 = canvas edge .. 1 = bezel edge
            r = outer_r - f * (outer_r - inner_r)
            strength = 0.42 * (f ** 1.8)
            item = c.create_oval(cx - r, cy - r, cx + r, cy + r,
                                 fill=bg, outline="")
            self._halo_items.append((item, strength))

        # Machined bezel with the room light coming from the upper left.
        c.create_oval(cx - bezel_r, cy - bezel_r, cx + bezel_r, cy + bezel_r,
                      fill="#2c2c33", outline="#101014", width=1)
        arc_r = bezel_r - 0.5
        c.create_arc(cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                     start=55, extent=150, style="arc",
                     outline="#5a5a64", width=1)
        c.create_arc(cx - arc_r, cy - arc_r, cx + arc_r, cy + arc_r,
                     start=235, extent=150, style="arc",
                     outline="#0a0a0d", width=1)
        step_r = (bezel_r + well_r) / 2
        c.create_oval(cx - step_r, cy - step_r, cx + step_r, cy + step_r,
                      fill="", outline="#3a3a41", width=1)

        wear_rng = random.Random(self._wear_seed)
        self._add_wear_marks(c, cx, cy, well_r, bezel_r, wear_rng)

        # Recessed well the die sits in. Its cavity picks up bounced light
        # when the die is lit, and the lip catches a faint edge of it.
        self._well_item = c.create_oval(cx - well_r, cy - well_r,
                                        cx + well_r, cy + well_r,
                                        fill="#08080b", outline="#000000",
                                        width=1)
        self._lip_item = c.create_oval(cx - well_r, cy - well_r,
                                       cx + well_r, cy + well_r,
                                       fill="", outline=self._pal["lip_off"],
                                       width=1)

        # Domed die: rim -> mid -> hot core fakes a radial gradient.
        mid_r = die_r * 0.70
        core_r = die_r * 0.42
        self._die_rim = c.create_oval(dcx - die_r, dcy - die_r,
                                      dcx + die_r, dcy + die_r,
                                      fill=self._pal["epoxy_rim"], outline="")
        self._die_mid = c.create_oval(dcx - mid_r, dcy - mid_r,
                                      dcx + mid_r, dcy + mid_r,
                                      fill=self._pal["epoxy_mid"], outline="")
        self._die_core = c.create_oval(dcx - core_r, dcy - core_r,
                                       dcx + core_r, dcy + core_r,
                                       fill=self._pal["epoxy_core"], outline="")

        # Dust settled on the dome -- silhouettes when lit. Scaled to the
        # die so small LEDs get a fleck, not a pupil.
        n_dust = int(round((1 + 2 * self.wear_level) * die_r / 12))
        for _ in range(n_dust):
            ang = wear_rng.uniform(0, math.tau)
            rad = wear_rng.uniform(die_r * 0.25, die_r * 0.8)
            x = dcx + rad * math.cos(ang)
            y = dcy + rad * math.sin(ang)
            s = wear_rng.uniform(0.09, 0.16) * die_r
            c.create_oval(x, y, x + s, y + s, fill="#101014", outline="")

        # Specular glint: faint room-light reflection when off, hot when on.
        gx = dcx + die_r * (-0.38 + self._glint_jitter)
        gy = dcy + die_r * (-0.42 + self._glint_jitter)
        gw = die_r * 0.55
        gh = die_r * 0.40
        self._glint = c.create_oval(gx - gw / 2, gy - gh / 2,
                                    gx + gw / 2, gy + gh / 2,
                                    fill=self._pal["glint_amb"], outline="")

        self._render()
        if self._state == "on" or self._b > 0:
            self._kick()

    def _add_wear_marks(self, c, cx, cy, well_r, bezel_r, rng):
        """Dust and micro-scratches on the bezel ring, fixed per instance."""
        for _ in range(int(9 * self.wear_level)):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(well_r + 1.5, max(well_r + 1.5, bezel_r - 1.0))
            x = cx + rad * math.cos(ang)
            y = cy + rad * math.sin(ang)
            s = rng.uniform(0.5, 1.4)
            color = rng.choice(("#4a4a52", "#3c3c44", "#22222a", "#565660"))
            c.create_oval(x, y, x + s, y + s, fill=color, outline="")
        for _ in range(int(4 * self.wear_level)):
            ang = rng.uniform(0, math.tau)
            rad = rng.uniform(well_r + 2.0, max(well_r + 2.0, bezel_r - 1.5))
            x1 = cx + rad * math.cos(ang)
            y1 = cy + rad * math.sin(ang)
            length = rng.uniform(2.0, 5.0)
            a2 = ang + math.pi / 2 + rng.uniform(-0.9, 0.9)
            x2 = x1 + length * math.cos(a2)
            y2 = y1 + length * math.sin(a2)
            color = "#15151a" if rng.random() < 0.6 else "#4d4d55"
            c.create_line(x1, y1, x2, y2, fill=color, width=1)

    def _render(self):
        """Repaint the dynamic layers for the current brightness."""
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists():
            return
        b = self._b
        die_b = b ** 0.75    # the die lights before the bloom develops,
        halo_b = b ** 1.60   # so a cooling ember glows without a halo
        p = self._pal
        cfg = self.canvas.itemconfig
        try:
            for item, strength in self._halo_items:
                cfg(item, fill=_mix(self._panel_bg, p["glow"], strength * halo_b))
            cfg(self._well_item, fill=_mix("#08080b", p["well_lit"], 0.55 * die_b))
            cfg(self._lip_item, outline=_mix(p["lip_off"], p["lip_on"], 0.45 * die_b))
            cfg(self._die_rim, fill=_mix(p["epoxy_rim"], p["lit_rim"], die_b))
            cfg(self._die_mid, fill=_mix(p["epoxy_mid"], p["lit_mid"], die_b))
            cfg(self._die_core, fill=_mix(p["epoxy_core"], p["lit_core"], die_b))
            cfg(self._glint, fill=_mix(p["glint_amb"], p["glint_hot"], die_b))
        except tk.TclError:
            pass

    # ------------------------------------------------------------------
    # Brightness animation engine
    # ------------------------------------------------------------------

    def _kick(self):
        """Start the animation loop if it is parked."""
        if self._anim_job is None:
            self._schedule(1)

    def _schedule(self, delay_ms):
        try:
            self._anim_job = self.after(max(1, int(delay_ms)), self._tick)
        except tk.TclError:
            self._anim_job = None

    def _cancel_anim(self):
        if self._anim_job is not None:
            try:
                self.after_cancel(self._anim_job)
            except (tk.TclError, ValueError):
                pass
            self._anim_job = None

    def _tick(self):
        self._anim_job = None
        if not self.winfo_exists() or not self.canvas.winfo_exists():
            return
        delay = self.FRAME_MS
        if self._state == "on":
            goal = self._base_brightness * self._noise
            if self._b < goal - 0.01:
                # Warming up: old caps charge fast, but not instantly.
                self._b = min(goal, self._b + self.FRAME_MS / self._attack_ms)
            else:
                # Electrical dips are instant.
                self._b = goal
                if self.flicker_enabled:
                    delay = self._next_flicker_event()
                else:
                    self._noise = 1.0
                    if abs(self._b - self._base_brightness) < 0.005:
                        self._render()
                        return  # steady: park the loop
        else:
            # Ember afterglow: the die cools instead of snapping dark.
            self._b *= math.exp(-self.FRAME_MS / self._decay_tau)
            if self._b < 0.02:
                self._b = 0.0
                self._render()
                return
        self._render()
        self._schedule(delay)

    def _next_flicker_event(self):
        """Pick the next flicker excursion; returns the hold time in ms."""
        rng = self._rng
        d = self._flicker_depth
        r = rng.random()
        if r < 0.10:
            self._noise = 1.0                                   # calm stretch
            return rng.uniform(400, 900)
        if r < 0.72:
            self._noise = 1.0 - rng.uniform(0.0, 0.07) * d      # mains shimmer
            return rng.uniform(90, 220)
        if r < 0.90:
            self._noise = 1.0 - rng.uniform(0.07, 0.22) * d     # sag
            return rng.uniform(60, 140)
        if r < 0.975:
            self._noise = 1.0 - rng.uniform(0.25, 0.45) * d     # deep sag
            return rng.uniform(40, 90)
        self._noise = rng.uniform(0.05, 0.16)                   # contact dropout
        return rng.uniform(25, 60)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_state(self, state: str):
        """ Sets the state of the LED ('on' or 'off'). """
        new_state = str(state).lower()
        if new_state not in ["on", "off"]:
            return
        if new_state == self._state:
            return
        self._state = new_state
        self._noise = 1.0
        self._cancel_anim()
        self._schedule(1)

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
        enabled = bool(enabled)
        if enabled == self.flicker_enabled:
            if enabled and self._state == "on":
                self._kick()
            return
        self.flicker_enabled = enabled
        if not enabled:
            self._noise = 1.0
        self._cancel_anim()
        self._schedule(1)

    def destroy(self):
        self._cancel_anim()
        super().destroy()


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


# --- Example Usage ---
if __name__ == "__main__":
    ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    PANEL_BG = "#1a1a2e"  # match the app's panel color
    app = ctk.CTk(fg_color=PANEL_BG); app.title("Vintage Indicators Demo"); app.geometry("620x480")
    title_label = ctk.CTkLabel(app, text="Vintage Indicators Demo", font=("Roboto", 20)); title_label.pack(pady=20)
    led_frame = ctk.CTkFrame(app, fg_color=PANEL_BG); led_frame.pack(pady=10)
    led_label_title = ctk.CTkLabel(led_frame, text="Worn LEDs", font=("Roboto", 14)); led_label_title.pack(pady=(0, 5))
    led_indicators_frame = ctk.CTkFrame(led_frame, fg_color="transparent"); led_indicators_frame.pack()
    leds = []; led_colors = ["#E6455E", "#2FC41F", "#E1E100", "#00C2C2", "#7D26CD"]
    for i, color in enumerate(led_colors):
        wear = random.uniform(0.6, 0.9)
        led = WornLED(led_indicators_frame, color=color, size=40, explicit_canvas_bg=PANEL_BG); led.pack(side="left", padx=10)
        led.set_wear_level(wear)
        if i % 2 == 0: led.set_state("on")
        if i % 3 != 1: led.enable_flicker(True)
        leds.append(led)
    neon_frame = ctk.CTkFrame(app); neon_frame.pack(pady=20)
    neon_label_title = ctk.CTkLabel(neon_frame, text="Neon Lights", font=("Roboto", 14)); neon_label_title.pack(pady=(0, 5))
    neon_indicators_frame = ctk.CTkFrame(neon_frame, fg_color="transparent"); neon_indicators_frame.pack()
    neons = []; neon_colors = ["#ff00ff", "#00ffff", "#ff6600", "#39ff14"]
    for i, color in enumerate(neon_colors):
        neon = NeonLight(neon_indicators_frame, color=color, width=120, height=30); neon.pack(side="top", pady=8)
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
