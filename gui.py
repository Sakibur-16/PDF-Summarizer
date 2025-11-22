# gui.py - FIXED: Labelframe + .env + Full Summary
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from Main import DocumentSummarizer
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

class ModernSummarizerGUI:
    def __init__(self):
        self.is_dark = False
        self.root = tk.Tk()
        self.root.title("Summify AI – OCR + Full Summary")
        self.root.geometry("950x740")
        self.root.minsize(850, 650)
        self.file_path = None
        self.processing = False
        self.cancel_event = threading.Event()
        self.style = ttk.Style()
        self.apply_theme()
        self.build_ui()

    def apply_theme(self):
        theme = "darkly" if self.is_dark else "cosmo"
        self.style.theme_use(theme)
        bg = "#0f0f0f" if self.is_dark else "#f8f9fa"
        self.root.configure(bg=bg)
        self.colors = {
            "bg": bg,
            "card": "#1e1e1e" if self.is_dark else "#ffffff",
            "fg": "#ffffff" if self.is_dark else "#2c3e50",
            "subtle": "#bbbbbb" if self.is_dark else "#6c757d",
            "log_bg": "#1a1a1a" if self.is_dark else "#2c3e50",
            "log_fg": "#cccccc" if self.is_dark else "#ecf0f1"
        }
        if hasattr(self, 'theme_btn'):
            self.theme_btn.config(text="Light Mode" if self.is_dark else "Dark Mode")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    def build_ui(self):
        header = tk.Frame(self.root, bg=self.colors["bg"], padx=30, pady=20)
        header.pack(fill=X)
        ttk.Label(header, text="Summify AI", font=("Helvetica", 20, "bold"), foreground=self.colors["fg"]).pack(side=LEFT)
        ttk.Label(header, text="OCR • Full Summary • Cancel", font=("Helvetica", 11), foreground=self.colors["subtle"]).pack(side=LEFT, padx=(15, 0))
        self.theme_btn = ttk.Button(header, text="Dark Mode", bootstyle="secondary", command=self.toggle_theme, width=12)
        self.theme_btn.pack(side=RIGHT, padx=10)

        container = tk.Frame(self.root, bg=self.colors["bg"], padx=25, pady=10)
        container.pack(fill=BOTH, expand=True)

        # FIXED: Labelframe
        file_card = ttk.Labelframe(container, text="Upload Document", bootstyle="info")
        file_card.pack(fill=X, pady=(0, 18))
        self.file_label = tk.Label(file_card, text="No file selected", bg=self.colors["card"], fg=self.colors["subtle"], font=("Consolas", 10))
        self.file_label.pack(pady=8, anchor=W)
        ttk.Button(file_card, text="Browse Files", bootstyle="success", command=self.browse).pack(pady=6)

        opt_card = ttk.Labelframe(container, text="Options", bootstyle="secondary")
        opt_card.pack(fill=X, pady=(0, 18))
        tk.Label(opt_card, text="Output Language:", bg=self.colors["card"], fg=self.colors["fg"], font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky=W, pady=8, padx=5)
        self.lang_var = tk.StringVar(value="English")
        ttk.Combobox(opt_card, textvariable=self.lang_var, values=["English", "Bengali (বাংলা)", "Arabic (العربية)"], state="readonly", bootstyle="info", width=25).grid(row=0, column=1, padx=(15, 0), pady=8, sticky=W)

        action_frame = tk.Frame(container, bg=self.colors["bg"])
        action_frame.pack(pady=15)
        self.start_btn = ttk.Button(action_frame, text="Start Summarizing", bootstyle="success", command=self.start_processing, width=20)
        self.start_btn.pack(side=LEFT, padx=8)
        self.stop_btn = ttk.Button(action_frame, text="Stop", bootstyle="danger", command=self.stop_processing, width=20)
        self.stop_btn.pack(side=LEFT, padx=8)
        self.stop_btn.pack_forget()

        prog_card = ttk.Labelframe(container, text="Progress", bootstyle="primary")
        prog_card.pack(fill=X, pady=(0, 18))
        self.progress = ttk.Progressbar(prog_card, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(fill=X, pady=8, padx=10)
        self.status_label = ttk.Label(prog_card, text="Ready", foreground="#27ae60", font=("Helvetica", 10, "bold"))
        self.status_label.pack(pady=4)

        log_card = ttk.Labelframe(container, text="Live Log", bootstyle="dark")
        log_card.pack(fill=BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(log_card, wrap=tk.WORD, height=12, font=("Consolas", 9), bg=self.colors["log_bg"], fg=self.colors["log_fg"], insertbackground="white")
        self.log_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        footer = tk.Frame(container, bg=self.colors["bg"], pady=10)
        footer.pack(fill=X)
        ttk.Button(footer, text="Clear Log", bootstyle="warning", command=lambda: self.log_text.delete(1.0, tk.END)).pack(side=LEFT, padx=5)
        ttk.Button(footer, text="Open Outputs", bootstyle="info", command=lambda: os.startfile('outputs') if sys.platform == 'win32' else os.system('open "outputs"' if sys.platform == 'darwin' else 'xdg-open "outputs"')).pack(side=LEFT, padx=5)

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("PDF & Word", "*.pdf *.docx")])
        if path:
            self.file_path = path
            self.file_label.config(text=Path(path).name, fg="#90ee90" if self.is_dark else "#27ae60")
            self.log(f"Selected: {Path(path).name}")

    def start_processing(self):
        if self.processing or not self.file_path:
            messagebox.showerror("Error", "Select a file first!")
            return
        if not API_KEY:
            messagebox.showerror("Error", "Set OPENROUTER_API_KEY in .env")
            return

        self.processing = True
        self.cancel_event.clear()
        self.start_btn.pack_forget()
        self.stop_btn.pack(side=LEFT, padx=8)
        self.progress.start(15)
        self.status_label.config(text="Processing... (OCR may take time)", foreground="#f39c12")
        self.log_text.delete(1.0, tk.END)
        threading.Thread(target=self.run_summarization, daemon=True).start()

    def stop_processing(self):
        self.cancel_event.set()
        self.log("Cancellation requested...")
        self.status_label.config(text="Stopping...", foreground="#e74c3c")

    def run_summarization(self):
        try:
            lang_map = {"English": "en", "Bengali (বাংলা)": "bn", "Arabic (العربية)": "ar"}
            bot = DocumentSummarizer(api_key=API_KEY, output_lang=lang_map[self.lang_var.get()])
            result = bot.summarise(self.file_path, cancel_event=self.cancel_event)

            if self.cancel_event.is_set():
                self.root.after(0, lambda: messagebox.showinfo("Cancelled", "Stopped by user"))
            else:
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Summary saved!\n{result['txt_path']}"))
            self.root.after(0, self.processing_done, not self.cancel_event.is_set())
        except Exception as e:
            error_msg = str(e)
            self.log(f"ERROR: {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Failed", error_msg))
            self.root.after(0, self.processing_done, False)

    def processing_done(self, success):
        self.processing = False
        self.cancel_event.clear()
        self.progress.stop()
        self.stop_btn.pack_forget()
        self.start_btn.pack(side=LEFT, padx=8)
        self.status_label.config(text="Success!" if success else "Cancelled", foreground="#27ae60" if success else "#e74c3c")

if __name__ == "__main__":
    app = ModernSummarizerGUI()
    app.root.mainloop()