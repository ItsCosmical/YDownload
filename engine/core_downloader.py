import yt_dlp
import os
import threading
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
            raise Exception("Download manually aborted by user.")

        if d['status'] == 'downloading':
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 1)
            percent = downloaded / total if total else 0
            
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            
            self.progress_callback(percent)
            self.status_callback(f"Streaming: {d.get('_percent_str', '0%')} | Speed: {speed} | ETA: {eta}")

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
            'writethumbnail': self.config.get("embed_thumbnail", True),
            'writedescription': self.config.get("write_description", False),
            'keepvideo': self.config.get("keep_video", False),
            'postprocessors': [],
            'noplaylist': False 
        }

        if self.config.get("auto_retry", True):
            ydl_opts['retries'] = 5
            ydl_opts['fragment_retries'] = 5

        try:
            p_start = self.config.get("playlist_start", "1")
            if p_start.isdigit(): ydl_opts['playliststart'] = int(p_start)
            p_end = self.config.get("playlist_end", "")
            if p_end.isdigit(): ydl_opts['playlistend'] = int(p_end)
        except ValueError:
            pass

        speed = self.config.get("speed_limit", "Unlimited")
        speed_map = {"10 MB/s": 10000000, "5 MB/s": 5000000, "1 MB/s": 1000000, "500 KB/s": 500000}
        if speed in speed_map: ydl_opts['ratelimit'] = speed_map[speed]

        size = self.config.get("max_filesize", "Unlimited")
        if size != "Unlimited": ydl_opts['max_filesize'] = size

        if self.config.get("force_ipv4", False):
            ydl_opts['source_address'] = '0.0.0.0'

        browser = self.config.get("browser_cookie", "None")
        if browser != "None":
            ydl_opts['cookiesfrombrowser'] = (browser.lower(), )

        if self.config.get("sponsorblock", False):
            ydl_opts['postprocessors'].append({
                'key': 'SponsorBlock',
                'categories': ['sponsor', 'intro', 'outro', 'interaction', 'selfpromo']
            })

        if self.config.get("download_subs", False) or self.config.get("burn_subs", False):
            ydl_opts['writesubtitles'] = True
            ydl_opts['subtitleslangs'] = ['en', 'all'] 
            ydl_opts['postprocessors'].append({'key': 'FFmpegSubtitlesConvertor', 'format': 'srt'})
            if not self.config.get("burn_subs", False):
                ydl_opts['postprocessors'].append({'key': 'FFmpegEmbedSubtitle'})

        format_choice = self.config.get("format_choice", "Best Video (MP4)")
        if "Audio Only" in format_choice:
            ydl_opts['format'] = 'bestaudio/best'
            codec = 'mp3'
            if 'WAV' in format_choice: codec = 'wav'
            elif 'FLAC' in format_choice: codec = 'flac'
            
            ydl_opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
                'preferredquality': '192',
            })
            
            if self.config.get("normalize_audio", False):
                ydl_opts['postprocessors'].append({
                    'key': 'Exec',
                    'exec_cmd': "ffmpeg -i {} -af loudnorm=I=-16:TP=-1.5:LRA=11 temp.wav && move /Y temp.wav {}"
                })
        else:
            q_map = {
                "4K (2160p)": "bestvideo[height<=2160]+bestaudio/best",
                "1440p": "bestvideo[height<=1440]+bestaudio/best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best",
                "720p": "bestvideo[height<=720]+bestaudio/best",
                "Best Available": "bestvideo+bestaudio/best"
            }
            ydl_opts['format'] = q_map.get(self.config.get("quality_choice", "Best Available"), "best")
            ydl_opts['postprocessors'].append({'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'})

        if self.config.get("embed_thumbnail", True):
            ydl_opts['postprocessors'].append({'key': 'EmbedThumbnail'})
        if self.config.get("embed_metadata", True):
            ydl_opts['postprocessors'].append({'key': 'FFmpegMetadata'})

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                for target_url in urls:
                    if self.is_cancelled: break
                    self.logger.debug(f"\n[SYSTEM] Connecting to target: {target_url}\n")
                    
                    info = ydl.extract_info(target_url, download=True)
                    
                    videos = info.get('entries', [info])
                    for video in videos:
                        if not video: continue
                        
                        ext = 'mp4'
                        if "Audio Only" in format_choice:
                            if 'WAV' in format_choice: ext = 'wav'
                            elif 'FLAC' in format_choice: ext = 'flac'
                            else: ext = 'mp3'

                        raw_filename = f"{video.get('title', 'video')}.{ext}"
                        safe_filename = clean_filename(raw_filename)
                        full_path = os.path.join(out_path, safe_filename)
                        
                        # Apply rule only if toggled
                        if self.config.get("enable_cleanup", True):
                            apply_cosmic_rule(full_path, self.logger)
                        
                        if self.config.get("burn_subs", False) and ext == 'mp4':
                            burn_hardsubs(full_path, self.logger)

            if not self.is_cancelled:
                self.status_callback("SUCCESS: All operations completed.")
                play_finish_sound(self.config.get("play_sound", True))
                execute_shutdown(self.config.get("auto_shutdown", False), self.logger)
                
        except Exception as e:
            msg = "PROCESS ABORTED." if self.is_cancelled else f"CRITICAL ERROR: {e}"
            self.status_callback(msg)
        finally:
            self.finish_callback()