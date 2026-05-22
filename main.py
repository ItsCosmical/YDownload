import customtkinter as ctk
from gui.main_window import MainWindow

def run_app():
    # Initialize the core framework
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Launch the application
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    try:
        print("Initializing YDownload Engine...")
        run_app()
    except Exception as e:
        print("\n--- FATAL APPLICATION CRASH ---")
        print(f"Error: {e}")
        input("Press Enter to exit...")