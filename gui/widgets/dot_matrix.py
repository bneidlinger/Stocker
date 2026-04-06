# gui/widgets/dot_matrix.py
# Dot Matrix display widgets adapted from provided code.
# Added dynamic color support and flicker enabling.
# Fixed blank display issue.

import customtkinter as ctk
import math
import random
import tkinter as tk # For TclError

# --- Helper Functions ---

def darken_color(hex_color, factor=0.5):
    """Darkens a hex color string."""
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith('#'):
        # print(f"Warning: darken_color received invalid input: {hex_color}")
        return "#000000" # Fallback black
    try:
        r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
        r = max(0, int(r * factor)); g = max(0, int(g * factor)); b = max(0, int(b * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        # print(f"Warning: darken_color failed for: {hex_color}")
        return "#000000"

def lighten_color(hex_color, factor=0.5):
    """Lightens a hex color string by mixing with white."""
    if not isinstance(hex_color, str) or len(hex_color) != 7 or not hex_color.startswith('#'):
        # print(f"Warning: lighten_color received invalid input: {hex_color}")
        return "#ffffff" # Fallback white
    try:
        r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
        r = min(255, int(r + (255 - r) * factor)); g = min(255, int(g + (255 - g) * factor)); b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    except ValueError:
        # print(f"Warning: lighten_color failed for: {hex_color}")
        return "#ffffff"

# --- MatrixPixel Class ---
class MatrixPixel(ctk.CTkFrame):
    """Simulates a single pixel in a dot matrix display."""
    def __init__(self, master, color="#00ff00", size=8, explicit_canvas_bg="#050505", **kwargs):
        super().__init__(master, width=size, height=size, fg_color="transparent", **kwargs)

        self.size = size
        self.base_color = color # Store the intended 'on' color (should be hex)
        self.state = "off"
        self.burn_in_level = 0.0
        self.flicker_enabled = False
        self.flicker_job = None
        self.pixel_obj = None
        self.on_color = "#000000" # Initialize calculated colors
        # Store explicit background, defaulting if None
        self.explicit_canvas_bg = explicit_canvas_bg if explicit_canvas_bg else "#050505"
        self.off_color = self.explicit_canvas_bg # Off color should match background initially

        # Calculate initial on/off colors based on potential burn-in
        self._update_colors()

        self.canvas = ctk.CTkCanvas(self, width=size, height=size,
                                      highlightthickness=0, borderwidth=0,
                                      bg=self.explicit_canvas_bg) # Use stored background
        self.canvas.pack(fill="both", expand=True)
        self.after(10, self.draw) # Defer first draw slightly

    def _update_colors(self):
        """Calculates on/off colors based on base color and burn-in."""
        # Calculate 'on' color based on base_color and burn-in
        on_dim_factor = 1.0 - (self.burn_in_level * 0.3)
        self.on_color = darken_color(self.base_color, on_dim_factor)

        # Calculate 'off' color - should match the background
        # Apply burn-in effect by slightly lightening the background
        off_bright_factor = self.burn_in_level * 0.10 # Less brightening for off state
        self.off_color = lighten_color(self.explicit_canvas_bg, off_bright_factor)


    def set_base_color(self, new_color):
        """Sets a new base color (HEX) for the pixel and updates."""
        # Basic validation for hex color
        if not isinstance(new_color, str) or len(new_color) != 7 or not new_color.startswith('#'):
             # print(f"Warning: Invalid hex color passed to set_base_color: {new_color}")
             new_color = "#ff00ff" # Fallback to magenta if invalid

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
        inset = 1; # Adjust inset if needed
        x0, y0 = inset, inset;
        x1, y1 = self.size - inset, self.size - inset

        if self.state == "on":
            current_color = self.on_color # Use calculated on color
            self.pixel_obj = self.canvas.create_rectangle(x0, y0, x1, y1, fill=current_color, outline="")
            # Add glow effect only if pixel is meant to be bright (optional)
            # if self.burn_in_level < 0.8: # Example: Less glow for heavily burnt-in pixels
            #     glow_color = lighten_color(self.on_color, 0.4)
            #     self.canvas.create_rectangle(x0 - 1, y0 - 1, x1 + 1, y1 + 1, fill="", outline=glow_color, width=1, stipple="gray25")
            #     self.canvas.lift(self.pixel_obj) # Ensure pixel is above glow
        else:
            # --- FIX: Use calculated off_color (background + burn-in) ---
            current_color = self.off_color
            # Draw the rectangle filled with the calculated off color
            self.pixel_obj = self.canvas.create_rectangle(x0, y0, x1, y1, fill=current_color, outline="")
            # --- END FIX ---

        # Manage flicker state after drawing
        if self.state == 'on' and self.flicker_enabled:
            self._start_flicker()
        elif self.state == 'off' and self.flicker_job:
            # Stop flicker if state is off
            if self.flicker_job:
                try: self.after_cancel(self.flicker_job)
                except tk.TclError: pass
                self.flicker_job = None

    def _start_flicker(self):
        """Handles pixel flickering."""
        if self.flicker_job:
            try: self.after_cancel(self.flicker_job)
            except tk.TclError: pass
            self.flicker_job = None
        if not self.flicker_enabled or self.state != "on" or not self.winfo_exists(): return

        intensity = random.uniform(0.75, 1.0)
        # Flicker the calculated on_color
        flicker_color = darken_color(self.on_color, intensity)

        try:
            if self.pixel_obj and self.canvas.winfo_exists() and self.pixel_obj in self.canvas.find_all():
                 self.canvas.itemconfig(self.pixel_obj, fill=flicker_color)
            else:
                 self.flicker_job = None; return # Stop if object invalid
        except tk.TclError:
            self.flicker_job = None; return # Stop if error

        delay = random.randint(100, 600)
        if self.flicker_enabled and self.state == "on" and self.winfo_exists():
            self.flicker_job = self.after(delay, self._start_flicker)
        else:
             self.flicker_job = None

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
                self._update_colors() # Recalculate on/off colors
                if self.winfo_exists(): self.draw()
        except (ValueError, TypeError):
            print(f"MatrixPixel: Invalid level passed to set_burn_in: {level}")

    def enable_flicker(self, enabled=True):
        """Enables or disables flickering."""
        new_flicker_state = bool(enabled)
        if new_flicker_state != self.flicker_enabled:
            self.flicker_enabled = new_flicker_state
            if self.flicker_enabled and self.state == "on":
                 # If enabling and 'on', draw solid first then schedule flicker
                 if self.winfo_exists():
                      self.draw()
                      self.after(10, self._start_flicker)
            elif not self.flicker_enabled:
                # If disabling, cancel job and redraw solid color if 'on'
                if self.flicker_job:
                    try: self.after_cancel(self.flicker_job)
                    except tk.TclError: pass
                    self.flicker_job = None
                if self.state == 'on' and self.winfo_exists():
                    self.draw()


# --- MatrixText Class ---
class MatrixText:
    """Helper class for creating text displays using matrix pixels."""
    def __init__(self, parent, rows=7, cols=60, pixel_size=4, char_spacing=1, bg_color="#050505", default_on_color="#00ff00"):
        self.frame = ctk.CTkFrame(parent, fg_color=bg_color)
        self.pixels = [] # 2D array [row][col] of MatrixPixel widgets
        self.rows = rows
        self.cols = cols # Total pixel columns
        self.pixel_size = pixel_size
        self.char_spacing = char_spacing
        self.bg_color = bg_color
        self.default_on_color = default_on_color
        self.current_color = default_on_color # Track the current color for the text

        self._char_map = self._create_char_map()

        for r in range(rows):
            pixel_row = []
            row_frame = ctk.CTkFrame(self.frame, fg_color=bg_color)
            # Reduce padding between rows
            row_frame.pack(pady=0, fill="x", expand=False)
            for c in range(cols):
                # Apply random burn-in for vintage effect
                burn_in = random.uniform(0.1, 0.7)
                # Pass explicit bg and default on color
                pixel = MatrixPixel(row_frame, color=self.default_on_color, size=pixel_size, explicit_canvas_bg=self.bg_color)
                # Reduce padding between pixels
                pixel.pack(side="left", padx=0, pady=0)
                pixel.set_burn_in(burn_in)
                pixel_row.append(pixel)
            self.pixels.append(pixel_row)

    def _create_char_map(self): # (remains the same as previous version)
        """Creates the 5x7 character map."""
        # --- (Character map dictionary omitted for brevity - keep as before) ---
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
            '.': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,1,0,0]],
            ':': [[0,0,0,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '-': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]],
            '_': [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[1,1,1,1,1]],
            '?': [[0,1,1,1,0],[1,0,0,0,1],[0,0,0,0,1],[0,0,0,1,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],
            '!': [[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,1,0,0],[0,0,0,0,0],[0,0,1,0,0]],
        }

    def display_text(self, text, color=None):
        """
        Displays text on the matrix, using the provided HEX color.

        Args:
            text (str): The text string to display.
            color (str | None): The HEX color code (e.g., '#FF0000') for the text.
                                If None, uses default_on_color.
        """
        # self.clear() # Clear is handled separately now for blank state
        # Update current color, fallback to default if None or invalid
        hex_color = color if (color and isinstance(color, str) and color.startswith('#')) else self.default_on_color
        self.current_color = hex_color

        char_width_total = 5 + self.char_spacing
        current_col = 0
        line = text.split('\n')[0] # Process first line only

        # Turn off all pixels initially before drawing new text
        for r_idx in range(self.rows):
             for c_idx in range(self.cols):
                 if r_idx < len(self.pixels) and c_idx < len(self.pixels[r_idx]):
                      pixel = self.pixels[r_idx][c_idx]
                      if pixel.winfo_exists():
                           pixel.set_state("off")
                           pixel.enable_flicker(False) # Ensure flicker is off for off pixels

        # Draw the characters
        for char in line:
            if current_col + 5 <= self.cols:
                self.display_char(char, current_col) # display_char uses self.current_color
                current_col += char_width_total
            else: break # Stop if text exceeds display width


    def display_char(self, char, start_col):
        """Displays a single character pattern at the specified column using current color."""
        default_pattern = [[1]*5]*7 # Solid block for unknown chars
        pattern = self._char_map.get(char.upper(), default_pattern)

        for r_idx, row_pattern in enumerate(pattern):
            if r_idx < self.rows:
                for c_idx, is_on in enumerate(row_pattern):
                    target_col = start_col + c_idx
                    if target_col < self.cols:
                        if r_idx < len(self.pixels) and target_col < len(self.pixels[r_idx]):
                            pixel = self.pixels[r_idx][target_col]
                            if pixel.winfo_exists():
                                # Set the base color for the pixel first (should be hex)
                                pixel.set_base_color(self.current_color)
                                # Set the state (this will draw with updated on/off colors)
                                pixel.set_state("on" if is_on else "off")
                                # Enable flicker only for 'on' pixels
                                pixel.enable_flicker(is_on)


    def clear(self):
        """Turns off all pixels and disables their flicker, making the display blank."""
        # print("DEBUG: MatrixText clear called") # Debug
        for row in self.pixels:
            for pixel in row:
                if pixel.winfo_exists():
                    pixel.enable_flicker(False) # Disable flicker first
                    pixel.set_state("off")      # Then turn off (draws background color)

    def get_frame(self):
        """Returns the main frame containing the pixels."""
        return self.frame