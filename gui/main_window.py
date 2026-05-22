import customtkinter as ctk
from tkinter import filedialog
import os

from utils.config_manager import load_config, save_config
from utils.logger import AppLogger
from engine.core_downloader import CoreDownloader

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("YDownload | by itscosmical")
        self.geometry("950x750")
        self.minsize(800, 650)
        
        self.config = load_config()
        self.downloader_engine = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self, width=900, height=700)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tabview.add("Downloader")
        self.tabview.add("Batch Queue")
        self.tabview.add("Settings")
        self.tabview.add("About")

        self.setup_downloader_tab()
        self.setup_batch_tab()
        self.setup_settings_tab()
        self.setup_about_tab()

    def setup_downloader_tab(self):
        tab = self.tabview.tab("Downloader")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(3, weight=1) 

        ctk.CTkLabel(tab, text="YDownload Engine", font=ctk.CTkFont(size=28, weight="bold"), text_color="#00a8ff").grid(row=0, column=0, columnspan=2, pady=(10, 20), sticky="w")

        self.url_entry = ctk.CTkEntry(tab, placeholder_text="Paste YouTube URL, Playlist, or Shorts link...", height=45, font=ctk.CTkFont(size=14))
        self.url_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)

        self.dl_btn = ctk.CTkButton(btn_frame, text="▶ START STREAM", command=lambda: self.start_download([self.url_entry.get()]), height=50, font=ctk.CTkFont(weight="bold", size=16))
        self.dl_btn.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.cancel_btn = ctk.CTkButton(btn_frame, text="⏹ ABORT", command=self.cancel_download, fg_color="#cc0000", hover_color="#ff3333", height=50, state="disabled")
        self.cancel_btn.grid(row=0, column=1, sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(tab, height=20)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.status_label = ctk.CTkLabel(tab, text="Awaiting input...", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=5, column=0, columnspan=2, sticky="w")

        self.log_box = ctk.CTkTextbox(tab, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(10, 20))
        self.app_logger = AppLogger(self.log_box)

    def setup_batch_tab(self):
        tab = self.tabview.tab("Batch Queue")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab, text="Mass Link Processor", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, sticky="w", pady=10)
        
        self.batch_box = ctk.CTkTextbox(tab, font=ctk.CTkFont(size=13))
        self.batch_box.insert("0.0", "Paste multiple URLs here (one per line)...\n")
        self.batch_box.grid(row=1, column=0, sticky="nsew", pady=10)

        ctk.CTkButton(tab, text="Download All in Queue", command=self.start_batch, height=45).grid(row=2, column=0, sticky="ew", pady=10)

    def setup_settings_tab(self):
        tab = self.tabview.tab("Settings")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)

        dir_frame = ctk.CTkFrame(tab)
        dir_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkButton(dir_frame, text="📁 Set Output Folder", command=self.set_directory).pack(side="left", padx=10, pady=10)
        self.dir_label = ctk.CTkLabel(dir_frame, text=f"Current: {self.config['output_path']}", font=ctk.CTkFont(size=11), text_color="gray")
        self.dir_label.pack(side="left", padx=10)

        self.scroll = ctk.CTkScrollableFrame(tab)
        self.scroll.grid(row=1, column=0, sticky="nsew")

        self.vars = {
            "format_choice": ctk.StringVar(value=self.config.get("format_choice", "Best Video (MP4)")),
            "quality_choice": ctk.StringVar(value=self.config.get("quality_choice", "Best Available")),
            "browser_cookie": ctk.StringVar(value=self.config.get("browser_cookie", "None")),
            "speed_limit": ctk.StringVar(value=self.config.get("speed_limit", "Unlimited")),
            "max_filesize": ctk.StringVar(value=self.config.get("max_filesize", "Unlimited")),
            "playlist_start": ctk.StringVar(value=self.config.get("playlist_start", "1")),
            "playlist_end": ctk.StringVar(value=self.config.get("playlist_end", "")),
            "custom_template": ctk.StringVar(value=self.config.get("custom_template", "%(title)s.%(ext)s")),
            
            "embed_thumbnail": ctk.BooleanVar(value=self.config.get("embed_thumbnail", True)),
            "download_subs": ctk.BooleanVar(value=self.config.get("download_subs", False)),
            "burn_subs": ctk.BooleanVar(value=self.config.get("burn_subs", False)),
            "sponsorblock": ctk.BooleanVar(value=self.config.get("sponsorblock", False)),
            "play_sound": ctk.BooleanVar(value=self.config.get("play_sound", True)),
            "write_description": ctk.BooleanVar(value=self.config.get("write_description", False)),
            "embed_metadata": ctk.BooleanVar(value=self.config.get("embed_metadata", True)),
            "force_ipv4": ctk.BooleanVar(value=self.config.get("force_ipv4", False)),
            "keep_video": ctk.BooleanVar(value=self.config.get("keep_video", False)),
            "auto_shutdown": ctk.BooleanVar(value=self.config.get("auto_shutdown", False)),
            "normalize_audio": ctk.BooleanVar(value=self.config.get("normalize_audio", False)),
            "auto_retry": ctk.BooleanVar(value=self.config.get("auto_retry", True)),
            "enable_cleanup": ctk.BooleanVar(value=self.config.get("enable_cleanup", True))
        }

        # --- MEDIA ---
        ctk.CTkLabel(self.scroll, text="Core Media Configuration", font=ctk.CTkFont(weight="bold", size=16), text_color="#00a8ff").pack(anchor="w", pady=(10, 5))
        
        row1 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row1.pack(fill="x", pady=5)
        ctk.CTkOptionMenu(row1, values=["Best Video (MP4)", "Audio Only (MP3)", "Audio Only (WAV)", "Audio Only (FLAC)"], variable=self.vars["format_choice"], command=self.update_config).pack(side="left", padx=(0, 10))
        ctk.CTkOptionMenu(row1, values=["Best Available", "4K (2160p)", "1440p", "1080p", "720p"], variable=self.vars["quality_choice"], command=self.update_config).pack(side="left")

        ctk.CTkLabel(self.scroll, text="Custom Naming Template (e.g. %(uploader)s - %(title)s):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 0))
        tmpl_entry = ctk.CTkEntry(self.scroll, textvariable=self.vars["custom_template"], width=300)
        tmpl_entry.pack(anchor="w", pady=5)
        tmpl_entry.bind("<FocusOut>", lambda e: self.update_config())

        # --- METADATA ---
        ctk.CTkLabel(self.scroll, text="Metadata & Subtitles", font=ctk.CTkFont(weight="bold", size=16), text_color="#00a8ff").pack(anchor="w", pady=(20, 5))
        grid1 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid1.pack(fill="x")
        ctk.CTkSwitch(grid1, text="Embed High-Res Thumbnail", variable=self.vars["embed_thumbnail"], command=self.update_config).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 20))
        ctk.CTkSwitch(grid1, text="Embed Chapters & Tags", variable=self.vars["embed_metadata"], command=self.update_config).grid(row=0, column=1, sticky="w", pady=5)
        ctk.CTkSwitch(grid1, text="Download Subtitles (.srt)", variable=self.vars["download_subs"], command=self.update_config).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 20))
        ctk.CTkSwitch(grid1, text="Save Description (.txt)", variable=self.vars["write_description"], command=self.update_config).grid(row=1, column=1, sticky="w", pady=5)
        ctk.CTkSwitch(grid1, text="Burn Subtitles (Hardsubs)", variable=self.vars["burn_subs"], command=self.update_config).grid(row=2, column=0, sticky="w", pady=5, padx=(0, 20))
        ctk.CTkSwitch(grid1, text="Keep Video when extracting Audio", variable=self.vars["keep_video"], command=self.update_config).grid(row=2, column=1, sticky="w", pady=5)

        # --- NETWORK & SYSTEM ---
        ctk.CTkLabel(self.scroll, text="Network & System Tasks", font=ctk.CTkFont(weight="bold", size=16), text_color="#00a8ff").pack(anchor="w", pady=(20, 5))
        grid2 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        grid2.pack(fill="x")
        ctk.CTkSwitch(grid2, text="SponsorBlock (Auto-cut ads)", variable=self.vars["sponsorblock"], command=self.update_config).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 20))
        ctk.CTkSwitch(grid2, text="Force IPv4", variable=self.vars["force_ipv4"], command=self.update_config).grid(row=0, column=1, sticky="w", pady=5)
        ctk.CTkSwitch(grid2, text="Auto-Delete videos starting with numbers", variable=self.vars["enable_cleanup"], command=self.update_config).grid(row=1, column=0, sticky="w", pady=5, padx=(0, 20))
        ctk.CTkSwitch(grid2, text="Play Finish Sound", variable=self.vars["play_sound"], command=self.update_config).grid(row=1, column=1, sticky="w", pady=5)
        ctk.CTkSwitch(grid2, text="Shutdown PC when finished", variable=self.vars["auto_shutdown"], command=self.update_config).grid(row=2, column=0, sticky="w", pady=5, padx=(0, 20))
        ctk.CTkSwitch(grid2, text="Auto-Retry on connection drop", variable=self.vars["auto_retry"], command=self.update_config).grid(row=2, column=1, sticky="w", pady=5)

        ctk.CTkLabel(self.scroll, text="Auth Bypass (Browser Cookies):").pack(anchor="w", pady=(15, 0))
        ctk.CTkOptionMenu(self.scroll, values=["None", "Chrome", "Edge", "Firefox", "Opera", "Brave"], variable=self.vars["browser_cookie"], command=self.update_config).pack(anchor="w", pady=5)

        row3 = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row3.pack(fill="x", pady=10)
        
        limit_frame = ctk.CTkFrame(row3, fg_color="transparent")
        limit_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(limit_frame, text="Speed Limit:").pack(anchor="w")
        ctk.CTkOptionMenu(limit_frame, values=["Unlimited", "10 MB/s", "5 MB/s", "1 MB/s", "500 KB/s"], variable=self.vars["speed_limit"], command=self.update_config).pack(anchor="w")

        size_frame = ctk.CTkFrame(row3, fg_color="transparent")
        size_frame.pack(side="left")
        ctk.CTkLabel(size_frame, text="Max File Size:").pack(anchor="w")
        ctk.CTkOptionMenu(size_frame, values=["Unlimited", "500M", "1G", "2G", "5G"], variable=self.vars["max_filesize"], command=self.update_config).pack(anchor="w")

        ctk.CTkLabel(self.scroll, text="Playlist Index Targeting (Start/End video numbers):").pack(anchor="w", pady=(10, 0))
        pl_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        pl_frame.pack(fill="x", pady=5)
        pl_start = ctk.CTkEntry(pl_frame, textvariable=self.vars["playlist_start"], width=60)
        pl_start.pack(side="left", padx=(0, 10))
        pl_start.bind("<FocusOut>", lambda e: self.update_config())
        pl_end = ctk.CTkEntry(pl_frame, textvariable=self.vars["playlist_end"], width=60, placeholder_text="Last")
        pl_end.pack(side="left")
        pl_end.bind("<FocusOut>", lambda e: self.update_config())

    def setup_about_tab(self):
        tab = self.tabview.tab("About")
        ctk.CTkLabel(tab, text="YDownload", font=ctk.CTkFont(size=40, weight="bold"), text_color="#00a8ff").pack(pady=(50, 5))
        ctk.CTkLabel(tab, text="Made by itscosmical", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)

    def set_directory(self):
        folder = filedialog.askdirectory()
        if folder:
            self.config["output_path"] = folder
            self.dir_label.configure(text=f"Current: {folder}")
            save_config(self.config)

    def update_config(self, *args):
        for key, var in self.vars.items():
            self.config[key] = var.get()
        save_config(self.config)

    def update_ui_progress(self, percent):
        self.progress_bar.set(percent)

    def update_ui_status(self, text):
        color = "white"
        if "ERROR" in text or "ABORT" in text: color = "red"
        elif "SUCCESS" in text: color = "#00ff00"
        self.status_label.configure(text=text, text_color=color)

    def download_finished(self):
        self.dl_btn.configure(state="normal")
        self.cancel_btn.configure(state="disabled")

    def cancel_download(self):
        if self.downloader_engine:
            self.downloader_engine.cancel()
            self.update_ui_status("ABORT SEQUENCE INITIATED...")

    def start_batch(self):
        raw_urls = self.batch_box.get("0.0", "end").strip().split('\n')
        valid_urls = [u.strip() for u in raw_urls if "http" in u]
        if valid_urls:
            self.tabview.set("Downloader")
            self.start_download(valid_urls)

    def start_download(self, urls):
        urls = [u for u in urls if u.strip()]
        if not urls: return

        self.dl_btn.configure(state="disabled")
        self.cancel_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.log_box.delete("0.0", "end")

        self.downloader_engine = CoreDownloader(
            config=self.config,
            logger=self.app_logger,
            progress_callback=self.update_ui_progress,
            status_callback=self.update_ui_status,
            finish_callback=self.download_finished
        )
        self.downloader_engine.start(urls)