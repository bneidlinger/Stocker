# gui/widgets/dot_matrix.py
# Dot Matrix display widgets adapted from provided code.
# Added dynamic color support and flicker enabling.

import customtkinter as ctk
import math
import random
import tkinter as tk # For TclError

# --- Helper Functions (remain the same) ---

def darken_color(hex_color, factor=0.5):
    """Darkens a hex color string."""
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith('#'):
        return "#000000"
    try:
        r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
        r = max(0, int(r * factor)); g = max(0, int(g * factor)); b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError: return "#000000"

def lighten_color(hex_color, factor=0.5):
    """Lightens a hex color string by mixing with white."""
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith('#'):
        return "#ffffff"
    try:
        r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError: return "#ffffff"

# --- MatrixPixel Class ---
class MatrixPixel(ctk.CTkFrame):
    """Simulates a single pixel in a dot matrix display."""
    # --- Modified: Store base_color ---
    def __init__(self, master, color="#00ff00", size=8, explicit_canvas_bg="#050505", **kwargs):
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)

        self.size = size
        self.base_color = color # Store the intended 'on' color
        self.state = "off"
        self.burn_in_level = 0.0
        self.flicker_enabled = False
        self.flicker_job = None
        self.pixel_obj = None

        self._update_colors() # Calculate initial on/off colors

        self.canvas = ctk.CTkCanvas(self, width=size, height=size,
                                    highlightthickness=0, borderwidth=0,
                                    bg=explicit_canvas_bg)
        self.canvas.pack(fill="both", expand=True)
        self.after(0, self.draw)

    # --- Modified: Use self.base_color ---
    def _update_colors(self):
        """Calculates on/off colors based on base color and burn-in."""
        on_dim_factor = 1.0 - (self.burn_in_level * 0.3)
        off_bright_factor = self.burn_in_level * 0.15
        self.on_color = darken_color(self.base_color, on_dim_factor) # Use base_color
        base_off_color = darken_color(self.base_color, 0.05) # Use base_color
        self.off_color = lighten_color(base_off_color, off_bright_factor)

    # --- NEW: Method to change base color ---
    def set_base_color(self, new_color):
        """Sets a new base color for the pixel and updates."""
        if new_color != self.base_color:
            self.base_color = new_color
            self._update_colors()
            # Redraw immediately if the widget exists to reflect new on/off colors
            if self.winfo_exists():
                self.draw()

    def draw(self):
        """Draws the matrix pixel."""
        if not hasattr(self, 'canvas') or not self.canvas.winfo_exists(): return
        self.canvas.delete("all")
        inset = 1; x0, y0 = inset, inset; x1, y1 = self.size - inset, self.size - inset
        current_color = self.on_color if self.state == "on" else self.off_color
        self.pixel_obj = self.canvas.create_rectangle(x0, y0, x1, y1, fill=current_color, outline="")
        if self.state == "on":
            glow_color = lighten_color(self.on_color, 0.4)
            self.canvas.create_rectangle(x0 - 1, y0 - 1, x1 + 1, y1 + 1, fill="", outline=glow_color, width=1, stipple="gray25")
            self.canvas.lift(self.pixel_obj)
        # Manage flicker state after drawing
        if self.state == 'on' and self.flicker_enabled: self._start_flicker()
        elif self.state == 'off' and self.flicker_job:
            if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None

    def _start_flicker(self):
        """Handles pixel flickering."""
        if self.flicker_job: self.after_cancel(self.flicker_job); self.flicker_job = None
        if not self.flicker_enabled or self.state != "on" or not self.pixel_obj or not self.canvas.winfo_exists(): return
        intensity = random.uniform(0.75, 1.0)
        flicker_color = darken_color(self.on_color, intensity) # Flicker the calculated on_color
        try:
            if self.pixel_obj in self.canvas.find_all(): self.canvas.itemconfig(self.pixel_obj, fill=flicker_color)
            else: self.flicker_job = None; return
        except tk.TclError: self.flicker_job = None; return
        except Exception: self.flicker_job = None; return
        delay = random.randint(100, 600)
        if self.flicker_enabled and self.state == "on":
            try:
                if self.winfo_exists(): self.flicker_job = self.after(delay, self._start_flicker)
                else: self.flicker_job = None
            except Exception: self.flicker_job = None

    def set_state(self, state):
        """Sets the pixel state ('on' or 'off')."""
        new_state = "on" if state == "on" else "off"
        if new_state != self.state:
            self.state = new_state
            if self.winfo_exists(): self.draw()

    def toggle(self):
        """Toggles the pixel state."""
        self.set_state("off" if self.state == "on" else "on")

    def set_burn_in(self, level):
        """Sets the burn-in level (0.0 to 1.0)."""
        try:
            new_level = max(0.0, min(1.0, float(level)))
            if abs(new_level - self.burn_in_level) > 1e-6:
                self.burn_in_level = new_level
                self._update_colors()
                if self.winfo_exists(): self.draw()
        except (ValueError, TypeError): print(f"MatrixPixel: Invalid level passed to set_burn_in: {level}")

    # --- Modified: enable_flicker also redraws if turning flicker off while 'on' ---
    def enable_flicker(self, enabled=True):
        """Enables or disables flickering."""
        new_flicker_state = bool(enabled)
        if new_flicker_state != self.flicker_enabled:
            self.flicker_enabled = new_flicker_state
            if self.flicker_enabled and self.state == "on":
                self._start_flicker()
            elif not self.flicker_enabled:
                if self.flicker_job:
                    self.after_cancel(self.flicker_job)
                    self.flicker_job = None
                # If turning flicker off while pixel is on, redraw to show steady color
                if self.state == 'on' and self.winfo_exists():
                    self.draw()


