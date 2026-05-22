class AppLogger:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def debug(self, msg):
        self.text_widget.insert("end", msg + "\n")
        self.text_widget.see("end")

    def info(self, msg):
        self.debug(msg)

    def warning(self, msg):
        self.debug(f"[WARN] {msg}")

    def error(self, msg):
        self.debug(f"[ERROR] {msg}")