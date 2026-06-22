import tkinter as tk
from tkinter import ttk
import requests

API_BASE_URL = "http://localhost:8000"

class DashboardPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="System Dashboard", font=("Helvetica", 18, "bold")).pack(pady=20)

        self.status_frame = ttk.LabelFrame(self, text="Health Status")
        self.status_frame.pack(fill=tk.X, padx=20, pady=10)

        self.ollama_status_var = tk.StringVar(value="Ollama: Unknown")
        self.api_status_var = tk.StringVar(value="API Server: Unknown")
        self.tools_var = tk.StringVar(value="Tools Loaded: 0")

        ttk.Label(self.status_frame, textvariable=self.ollama_status_var, font=("Helvetica", 12)).pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(self.status_frame, textvariable=self.api_status_var, font=("Helvetica", 12)).pack(anchor=tk.W, padx=10, pady=5)
        ttk.Label(self.status_frame, textvariable=self.tools_var, font=("Helvetica", 12)).pack(anchor=tk.W, padx=10, pady=5)

        ttk.Button(self, text="Refresh", command=self.refresh_data).pack(pady=10)

    def refresh_data(self):
        try:
            response = requests.get(f"{API_BASE_URL}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.ollama_status_var.set(f"Ollama: {data.get('ollama_status', 'Unknown')}")
                self.api_status_var.set(f"API Server: {data.get('api_server_status', 'Unknown')}")
                self.tools_var.set(f"Tools Loaded: {data.get('tool_count', 0)}")
            else:
                self.api_status_var.set("API Server: Error")
        except Exception:
            self.api_status_var.set("API Server: Offline")
            self.ollama_status_var.set("Ollama: Unknown")
