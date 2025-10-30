# GUI.py - FULL DARK MODE + NO TCL ERROR
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
        self.root.title("Summify AI – Smart Document Summarizer")
        self.root.geometry("950x740")
        self.root.minsize(850, 650)

        self.file_path = None
        self.processing = False
        self.cancel_event = threading.Event()

        self.style = ttk.Style()
        self.apply_theme()
        self.build_ui()

    def apply_theme(self):
        if self.is_dark:
            self.root.configure(bg="#0f0f0f")
            bg = "#1e1e1e"
            card_bg = "#252526"
            fg = "#ffffff"
            subtle = "#bbbbbb"
            log_bg = "#1a1a1a"
            log_fg = "#cccccc"
            theme_name = "darkly"
        else:
            self.root.configure(bg="#f8f9fa")
            bg = "#f8f9fa"
            card_bg = "#ffffff"
            fg = "#2c3e50"
            subtle = "#6c757d"
            log_bg = "#2c3e50"
            log_fg = "#ecf0f1"
            theme_name = "cosmo"

        self.style.theme_use(theme_name)

        # Configure styles
        self.style.configure("Card.TFrame", background=card_bg, relief="flat", borderwidth=1, padding=15)
        self.style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), foreground=fg)
        self.style.configure("Subtitle.TLabel", font=("Helvetica", 11), foreground=subtle)
        self.style.configure("Accent.TButton", font=("Helvetica", 11, "bold"), padding=12)
        self.style.map("Accent.TButton",
                       background=[("active", "#0e78d4" if self.is_dark else "#3498db")],
                       foreground=[("active", "white")])

        # Store colors for later use
        self.colors = {
            "root_bg": self.root.cget("bg"),
            "card_bg": card_bg,
            "fg": fg,
            "subtle": subtle,
            "log_bg": log_bg,
            "log_fg": log_fg
        }

        # Update widgets if they exist
        if hasattr(self, 'file_label'):
            self.file_label.config(bg=card_bg, fg=subtle)
        if hasattr(self, 'log_text'):
            self.log_text.config(bg=log_bg, fg=log_fg, insertbackground="white" if self.is_dark else "black")
        if hasattr(self, 'theme_btn'):
            self.theme_btn.config(text="Light Mode" if self.is_dark else "Dark Mode")

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.apply_theme()

    def build_ui(self):
        # Header
        header = tk.Frame(self.root, bg=self.colors["root_bg"], padx=30, pady=20)
        header.pack(fill=X)

        ttk.Label(header, text="Summify AI", style="Title.TLabel").pack(side=LEFT)
        ttk.Label(header, text="Upload • Summarize • Understand", style="Subtitle.TLabel") \
            .pack(side=LEFT, padx=(15, 0))

        self.theme_btn = ttk.Button(header, text="Dark Mode", bootstyle=SECONDARY, command=self.toggle_theme, width=12)
        self.theme_btn.pack(side=RIGHT, padx=10)

        container = tk.Frame(self.root, bg=self.colors["root_bg"], padx=25, pady=10)
        container.pack(fill=BOTH, expand=True)

        # File Card
        file_card = ttk.LabelFrame(container, text="Upload Document", bootstyle=INFO, style="Card.TFrame")
        file_card.pack(fill=X, pady=(0, 18))
        self.file_label = tk.Label(file_card, text="No file selected", bg=self.colors["card_bg"], fg=self.colors["subtle"], font=("Consolas", 10))
        self.file_label.pack(pady=8, anchor=W)
        ttk.Button(file_card, text="Browse Files", bootstyle=SUCCESS, command=self.browse).pack(pady=6)

        # Options Card
        opt_card = ttk.LabelFrame(container, text="Options", bootstyle=SECONDARY, style="Card.TFrame")
        opt_card.pack(fill=X, pady=(0, 18))

        tk.Label(opt_card, text="Output Language:", bg=self.colors["card_bg"], fg=self.colors["fg"], font=("Helvetica", 10, "bold")) \
            .grid(row=0, column=0, sticky=W, pady=8, padx=5)
        self.lang_var = tk.StringVar(value="English")
        ttk.Combobox(opt_card, textvariable=self.lang_var,
                     values=["English", "Bengali (বাংলা)", "Arabic (العربية)"],
                     state="readonly", bootstyle=INFO, width=25) \
            .grid(row=0, column=1, padx=(15, 0), pady=8, sticky=W)

        tk.Label(opt_card, text="Document Type:", bg=self.colors["card_bg"], fg=self.colors["fg"], font=("Helvetica", 10, "bold")) \
            .grid(row=1, column=0, sticky=W, pady=8, padx=5)
        self.type_var = tk.StringVar(value="book")
        ttk.Combobox(opt_card, textvariable=self.type_var,
                     values=["book", "article", "research", "general"],
                     state="readonly", bootstyle=INFO, width=25) \
            .grid(row=1, column=1, padx=(15, 0), pady=8, sticky=W)

        # Action Buttons
        action_frame = tk.Frame(container, bg=self.colors["root_bg"])
        action_frame.pack(pady=15)

        self.start_btn = ttk.Button(action_frame, text="Start Summarizing", style="Accent.TButton",
                                    bootstyle=SUCCESS, command=self.start_processing, width=20)
        self.start_btn.pack(side=LEFT, padx=8)

        self.stop_btn = ttk.Button(action_frame, text="Stop Summarizing", style="Accent.TButton",
                                   bootstyle=DANGER, command=self.stop_processing, width=20)
        self.stop_btn.pack(side=LEFT, padx=8)
        self.stop_btn.pack_forget()

        # Progress
        prog_card = ttk.LabelFrame(container, text="Progress", bootstyle=PRIMARY, style="Card.TFrame")
        prog_card.pack(fill=X, pady=(0, 18))
        self.progress = ttk.Progressbar(prog_card, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(fill=X, pady=8, padx=10)
        self.status_label = ttk.Label(prog_card, text="Ready", foreground="#27ae60", font=("Helvetica", 10, "bold"))
        self.status_label.pack(pady=4)

        # Log
        log_card = ttk.LabelFrame(container, text="Live Log", bootstyle=DARK, style="Card.TFrame")
        log_card.pack(fill=BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(
            log_card, wrap=tk.WORD, height=12, font=("Consolas", 9),
            bg=self.colors["log_bg"], fg=self.colors["log_fg"], insertbackground="white", relief="flat", bd=0
        )
        self.log_text.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Footer
        footer = tk.Frame(container, bg=self.colors["root_bg"], pady=10)
        footer.pack(fill=X)
        ttk.Button(footer, text="Clear Log", bootstyle=WARNING, command=self.clear_log).pack(side=LEFT, padx=5)
        ttk.Button(footer, text="Open Outputs", bootstyle=INFO, command=self.open_outputs).pack(side=LEFT, padx=5)

    def log(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{ts}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def browse(self):
        path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[("PDF & Word", "*.pdf *.docx"), ("All", "*.*")]
        )
        if path:
            self.file_path = path
            self.file_label.config(text=Path(path).name, fg="#90ee90" if self.is_dark else "#27ae60")
            self.log(f"Selected: {Path(path).name}")

    def open_outputs(self):
        out = Path('outputs')
        out.mkdir(exist_ok=True)
        if sys.platform == 'win32':
            os.startfile(out)
        elif sys.platform == 'darwin':
            os.system(f'open "{out}"')
        else:
            os.system(f'xdg-open "{out}"')

    def start_processing(self):
        if self.processing: return
        if not self.file_path:
            messagebox.showerror("Error", "Please select a document first!")
            return
        if not API_KEY:
            messagebox.showerror("Error", "Set OPENROUTER_API_KEY in .env")
            return

        self.processing = True
        self.cancel_event.clear()

        self.start_btn.pack_forget()
        self.stop_btn.pack(side=LEFT, padx=8)
        self.progress.start(15)
        self.status_label.config(text="Summarizing... (this may take 1-3 minutes)", foreground="#f39c12")
        self.clear_log()

        threading.Thread(target=self.run_summarization, daemon=True).start()

    def stop_processing(self):
        if not self.processing: return
        self.cancel_event.set()
        self.log("Cancellation requested...")
        self.status_label.config(text="Stopping... Please wait", foreground="#e74c3c")

    def run_summarization(self):
        try:
            lang_map = {"English": "en", "Bengali (বাংলা)": "bn", "Arabic (العربية)": "ar"}
            out_lang = lang_map[self.lang_var.get()]

            bot = DocumentSummarizer(api_key=API_KEY, output_lang=out_lang)
            result = bot.summarise(self.file_path, doc_type=self.type_var.get(), cancel_event=self.cancel_event)

            if self.cancel_event.is_set():
                self.root.after(0, self.processing_done, False, "Cancelled by user")
                return

            self.log("="*60)
            self.log("SUMMARIZATION COMPLETE!")
            self.log(f"File: {result['file']}")
            self.log(f"Chapters: {len(result['chapters'])}")
            self.log(f"Saved: {result['json_path']}")
            self.log(f"Readable: {result['txt_path']}")

            self.root.after(0, self.processing_done, True, result['txt_path'])

        except Exception as e:
            if not self.cancel_event.is_set():
                self.log(f"ERROR: {e}")
            self.root.after(0, self.processing_done, False, str(e))

    def processing_done(self, success, msg):
        self.processing = False
        self.cancel_event.clear()
        self.progress.stop()
        self.stop_btn.pack_forget()
        self.start_btn.pack(side=LEFT, padx=8)

        if success:
            self.status_label.config(text="Success! Summary saved", foreground="#27ae60")
            messagebox.showinfo("Done", f"Summary ready!\n\nTXT: {msg}")
        else:
            self.status_label.config(text="Failed or Cancelled", foreground="#e74c3c")
            if "Cancelled" not in msg:
                messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = ModernSummarizerGUI()
    app.root.mainloop()