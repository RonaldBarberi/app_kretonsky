# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 18:41:48 2024

@author: Ronal.Barberi
"""

#%% Import libraries

import os
import sys
import time
import json
import psutil
import threading
import subprocess
import tkinter as tk
from tkinter import ttk
from _cls_nav_directorys import Nav_Directorys as nd

#%% Create class

class FunctionExecuter:
    def __init__(self, varPathVenv, varScriptsPath, varScriptExecute, varTreeview, varProcessId, varConsoleOutput):
        self.varPathVenv = varPathVenv
        self.varScriptsPath = varScriptsPath
        self.varScriptExecute = varScriptExecute
        self.varTreeview = varTreeview
        self.varProcessId = varProcessId
        self.varConsoleOutput = varConsoleOutput

    def execute_process(self):
        full_path_script = f'{self.varScriptsPath}\\{self.varScriptExecute}'
        command = [f'{self.varPathVenv}\\Scripts\\python', '-u', full_path_script]
        print(f"Executing: {' '.join(command)}")
        self.varConsoleOutput.insert(tk.END, f"Executing: {' '.join(command)}\n")
        self.varConsoleOutput.see(tk.END)

        start_time = time.time()
        self.varTreeview.item(self.varProcessId, values=(self.varTreeview.item(self.varProcessId)['values'][0], 
                                                    self.varScriptExecute, 
                                                    "In Progress", 
                                                    "Calculating..."))
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1) as proc:
                for line in proc.stdout:
                    self.varConsoleOutput.insert(tk.END, line)
                    self.varConsoleOutput.see(tk.END)
                    sys.stdout.write(line)
                proc.wait()

            elapsed_time = time.time() - start_time
            if proc.returncode == 0:
                self.varTreeview.item(self.varProcessId, values=(self.varTreeview.item(self.varProcessId)['values'][0], 
                                                            self.varScriptExecute, 
                                                            "Success", 
                                                            f"{elapsed_time:.2f} seconds"))
                print(f"{self.varScriptExecute} executing correct.")
            else:
                self.varTreeview.item(self.varProcessId, values=(self.varTreeview.item(self.varProcessId)['values'][0], 
                                                            self.varScriptExecute, 
                                                            "Failed", 
                                                            f"{elapsed_time:.2f} seconds"))
                print(f"El script {self.varScriptExecute} finish to code return {proc.returncode}.")
        except Exception as e:
            elapsed_time = time.time() - start_time
            self.varTreeview.item(self.varProcessId, values=(self.varTreeview.item(self.varProcessId)['values'][0], 
                                                        self.varScriptExecute, 
                                                        "Failed", 
                                                        f"{elapsed_time:.2f} seconds"))
            self.varConsoleOutput.insert(tk.END, f"Failed executed script: {e}\n")
            self.varConsoleOutput.see(tk.END)
            print(f"Error to ejecute script: {e}")

    def main(self):
        thread = threading.Thread(target=self.execute_process)
        thread.start()


class AplicacionConMenu:
    def __init__(self, root, varPathJson, varPathVenv, varScriptsPath):
        self.root = root
        self.varPathJson = varPathJson
        self.varPathVenv = varPathVenv
        self.varScriptsPath = varScriptsPath
        self.root.title("KRESTONSKY")
        self.root.geometry("1200x500")

        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.right_frame = tk.Frame(self.root, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.top_right_frame = tk.Frame(self.right_frame, height=150)
        self.top_right_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.bottom_right_frame = tk.Frame(self.right_frame)
        self.bottom_right_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.menu_bar = tk.Menu(self.left_frame)
        with open(self.varPathJson, 'r') as file:
            args = json.load(file)
        for menuapp, dictwo in args.items():
            archivo_menu = tk.Menu(self.menu_bar, tearoff=0)
            for submenuapp, optionapp in dictwo.items():
                submenu = tk.Menu(archivo_menu, tearoff=0)
                for option in optionapp:
                    for label, command in option.items():
                        submenu.add_command(label=label, command=lambda lbl=label, cmd=command: self.ejecutar_comando(lbl, cmd))
                archivo_menu.add_cascade(label=submenuapp, menu=submenu)
            self.menu_bar.add_cascade(label=menuapp, menu=archivo_menu)
        self.root.config(menu=self.menu_bar)

        self.style_treeview()
        self.tree = ttk.Treeview(self.left_frame, style="Custom.Treeview")
        self.tree.pack(expand=True, fill=tk.BOTH)
        self.columns_to_app()

        self.label_cpu = tk.Label(self.top_right_frame, text="CPU: ", font=("Consola", 10))
        self.label_cpu.pack(pady=10)
        self.label_ram = tk.Label(self.top_right_frame, text="RAM: ", font=("Consola", 10))
        self.label_ram.pack(pady=10)
        self.label_disk = tk.Label(self.top_right_frame, text="DISK: ", font=("Consola", 10))
        self.label_disk.pack(pady=10)
        self.label_network = tk.Label(self.top_right_frame, text="NETWORK: ", font=("Consola", 10))
        self.label_network.pack(pady=10)

        self.varConsoleOutput = tk.Text(self.bottom_right_frame, height=10, wrap=tk.WORD, bg="black", fg="white", font=("Helvetica", 10))
        self.varConsoleOutput.pack(fill=tk.BOTH, expand=True)
        sys.stdout = TextRedirector(self.varConsoleOutput)
        self.update_system_info()

    def style_treeview(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Custom.Treeview.Heading", background="#4a4a4a", foreground="white", font=("Helvetica", 10, "bold"))
        style.configure("Custom.Treeview", background="grey", foreground="white", fieldbackground="grey")

    def columns_to_app(self):
        self.tree["columns"] = ("Process", "Script Name", "Status", "Elapsed Time")
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("Process", anchor=tk.W, width=150)
        self.tree.column("Script Name", anchor=tk.W, width=150)
        self.tree.column("Status", anchor=tk.W, width=100)
        self.tree.column("Elapsed Time", anchor=tk.W, width=120)
        self.tree.heading("Process", text="Process", anchor=tk.W)
        self.tree.heading("Script Name", text="Script Name", anchor=tk.W)
        self.tree.heading("Status", text="Status", anchor=tk.W)
        self.tree.heading("Elapsed Time", text="Elapsed Time", anchor=tk.W)

    def ejecutar_comando(self, label, command):
        varProcessId = self.tree.insert("", "end", values=(label, command, "In Progress", "Calculating..."))
        script_execute = FunctionExecuter(self.varPathVenv, self.varScriptsPath, command, self.tree, varProcessId, self.varConsoleOutput)
        script_execute.main()

    def update_system_info(self):
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        net_io = psutil.net_io_counters()
        
        self.label_cpu.config(text=f"CPU: {cpu_percent}%")
        self.label_ram.config(text=f"RAM: {ram_percent}%")
        self.label_disk.config(text=f"DISK: {disk_percent}%")
        self.label_network.config(text=f"NET SENT: {net_io.bytes_sent / (1024 * 1024):.2f} MB, "
                                       f"RECEIVED: {net_io.bytes_recv / (1024 * 1024):.2f} MB")
        self.root.after(1000, self.update_system_info)


class TextRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, text):
        self.text_widget.insert(tk.END, text)
        self.text_widget.see(tk.END)

    def flush(self):
        pass

#%% Use class

if __name__ == "__main__":
    root = tk.Tk()
    varPathJson = nd.funJoinThreeDic(nd.funDicOneBack(), 'data', 'json', 'menu_submenu_commandito.json')
    varPathVenv = os.path.expanduser('~\Command_Center\claro_r4')
    varScriptsPath = nd.funDicCurrent()
    app = AplicacionConMenu(root, varPathJson, varPathVenv, varScriptsPath)
    root.mainloop()
