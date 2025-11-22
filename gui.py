# gui.py - Summify AI - Perfect Dark Mode + Modern UI (FINAL)
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
from ttkbootstrap.widgets import ToolTip

load_dotenv(override=True)
API_KEY = os.getenv("OPENROUTER_API_KEY")

class ModernSummarizerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Summify AI – Intelligent Document Summarizer")
        self.root.geometry("1150x820")
        self.root.minsize(1000, 700)

        self.is_dark = True
        self.file_path = None
        self.processing = False
        self.cancel_event = threading.Event()

        self.style = ttk.Style()
        self.colors = {}
        self.apply_theme()
        self.build_ui()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def apply_theme(self):
        self.is_dark = not self.is_dark if getattr(self, "toggle_requested", False) else self.is_dark
        self.toggle_requested = False

        # ttkbootstrap theme
        theme_name = "darkly" if self.is_dark else "flatly"
        self.style.theme_use(theme_name)

        # Custom color palette
        if self.is_dark:
            self.colors = {
                "bg": "#0d1117",
                "card": "#161b22",
                "border": "#30363d",
                "fg": "#f0f6fc",
                "subtle": "#8b949e",
                "accent": "#00d4aa",
                "header": "#00d4aa",
                "log_bg": "#0d1117",
                "log_fg": "#58f5d2"
            }
        else:
            self.colors = {
                "bg": "#f6f8fa",
                "card": "#ffffff",
                "border": "#d0d7de",
                "fg": "#24292f",
                "subtle": "#57606a",
                "accent": "#00b894",
                "header": "#00b894",
                "log_bg": "#ffffff",
                "log_fg": "#1e3a8a"
            }

        # Update root and all widgets
        self.root.configure(bg=self.colors["bg"])
        if hasattr(self, "widgets_to_recolor"):
            for widget in self.widgets_to_recolor:
                self.recolor_widget(widget)

        # Update theme button text
        if hasattr(self, "theme_btn"):
            self.theme_btn.configure(text="Light Mode" if self.is_dark else "Dark Mode")

    def recolor_widget(self, widget):
        try:
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.configure(bg=self.colors["bg"])
            elif isinstance(widget, tk.Label):
                if widget not in [self.file_label, self.file_details, self.status_label]:
                    widget.configure(bg=self.colors["bg"], fg=self.colors["fg"])
                # Special labels keep their own colors
            elif isinstance(widget, scrolledtext.ScrolledText):
                widget.configure(bg=self.colors["log_bg"], fg=self.colors["log_fg"])
        except: pass

        for child in widget.winfo_children():
            self.recolor_widget(child)

    def toggle_theme(self):
        self.toggle_requested = True
        self.apply_theme()

    def build_ui(self):
        self.widgets_to_recolor = []

        # Header
        header = tk.Frame(self.root, bg=self.colors["header"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        self.widgets_to_recolor.append(header)

        tk.Label(header, text="Summify AI", font=("Segoe UI", 28, "bold"),
                 bg=self.colors["header"], fg="white").place(x=30, y=12)
        tk.Label(header, text="OCR • Full-Text Summary • Multilingual • Export",
                 font=("Segoe UI", 11), bg=self.colors["header"], fg="white").place(x=32, y=62)

        self.theme_btn = ttk.Button(header, text="Light Mode", bootstyle="link", command=self.toggle_theme)
        self.theme_btn.place(x=1000, y=28)

        # Main container
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=30, pady=20)
        self.widgets_to_recolor.append(main)

        # Left Panel
        left = tk.Frame(main, bg=self.colors["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(0, 15))
        self.widgets_to_recolor.append(left)

        # Right Panel (Log)
        right = tk.Frame(main, bg=self.colors["bg"])
        right.pack(side="right", fill="both", expand=True, padx=(15, 0))
        self.widgets_to_recolor.append(right)

        # File Card
        file_card = ttk.Labelframe(left, text=" Document Upload", bootstyle="primary")
        file_card.pack(fill="x", pady=(0, 20))
        self.widgets_to_recolor.append(file_card)

        info_frame = tk.Frame(file_card, bg=self.colors["card"], relief="solid", bd=1)
        info_frame.pack(fill="x", pady=12, padx=12)
        self.widgets_to_recolor.append(info_frame)

        self.file_label = tk.Label(info_frame, text="No file selected", font=("Consolas", 11),
                                   bg=self.colors["card"], fg=self.colors["subtle"], anchor="w")
        self.file_label.pack(fill="x", padx=10, pady=(8, 2))

        self.file_details = tk.Label(info_frame, text="", font=("Helvetica", 9),
                                     bg=self.colors["card"], fg=self.colors["subtle"])
        self.file_details.pack(anchor="w", padx=10, pady=(0, 8))

        browse_btn = ttk.Button(file_card, text="Browse Files", bootstyle="success-outline",
                                command=self.browse, width=28)
        browse_btn.pack(pady=10)
        ToolTip(browse_btn, text="PDF & .docx files supported")

        # Options
        opt_card = ttk.Labelframe(left, text=" Summary Options", bootstyle="info")
        opt_card.pack(fill="x", pady=(0, 20))
        self.widgets_to_recolor.append(opt_card)

        tk.Label(opt_card, text="Language:", font=("Helvetica", 11, "bold"),
                 bg=self.colors["card"], fg=self.colors["fg"]).grid(row=0, column=0, padx=15, pady=15, sticky="w")
        self.lang_var = tk.StringVar(value="English")
        ttk.Combobox(opt_card, textvariable=self.lang_var,
                     values=["English", "Bengali (বাংলা)", "Arabic (العربية)", "Spanish", "French", "Hindi"],
                     state="readonly", width=28).grid(row=0, column=1, padx=15, pady=15, sticky="w")

        # Buttons
        btn_frame = tk.Frame(left, bg=self.colors["bg"])
        btn_frame.pack(pady=25)
        self.widgets_to_recolor.append(btn_frame)

        self.start_btn = ttk.Button(btn_frame, text="Start Summarizing", bootstyle="success",
                                    command=self.start_processing, width=24)
        self.start_btn.pack(side="left", padx=10)

        self.stop_btn = ttk.Button(btn_frame, text="Stop", bootstyle="danger",
                                   command=self.stop_processing, width=16)
        self.stop_btn.pack(side="left", padx=10)
        self.stop_btn.pack_forget()

        # Progress
        prog_card = ttk.Labelframe(left, text=" Progress", bootstyle="warning")
        prog_card.pack(fill="x", pady=(0, 20))
        self.widgets_to_recolor.append(prog_card)

        self.progress = ttk.Progressbar(prog_card, mode="determinate", bootstyle="success-striped")
        self.progress.pack(fill="x", padx=15, pady=12)

        self.status_label = ttk.Label(prog_card, text="Ready", font=("Helvetica", 10))
        self.status_label.pack(pady=5)

        # Log Panel
        log_card = ttk.Labelframe(right, text=" Live Activity Log", bootstyle="secondary")
        log_card.pack(fill="both", expand=True)
        self.widgets_to_recolor.append(log_card)

        self.log_text = scrolledtext.ScrolledText(log_card, font=("Consolas", 10),
                                                  bg=self.colors["log_bg"], fg=self.colors["log_fg"],
                                                  insertbackground=self.colors["accent"])
        self.log_text.pack(fill="both", expand=True, padx=12, pady=12)

        # Footer
        footer = tk.Frame(self.root, bg=self.colors["bg"])
        footer.pack(fill="x", pady=15, padx=30)
        self.widgets_to_recolor.append(footer)

        ttk.Button(footer, text="Clear Log", bootstyle="outline-secondary",
                   command=lambda: self.log_text.delete(1.0, "end")).pack(side="left", padx=5)
        ttk.Button(footer, text="Open Outputs", bootstyle="primary-outline",
                   command=self.open_outputs).pack(side="left", padx=5)
        tk.Label(footer, text="© 2025 Summify AI • Built with OpenRouter", fg=self.colors["subtle"],
                 bg=self.colors["bg"], font=("Helvetica", 9)).pack(side="right")

    def open_outputs(self):
        Path("outputs").mkdir(exist_ok=True)
        os.startfile("outputs") if sys.platform == "win32" else \
        os.system('open "outputs"' if sys.platform == "darwin" else 'xdg-open "outputs"')

    def log(self, msg, level="INFO"):
        icons = {"INFO": "•", "SUCCESS": "Success", "WARNING": "Warning", "ERROR": "Error", "CANCEL": "Cancel"}
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"{icons.get(level, 'Info')} [{ts}] {msg}\n")
        self.log_text.see("end")

    def browse(self):
        path = filedialog.askopenfilename(filetypes=[("PDF & Word", "*.pdf *.docx")])
        if path:
            self.file_path = path
            p = Path(path)
            size_mb = p.stat().st_size / (1024**2)
            self.file_label.config(text=p.name, fg=self.colors["accent"])
            self.file_details.config(text=f"Size: {size_mb:.2f} MB • Path: {p.parent}")
            self.log(f"Selected: {p.name}", "SUCCESS")

    def start_processing(self):
        if self.processing or not self.file_path or not API_KEY:
            messagebox.showwarning("Error", "Select file + set API key first!")
            return

        self.processing = True
        self.cancel_event.clear()
        self.progress["value"] = 0
        self.start_btn.pack_forget()
        self.stop_btn.pack(side="left", padx=10)
        self.status_label.config(text="Processing...")
        self.log_text.delete(1.0, "end")
        self.log("Summarization started...")

        threading.Thread(target=self.run_summarization, daemon=True).start()
        self.animate_progress()

    def animate_progress(self):
        if not self.processing: return
        for i in range(10, 101, 12):
            if not self.processing or self.cancel_event.is_set(): break
            self.root.after(i*120, lambda v=i: (
                self.progress.config(value=v),
                self.status_label.config(text=f"Processing... {v}%")
            ))

    def stop_processing(self):
        self.cancel_event.set()
        self.log("Cancelled by user", "CANCEL")

    def run_summarization(self):
        try:
            lang_map = {"English": "en", "Bengali": "bn", "Arabic": "ar", "Spanish": "es", "French": "fr", "Hindi": "hi"}
            lang = lang_map.get(self.lang_var.get().split()[0], "en")

            bot = DocumentSummarizer(api_key=API_KEY, output_lang=lang)
            result = bot.summarise(self.file_path, cancel_event=self.cancel_event)

            success = not self.cancel_event.is_set()
            path = result.get("txt_path", "outputs/summary.txt") if success else None

            if success:
                self.root.after(0, lambda: messagebox.showinfo("Success!", f"Summary saved!\n{path}"))
                self.log("Summary completed!", "SUCCESS")
            else:
                self.root.after(0, lambda: messagebox.showinfo("Cancelled", "Process stopped."))

            self.root.after(0, self.processing_done, success)

        except Exception as e:
            self.log(f"ERROR: {e}", "ERROR")
            self.root.after(0, lambda: messagebox.showerror("Failed", str(e)))
            self.root.after(0, self.processing_done, False)

    def processing_done(self, success):
        self.processing = False
        self.stop_btn.pack_forget()
        self.start_btn.pack(side="left", padx=10)
        self.progress["value"] = 100 if success else 0
        self.status_label.config(text="Completed!" if success else "Stopped",
                                  foreground=self.colors["accent"] if success else self.colors["subtle"])

    def on_close(self):
        if self.processing and messagebox.askyesno("Quit", "Processing in progress. Cancel and exit?"):
            self.cancel_event.set()
            self.root.after(1000, self.root.destroy)
        else:
            self.root.destroy()


if __name__ == "__main__":
    app = ModernSummarizerGUI()
    app.root.mainloop()