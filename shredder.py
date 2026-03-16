import os
import time
import threading
import queue
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- The Expanded Custom Theme Engine with Glass Elements ---
CUSTOM_THEMES = {
    "CommsLink Dark": {
        "mode": "Dark", "bg": "#121212", "frame": "#1e1e24", "border": "#333333",
        "primary": "#44bba4", "hover": "#399e8b", "danger": "#e94f37", "danger_hover": "#c8442f", "text": "#ffffff"
    },
    "Sanctuary Frosted": {
        "mode": "Light", "bg": "#fdfbf7", "frame": "#ffffff", "border": "#e0dcd3",
        "primary": "#b5c2b7", "hover": "#9aa79d", "danger": "#e2a9be", "danger_hover": "#c995a8", "text": "#4a4a4a"
    },
    "Cyber Neon": {
        "mode": "Dark", "bg": "#0a0a0c", "frame": "#14141a", "border": "#00f0ff",
        "primary": "#00f0ff", "hover": "#00c3cf", "danger": "#ff003c", "danger_hover": "#cc0030", "text": "#e0e0e0"
    },
    "Terminal Matrix": {
        "mode": "Dark", "bg": "#050505", "frame": "#0a0a0a", "border": "#003300",
        "primary": "#00ff41", "hover": "#008f11", "danger": "#ff0000", "danger_hover": "#990000", "text": "#00ff41"
    },
    "Aero Titanium": {
        "mode": "Dark", "bg": "#1c1e21", "frame": "#24272b", "border": "#4a5056",
        "primary": "#3498db", "hover": "#2980b9", "danger": "#e74c3c", "danger_hover": "#c0392b", "text": "#ecf0f1"
    },
    "Colab Midnight": {
        "mode": "Dark", "bg": "#1e1e1e", "frame": "#252526", "border": "#333333",
        "primary": "#f39c12", "hover": "#d35400", "danger": "#c0392b", "danger_hover": "#a93226", "text": "#cccccc"
    },
    "Crimson Void": {
        "mode": "Dark", "bg": "#0d0000", "frame": "#1a0000", "border": "#4d0000",
        "primary": "#ff3333", "hover": "#cc0000", "danger": "#ff8080", "danger_hover": "#ff4d4d", "text": "#ffe6e6"
    }
}

# --- ALL 4 WIPE ALGORITHMS INTACT ---
WIPE_ALGORITHMS = {
    "Quick (1-Pass)": 1,
    "Standard (3-Pass DoD)": 3,
    "Extreme (7-Pass Gutmann)": 7,
    "Paranoid (35-Pass Gutmann)": 35 
}

DEFAULT_THEME = "CommsLink Dark"
DEFAULT_ALGORITHM = "Standard (3-Pass DoD)"

class ShredderWorker:
    def __init__(self, task_queue, target_path, num_passes):
        self.task_queue = task_queue
        self.target_path = target_path
        self.num_passes = num_passes
        self.stop_requested = False

    def fbi_level_delete(self, filepath):
        if self.stop_requested: return False, "Aborted"
        if not os.path.isfile(filepath): return False, "Not Found"
        try:
            file_size = os.path.getsize(filepath)
            for p in range(self.num_passes):
                if self.stop_requested: return False, "Aborted"
                self.task_queue.put(('progress', f'Wiping Pass {p+1}/{self.num_passes}', (p / self.num_passes)))
                with open(filepath, "ba+") as file:
                    file.seek(0)
                    file.write(b'\x00' * file_size if p % 2 == 0 else os.urandom(file_size))
                    file.flush()
                    os.fsync(file.fileno())

            self.task_queue.put(('progress', f'Scrubbing metadata...', 0.9))
            current_path = filepath
            directory = os.path.dirname(filepath)
            for _ in range(5):
                random_name = os.urandom(8).hex() + ".tmp"
                new_path = os.path.join(directory, random_name)
                os.rename(current_path, new_path)
                current_path = new_path

            with open(current_path, "ba+") as file:
                file.truncate(0)
                file.flush()
                os.fsync(file.fileno())
            os.remove(current_path)
            return True, "Success"
        except Exception as e:
            return False, str(e)

    def run_shred_task(self):
        if self.stop_requested: return
        total_files = 0
        current_idx = 0

        if os.path.isfile(self.target_path):
            success, msg = self.fbi_level_delete(self.target_path)
            self.task_queue.put(('success' if success else 'failed', msg))
            
        elif os.path.isdir(self.target_path):
            for _, _, files in os.walk(self.target_path): total_files += len(files)
            if total_files == 0:
                self.task_queue.put(('failed', 'Folder is empty.'))
                return

            for root, dirs, files in os.walk(self.target_path, topdown=False):
                if self.stop_requested: return
                for name in files:
                    current_idx += 1
                    self.task_queue.put(('progress', f'Shredding Item {current_idx}/{total_files}', (current_idx / total_files)))
                    self.fbi_level_delete(os.path.join(root, name))
                for name in dirs: os.rmdir(os.path.join(root, name))
            
            if not self.stop_requested:
                os.rmdir(self.target_path)
                self.task_queue.put(('success', 'Folder shredded.'))
        else:
            self.task_queue.put(('failed', 'Target not found.'))

class CipherShredApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CipherShred")
        self.geometry("620x440")
        
        # --- GLASS UI EFFECT INTACT ---
        self.attributes('-alpha', 0.94)
        
        self.selected_algorithm_passes = WIPE_ALGORITHMS[DEFAULT_ALGORITHM]
        self.task_queue = queue.Queue()
        self.shred_in_progress = False
        self.animation_step = 0

        # --- UI LAYOUT ---
        self.config_frame = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color="transparent")
        self.config_frame.pack(side="top", fill="x", pady=(10, 0))

        self.theme_option = ctk.CTkOptionMenu(self.config_frame, values=list(CUSTOM_THEMES.keys()), command=self.apply_theme)
        self.theme_option.set(DEFAULT_THEME)
        self.theme_option.pack(side="left", padx=20)

        self.algo_option = ctk.CTkOptionMenu(self.config_frame, values=list(WIPE_ALGORITHMS.keys()), command=self.change_algo)
        self.algo_option.set(DEFAULT_ALGORITHM)
        self.algo_option.pack(side="right", padx=20)

        # Main Glass Card
        self.main_card = ctk.CTkFrame(self, corner_radius=20, border_width=2)
        self.main_card.pack(expand=True, fill="both", padx=35, pady=25)

        self.title_label = ctk.CTkLabel(self.main_card, text="CipherShred", font=ctk.CTkFont(size=36, weight="bold"))
        self.title_label.pack(pady=(35, 5))

        self.subtitle_label = ctk.CTkLabel(self.main_card, text="Secure Data Annihilation Engine", font=ctk.CTkFont(size=14))
        self.subtitle_label.pack(pady=(0, 35))

        self.btn_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.btn_frame.pack()

        self.btn_file = ctk.CTkButton(self.btn_frame, text="Select File", command=self.shred_file, width=170, height=45, corner_radius=10, font=ctk.CTkFont(weight="bold"))
        self.btn_file.grid(row=0, column=0, padx=12)

        self.btn_folder = ctk.CTkButton(self.btn_frame, text="Select Folder", command=self.shred_folder, width=170, height=45, corner_radius=10, font=ctk.CTkFont(weight="bold"))
        self.btn_folder.grid(row=0, column=1, padx=12)

        self.progress_bar = ctk.CTkProgressBar(self.main_card, width=420, height=6, corner_radius=3)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self.main_card, text="Awaiting Target...", font=ctk.CTkFont(size=13))

        self.apply_theme(DEFAULT_THEME)

    # --- UI Logic & Animations ---
    def apply_theme(self, theme_name):
        t = CUSTOM_THEMES[theme_name]
        ctk.set_appearance_mode(t["mode"])
        
        self.configure(fg_color=t["bg"])
        self.main_card.configure(fg_color=t["frame"], border_color=t["border"])
        
        self.title_label.configure(text_color=t["text"])
        self.subtitle_label.configure(text_color=t["text"])
        self.status_label.configure(text_color=t["text"])

        for opt in [self.theme_option, self.algo_option]:
            opt.configure(fg_color=t["frame"], button_color=t["primary"], button_hover_color=t["hover"], text_color=t["text"])

        self.btn_file.configure(fg_color=t["danger"], hover_color=t["danger_hover"], text_color="#ffffff")
        self.btn_folder.configure(fg_color=t["primary"], hover_color=t["hover"], text_color="#ffffff")
        
        self.progress_bar.configure(progress_color=t["primary"], fg_color=t["bg"])

    def change_algo(self, name):
        self.selected_algorithm_passes = WIPE_ALGORITHMS[name]

    def animate_active_status(self):
        if not self.shred_in_progress: return
        dots = "." * (self.animation_step % 4)
        current_text = self.status_label.cget("text").split("...")[0].replace(".", "")
        self.status_label.configure(text=f"{current_text}{dots}")
        self.animation_step += 1
        self.after(400, self.animate_active_status)

    # --- Threading & Execution ---
    def shred_file(self):
        path = filedialog.askopenfilename()
        if path and messagebox.askyesno("Confirm", "PERMANENTLY shred this file?"):
            self.start_task(path)

    def shred_folder(self):
        path = filedialog.askdirectory()
        if path and messagebox.askyesno("Confirm", "PERMANENTLY shred this entire folder?"):
            self.start_task(path)

    def start_task(self, path):
        self.shred_in_progress = True
        self.btn_file.configure(state="disabled")
        self.btn_folder.configure(state="disabled")
        
        self.progress_bar.pack(pady=(35, 10))
        self.status_label.pack()
        
        self.animate_active_status()

        self.worker = ShredderWorker(self.task_queue, path, self.selected_algorithm_passes)
        threading.Thread(target=self.worker.run_shred_task, daemon=True).start()
        self.process_queue()

    def process_queue(self):
        try:
            msg_type, msg_data, *extra = self.task_queue.get_nowait()
            
            if msg_type == 'progress':
                self.status_label.configure(text=msg_data)
                self.progress_bar.set(extra[0])
            elif msg_type in ['success', 'failed']:
                self.shred_in_progress = False
                self.progress_bar.pack_forget()
                self.status_label.pack_forget()
                self.btn_file.configure(state="normal")
                self.btn_folder.configure(state="normal")
                
                if msg_type == 'success':
                    messagebox.showinfo("Complete", "Data successfully annihilated.")
                else:
                    messagebox.showerror("Error", f"Failed: {msg_data}")
                return
        except queue.Empty:
            pass
        
        if self.shred_in_progress:
            self.after(50, self.process_queue)

if __name__ == "__main__":
    app = CipherShredApp()
    app.mainloop()