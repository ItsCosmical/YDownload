import yt_dlp
import os
import threading
import time
from utils.post_process import clean_filename, apply_cosmic_rule, play_finish_sound, burn_hardsubs, execute_shutdown

class CoreDownloader:
    def __init__(self, config, logger, progress_callback, status_callback, finish_callback):
        self.config = config
        self.logger = logger
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.finish_callback = finish_callback
        self.is_cancelled = False

    def cancel(self):
        self.is_cancelled = True

    def progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download manually aborted.")
        if d['status'] == 'downloading':
            self.progress_callback(d.get('_percent_str', 0))
            self.status_callback(f"Streaming: {d.get('_percent_str', '0%')} | ETA: {d.get('_eta_str', 'N/A')}")

    def start(self, urls):
        threading.Thread(target=self._run_engine, args=(urls,), daemon=True).start()

    def _run_engine(self, urls):
        out_path = self.config.get("output_path", os.getcwd())
        template = self.config.get("custom_template", "%(title)s.%(ext)s")
        if not template.strip(): template = "%(title)s.%(ext)s"
        
        ydl_opts = {
            'outtmpl': f"{out_path}/{template}",
            'progress_hooks': [self.progress_hook],
            'logger': self.logger,
            'overwrites': self.config.get("allow_overwrite", False),
            'noplaylist': False,
            'retries': float('inf'),
            'fragment_retries': float('inf'),
            'file_access_retries': float('inf'),
            'no_continue': True 
        }

        # Format Selection
        format_choice = self.config.get("format_choice", "Best Video (MP4)")
        if "Audio Only" in format_choice:
            ydl_opts['format'] = 'bestaudio/best'
            codec = 'mp3'
            if 'WAV' in format_choice: codec = 'wav'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': codec, 'preferredquality': '192'}]
        else:
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
            ydl_opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for target_url in urls:
                    if self.is_cancelled: break
                    
                    # Pre-download filter
                    info = ydl.extract_info(target_url, download=False)
                    title = info.get('title', '')
                    if self.config.get("enable_cleanup", True) and title and title[0].isdigit():
                        self.logger.debug(f"\n[COSMIC RULE] Skipping '{title}'\n")
                        continue

                    # Recovery Loop for I/O Errors
                    max_attempts = 1000
                    for attempt in range(max_attempts):
                        try:
                            ydl.download([target_url])
                            break 
                        except Exception as e:
                            self.logger.debug(f"\n[RECOVERY] I/O Error (Attempt {attempt+1}/{max_attempts}): {e}")
                            time.sleep(5)
                            if attempt == max_attempts - 1: raise e

            self.status_callback("SUCCESS: Process finished.")
            play_finish_sound(True)
        except Exception as e:
            self.status_callback(f"CRITICAL ERROR: {e}")
        finally:
            self.finish_callback()
