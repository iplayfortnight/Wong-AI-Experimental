import os
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox

class SimpleLauncher:
    def __init__(self):
        self.master_password = ""
        self.root = tk.Tk()
        self.root.title("Unlock AGI Memory Vault")
        self.root.geometry("350x150")
        self.root.eval('tk::PlaceWindow . center')
        
        tk.Label(self.root, text="Enter Master Password:", font=("Arial", 11)).pack(pady=10)
        self.entry = tk.Entry(self.root, show="*", font=("Arial", 12), width=25)
        self.entry.pack()
        self.entry.focus_set()
        
        self.entry.bind("<Return>", lambda e: self.submit())
        tk.Button(self.root, text="Unlock", font=("Arial", 10, "bold"), command=self.submit).pack(pady=15)

    def submit(self):
        pwd = self.entry.get().strip()
        if len(pwd) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long.")
            return
        self.master_password = pwd
        self.root.destroy()

    def start(self):
        self.root.mainloop()
        if not self.master_password:
            sys.exit(1)

        print("[BOOT] Starting background telemetry processes...")
        daemon = subprocess.Popen([sys.executable, "sensor_daemon.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2.0)

        print("\n--- SYSTEM ONLINE: RUNNING NATIVELY ON LOCAL STORAGE CELL ---")
        try:
            while True:
                user_input = input("\nEnter prompt for the AGI Node (or type 'exit' to quit): ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                if user_input:
                    subprocess.run([sys.executable, "ai_core.py", self.master_password, user_input])
        finally:
            daemon.terminate()
            if os.path.exists("daemon_pulse.tmp"):
                os.remove("daemon_pulse.tmp")

if __name__ == "__main__":
    app = SimpleLauncher()
    app.start()
