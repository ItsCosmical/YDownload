import os

def clean_filename(filename):
    # Basic sanitization for Windows paths
    for char in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        filename = filename.replace(char, '_')
    return filename

def apply_cosmic_rule(path, logger):
    # Add logic here for specific file naming rules you established
    pass

def play_finish_sound(enabled):
    if enabled:
        # Simple beep or sound trigger
        print("\a") 

def burn_hardsubs(path, logger):
    # Logic for FFmpeg burning subs
    pass

def execute_shutdown(enabled, logger):
    if enabled:
        os.system("shutdown /s /t 1")