# --- MatrixText Class ---
class MatrixText:
    """Helper class for creating text displays using matrix pixels."""
    # --- Modified: Store default color ---
    def __init__(self, parent, rows=7, cols=60, pixel_size=4, char_spacing=1, bg_color="#050505", default_on_color="#00ff00"):
        self.frame = ctk.CTkFrame(parent, fg_color=bg_color)
        self.pixels = []
        self.rows = rows
        self.cols = cols
        self.pixel_size = pixel_size
        self.char_spacing = char_spacing
        self.bg_color = bg_color
        self.default_on_color = default_on_color
        self.current_color = default_on_color # Track the current color for the text

        self._char_map = self._create_char_map()

        for r in range(rows):
            pixel_row = []
            row_frame = ctk.CTkFrame(self.frame, fg_color=bg_color)
            row_frame.pack(pady=0, fill="x", expand=False)
            for c in range(cols):
                burn_in = random.uniform(0.1, 0.7)
                # Pass explicit bg and default on color
                pixel = MatrixPixel(row_frame, color=self.default_on_color, size=pixel_size, explicit_canvas_bg=self.bg_color)
                pixel.pack(side="left", padx=0, pady=0)
                pixel.set_burn_in(burn_in)
                pixel_row.append(pixel)
            self.pixels.append(pixel_row)

    def _create_char_map(self): # (remains the same as previous version)
        """Creates the 5x7 character map."""
        return {
            'A': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'B': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
            'C': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,1],[0,1,1,1,0]],
            'D': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0]],
            'E': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'F': [[1,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            'G': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[1,0,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'H': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'I': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[1,1,1,1,1]],
            'J': [[0,0,1,1,1],[0,0,0,0,1],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'K': [[1,0,0,1,0],[1,0,1,0,0],[1,1,0,0,0],[1,1,0,0,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
            'L': [[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            'M': [[1,0,0,0,1],[1,1,0,1,1],[1,0,1,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'N': [[1,0,0,0,1],[1,1,0,0,1],[1,0,1,0,1],[1,0,0,1,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1]],
            'O': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'P': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0]],
            'Q': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,0,0,1,0],[0,1,1,0,1]],
            'R': [[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[1,1,1,1,0],[1,0,1,0,0],[1,0,0,1,0],[1,0,0,0,1]],
            'S': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,0],[0,1,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'T': [[1,1,1,1,1],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'U': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            'V': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0]],
            'W': [[1,0,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[1,0,1,0,1],[1,1,0,1,1],[1,1,0,1,1],[1,0,0,0,1]],
            'X': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1],[1,0,0,0,1]],
            'Y': [[1,0,0,0,1],[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            'Z': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,1]],
            '0': [[0,1,1,1,0],[1,0,0,1,1],[1,0,1,0,1],[1,1,0,0,1],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '1': [[0,0,1,0,0],[0,1,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,1,1,1,0]],
            '2': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[1,1,1,1,1]],
            '3': [[1,1,1,1,0],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,1,0],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '4': [[0,0,0,1,0],[0,0,1,1,0],[0,1,0,1,0],[1,0,0,1,0],[1,1,1,1,1],[0,0,0,1,0],[0,0,0,1,0]],
            '5': [[1,1,1,1,1],[1,0,0,0,0],[1,1,1,1,0],[0,0,0,0,1],[0,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '6': [[0,0,1,1,0],[0,1,0,0,0],[1,0,0,0,0],[1,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '7': [[1,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            '8': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,0]],
            '9': [[0,1,1,1,0],[1,0,0,0,1],[1,0,0,0,1],[0,1,1,1,1],[0,0,0,0,1],[0,0,0,1,0],[0,1,1,0,0]],
            ' ': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '>': [[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,1,0,0,0],[0,0,1,0,0],[0,0,0,1,0],[0,0,0,0,1]],
            '_': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1]],
            '.': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            ':': [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '-': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '\n':[[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
        }

    # --- Modified: display_text accepts color ---
    def display_text(self, text, color=None):
        """Displays text on the matrix, optionally setting the color."""
        self.clear()
        # Update current color, fallback to default if None
        self.current_color = color if color is not None else self.default_on_color

        char_width_total = 5 + self.char_spacing
        current_col = 0
        line = text.split('\n')[0] # Process first line only

        for char in line:
            if current_col + 5 <= self.cols:
                self.display_char(char, current_col) # display_char now uses self.current_color
                current_col += char_width_total
            else: break

    # --- Modified: display_char uses current_color and enables flicker ---
    def display_char(self, char, start_col):
        """Displays a single character pattern at the specified column."""
        default_pattern = [[1]*5]*7
        pattern = self._char_map.get(char.upper(), default_pattern)

        for r_idx, row_pattern in enumerate(pattern):
            if r_idx < self.rows:
                for c_idx, is_on in enumerate(row_pattern):
                    target_col = start_col + c_idx
                    if target_col < self.cols:
                        if r_idx < len(self.pixels) and target_col < len(self.pixels[r_idx]):
                            pixel = self.pixels[r_idx][target_col]
                            if pixel.winfo_exists():
                                # Set the base color for the pixel first
                                pixel.set_base_color(self.current_color)
                                # Set the state (this will draw with updated on/off colors)
                                pixel.set_state("on" if is_on else "off")
                                # Enable flicker only for 'on' pixels
                                pixel.enable_flicker(is_on)

    # --- Modified: clear also disables flicker ---
    def clear(self):
        """Turns off all pixels and disables their flicker."""
        for row in self.pixels:
            for pixel in row:
                 if pixel.winfo_exists():
                    pixel.enable_flicker(False) # Disable flicker first
                    pixel.set_state("off")     # Then turn off

    def get_frame(self):
        """Returns the main frame containing the pixels."""
        return self.frame

