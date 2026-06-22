import tkinter as tk
from tkinter import ttk
from desktop.pages.dashboard import DashboardPage
from desktop.pages.chat import ChatPage
from desktop.pages.settings import SettingsPage

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Air Quality Edge Assistant")
        self.geometry("900x700")
        self.minsize(800, 600)

        # Basic styling
        style = ttk.Style(self)
        style.theme_use("clam")

        # Create a container for notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize pages
        self.dashboard_page = DashboardPage(self.notebook)
        self.chat_page = ChatPage(self.notebook)
        self.settings_page = SettingsPage(self.notebook)

        self.notebook.add(self.dashboard_page, text="Dashboard")
        self.notebook.add(self.chat_page, text="Chat")
        self.notebook.add(self.settings_page, text="Settings")

        # Update dashboard when its tab is selected
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = event.widget.select()
        tab_text = event.widget.tab(selected_tab, "text")
        
        if tab_text == "Dashboard":
            self.dashboard_page.refresh_data()
        elif tab_text == "Chat":
            self.chat_page.refresh_history()
        elif tab_text == "Settings":
            self.settings_page.load_settings()

if __name__ == "__main__":
    app = App()
    app.mainloop()
