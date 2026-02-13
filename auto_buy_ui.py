import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
import time
import json
import os
from pynput import keyboard

# Replicating logic from auto_buy_potions.py but integrated into UI
TOTAL_ITEMS = 10000
MAX_PER_BUY = 200
LOOPS = TOTAL_ITEMS // MAX_PER_BUY
AUTOBUY_CONFIG_FILE = "autobuy_config.json"

class AutoBuyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MapleBuyer")
        self.root.geometry("200x220")
        
        # position top right
        screen_width = root.winfo_screenwidth()
        x_pos = screen_width - 220
        self.root.geometry(f"200x220+{x_pos}+50")
        
        # Always on top
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.9) # Slight transparency
        
        self.running = False
        self.input_pos = None
        self.confirm_pos = None
        
        self.create_widgets()
        self.load_config()
        
        # Start keyboard listener
        self.listener_thread = threading.Thread(target=self.start_listener, daemon=True)
        self.listener_thread.start()

    def create_widgets(self):
        # Styles
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 10))
        style.configure("TLabel", font=("Helvetica", 10))
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        self.lbl_status = tk.Label(self.root, textvariable=self.status_var, fg="white", bg="#333", font=("Helvetica", 12, "bold"), pady=5)
        self.lbl_status.pack(fill=tk.X)
        self.root.configure(bg="#222")

        # Info
        frm_info = tk.Frame(self.root, bg="#222")
        frm_info.pack(pady=5)
        
        self.lbl_locs = tk.Label(frm_info, text="Locs: Not Set", fg="#aaa", bg="#222", font=("Helvetica", 9))
        self.lbl_locs.pack()

        # Buttons
        frm_btns = tk.Frame(self.root, bg="#222")
        frm_btns.pack(pady=5, padx=10, fill=tk.X)
        
        btn_set_input = tk.Button(frm_btns, text="Set Input (F9)", command=self.set_input_pos_manual, bg="#444", fg="white", highlightbackground="#222")
        btn_set_input.pack(fill=tk.X, pady=2)
        
        btn_set_confirm = tk.Button(frm_btns, text="Set Confirm (F8)", command=self.set_confirm_pos_manual, bg="#444", fg="white", highlightbackground="#222")
        btn_set_confirm.pack(fill=tk.X, pady=2)
        
        self.btn_toggle = tk.Button(self.root, text="START (F10)", command=self.toggle_running, bg="#2ecc71", fg="black", highlightbackground="#222", font=("Helvetica", 12, "bold"))
        self.btn_toggle.pack(fill=tk.X, padx=10, pady=10)

        # Instructions
        tk.Label(self.root, text="ESC to Stop", fg="#666", bg="#222", font=("Helvetica", 8)).pack(side=tk.BOTTOM, pady=5)

    def update_loc_label(self):
        i_ok = "✓" if self.input_pos else "✗"
        c_ok = "✓" if self.confirm_pos else "✗"
        self.lbl_locs.config(text=f"Input: {i_ok} | Confirm: {c_ok}")
        
    def load_config(self):
        if os.path.exists(AUTOBUY_CONFIG_FILE):
            try:
                with open(AUTOBUY_CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.input_pos = tuple(data.get('INPUT_BOX_POS')) if data.get('INPUT_BOX_POS') else None
                    self.confirm_pos = tuple(data.get('CONFIRM_BTN_POS')) if data.get('CONFIRM_BTN_POS') else None
                    self.update_loc_label()
            except:
                pass

    def save_config(self):
        data = { 'INPUT_BOX_POS': self.input_pos, 'CONFIRM_BTN_POS': self.confirm_pos }
        try:
            with open(AUTOBUY_CONFIG_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

    def set_input_pos_manual(self):
        # We can't easily "wait for click" without blocking UI or complex hooks in pure python without listener
        # So we just tell user to hover and press F9, OR we take current mouse pos now
        self.status_var.set("Hover & Press F9")
        
    def set_confirm_pos_manual(self):
        self.status_var.set("Hover & Press F8")

    def toggle_running(self):
        if not self.running:
            if not self.input_pos or not self.confirm_pos:
                self.status_var.set("Set Locs First!")
                return
            self.start_loop()
        else:
            self.stop_loop()

    def start_loop(self):
        self.running = True
        self.btn_toggle.config(text="STOP (Esc)", bg="#e74c3c")
        self.status_var.set("Running...")
        # Run buy loop in thread
        threading.Thread(target=self.buy_loop_thread, daemon=True).start()

    def stop_loop(self):
        self.running = False
        self.btn_toggle.config(text="START (F10)", bg="#2ecc71")
        self.status_var.set("Stopped")

    def buy_loop_thread(self):
        # Initial Item capture
        item_x, item_y = pyautogui.position()
        
        for i in range(LOOPS):
            if not self.running: break
            
            self.root.after(0, lambda x=i: self.status_var.set(f"Batch {x+1}/{LOOPS}"))
            
            # 1. Click Item
            pyautogui.moveTo(item_x, item_y)
            pyautogui.click()
            time.sleep(0.08)
            pyautogui.click()
            
            time.sleep(0.8)
            if not self.running: break

            # 2. Input Box
            if self.input_pos:
                pyautogui.click(self.input_pos)
                time.sleep(0.15)
            
            # 3. Type
            pyautogui.write(str(MAX_PER_BUY), interval=0.05)
            time.sleep(0.2)
            
            # 4. Confirm
            if not self.running: break
            if self.confirm_pos:
                pyautogui.click(self.confirm_pos)
                time.sleep(0.3)
                
            time.sleep(0.5)
            
        self.root.after(0, self.stop_loop)

    def start_listener(self):
        def on_key(key):
            try:
                if key == keyboard.Key.f8:
                    x, y = pyautogui.position()
                    self.confirm_pos = (x, y)
                    self.save_config()
                    self.root.after(0, self.update_loc_label)
                    self.root.after(0, lambda: self.status_var.set("Confirm Set!"))
                    
                elif key == keyboard.Key.f9:
                    x, y = pyautogui.position()
                    self.input_pos = (x, y)
                    self.save_config()
                    self.root.after(0, self.update_loc_label)
                    self.root.after(0, lambda: self.status_var.set("Input Set!"))

                elif key == keyboard.Key.f10:
                    if not self.running:
                        self.root.after(0, self.toggle_running)
                        
                elif key == keyboard.Key.esc:
                    if self.running:
                        self.root.after(0, self.stop_loop)
            except:
                pass
        
        with keyboard.Listener(on_press=on_key) as listener:
            listener.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoBuyApp(root)
    root.mainloop()
