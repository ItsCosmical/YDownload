import os
import re
import subprocess

def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)

def apply_cosmic_rule(filepath, logger_instance=None):
    filename = os.path.basename(filepath)
    if os.path.exists(filepath) and filename[0].isdigit():
        os.remove(filepath)
        if logger_instance:
            logger_instance.debug(f"\n[COSMIC RULE] Deleted {filename} (Started with number)\n")

def play_finish_sound(play_sound_bool):
    if play_sound_bool:
        try:
            import winsound
            winsound.Beep(1000, 150)
            winsound.Beep(1500, 200)
        except Exception:
            pass

def execute_shutdown(shutdown_bool, logger_instance=None):
    if shutdown_bool:
        if logger_instance: logger_instance.info("\n[SYSTEM] Auto-Shutdown initiated. PC will turn off in 60 seconds.")
        os.system("shutdown /s /t 60")

def burn_hardsubs(video_path, logger_instance=None):
    base_name = video_path.rsplit('.', 1)[0]
    possible_srts = [f for f in os.listdir(os.path.dirname(video_path)) if f.startswith(os.path.basename(base_name)) and f.endswith('.srt')]
    
    if not possible_srts:
        if logger_instance: logger_instance.warning("[HARDSUB] No subtitles found to burn. Skipping.")
        return
        
    srt_path = os.path.join(os.path.dirname(video_path), possible_srts[0])
    temp_out = video_path.replace(".mp4", "_hardsubbed.mp4")
    
    if logger_instance: logger_instance.info("\n[HARDSUB] Burning subtitles into video. Fans might spin up, please wait...")

    escaped_srt = srt_path.replace('\\', '\\\\').replace(':', '\\:')
    cmd = ['ffmpeg', '-y', '-i', video_path, '-vf', f"subtitles='{escaped_srt}'", '-c:a', 'copy', temp_out]

    try:
        subprocess.run(cmd, creationflags=subprocess.CREATE_NO_WINDOW, check=True)
        os.replace(temp_out, video_path) 
        os.remove(srt_path) 
        if logger_instance: logger_instance.info("[HARDSUB] Subtitles successfully painted onto video!")
    except Exception as e:
        if logger_instance: logger_instance.error(f"[HARDSUB] Failed to burn subtitles: {e}")
        if os.path.exists(temp_out): os.remove(temp_out)