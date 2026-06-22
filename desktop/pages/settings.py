import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_BASE_URL = "http://localhost:8000"

class SettingsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Settings", font=("Helvetica", 18, "bold")).pack(pady=20)

        form_frame = ttk.Frame(self)
        form_frame.pack(fill=tk.X, padx=40, pady=10)

        # Ollama URL
        ttk.Label(form_frame, text="Ollama URL:").grid(row=0, column=0, sticky=tk.W, pady=10)
        self.ollama_url_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ollama_url_var, width=40).grid(row=0, column=1, sticky=tk.W, padx=10)

        # Model Name
        ttk.Label(form_frame, text="Model Name:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.model_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.model_name_var, width=40).grid(row=1, column=1, sticky=tk.W, padx=10)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Reload", command=self.load_settings).pack(side=tk.LEFT, padx=10)

    def load_settings(self):
        try:
            response = requests.get(f"{API_BASE_URL}/settings", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.ollama_url_var.set(data.get("OLLAMA_URL", "http://localhost:11434"))
                self.model_name_var.set(data.get("DEFAULT_MODEL", "gemma:2b"))
        except Exception:
            pass # Ignore if API is offline

    def save_settings(self):
        updates = {
            "OLLAMA_URL": self.ollama_url_var.get(),
            "DEFAULT_MODEL": self.model_name_var.get()
        }
        try:
            response = requests.post(f"{API_BASE_URL}/settings", json=updates, timeout=5)
            if response.status_code == 200:
                messagebox.showinfo("Success", "Settings saved successfully.")
            else:
                messagebox.showerror("Error", f"Failed to save settings: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not connect to API server: {e}")
