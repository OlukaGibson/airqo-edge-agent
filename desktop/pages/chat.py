import tkinter as tk
from tkinter import ttk, scrolledtext
import requests
import threading
import json
import queue

API_BASE_URL = "http://localhost:8000"

class ChatPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.conversation_id = None
        self.queue = queue.Queue()
        self.create_widgets()
        self.check_queue()

    def create_widgets(self):
        # Chat History Display
        self.chat_display = scrolledtext.ScrolledText(self, state='disabled', wrap=tk.WORD, font=("Helvetica", 12))
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure tags for styling
        self.chat_display.tag_config('user', foreground='blue', justify='right')
        self.chat_display.tag_config('assistant', foreground='green', justify='left')
        self.chat_display.tag_config('tool', foreground='gray', justify='left', font=("Courier", 10, "italic"))
        self.chat_display.tag_config('error', foreground='red', justify='center')

        # Input Area
        input_frame = ttk.Frame(self)
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_field = ttk.Entry(input_frame, font=("Helvetica", 12))
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self.send_message())

        self.send_button = ttk.Button(input_frame, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)

    def append_message(self, sender, message, tag):
        self.chat_display.config(state='normal')
        self.chat_display.insert(tk.END, f"{sender}:\n{message}\n\n", tag)
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def send_message(self):
        message = self.input_field.get().strip()
        if not message:
            return

        self.input_field.delete(0, tk.END)
        self.append_message("You", message, 'user')
        self.send_button.config(state='disabled')

        # Run API call in a thread to keep UI responsive
        threading.Thread(target=self._post_message, args=(message,), daemon=True).start()

    def check_queue(self):
        try:
            while True:
                msg_type, args = self.queue.get_nowait()
                if msg_type == "append":
                    self.append_message(*args)
                elif msg_type == "enable_button":
                    self.send_button.config(state='normal')
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_queue)

    def _post_message(self, message):
        payload = {
            "message": message,
            "conversation_id": self.conversation_id
        }
        try:
            response = requests.post(f"{API_BASE_URL}/chat", json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                self.conversation_id = data.get("conversation_id")
                
                # Show tools if any
                tools_used = data.get("tool_calls", [])
                if tools_used:
                    tool_names = [t.get("tool") for t in tools_used]
                    self.queue.put(("append", ("System", f"Executed tools: {', '.join(tool_names)}", 'tool')))
                
                # Show answer
                answer = data.get("answer", "")
                self.queue.put(("append", ("Agent", answer, 'assistant')))
            else:
                self.queue.put(("append", ("Error", f"Server returned {response.status_code}: {response.text}", 'error')))
        except Exception as e:
            self.queue.put(("append", ("Error", f"Failed to connect to server: {e}", 'error')))
        finally:
            self.queue.put(("enable_button", ()))

    def refresh_history(self):
        # We could load history from API here if desired
        pass
