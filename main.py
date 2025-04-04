# main.py
# Entry point for the application

import customtkinter as ctk
from gui.app import App
import os
from dotenv import load_dotenv

# Load environment variables (optional, good practice for API keys)
load_dotenv()

# --- Theming ---
# Modes: "System" (standard), "Dark", "Light"
ctk.set_appearance_mode("Dark")
# Themes: "blue" (standard), "green", "dark-blue"
# We can create custom themes later, for now let's use dark-blue
# and override colors for the Miami Vice / Retro Fallout feel.
ctk.set_default_color_theme("dark-blue")

# --- Main Application ---
if __name__ == "__main__":
    # Initialize the main application window
    app = App()
    # Start the Tkinter event loop
    app.mainloop()