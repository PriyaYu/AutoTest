import os
import subprocess
import time

def bring_terminal_to_front():
    try:
        pid = os.getpid()
        while pid > 1:
            comm = subprocess.check_output(f"ps -p {pid} -o comm=", shell=True).decode().strip()
            if ".app/Contents/" in comm:
                app_path = comm.split('.app/')[0]
                app_name = app_path.split('/')[-1]
                if "Code" in app_name or "Code Helper" in app_name:
                    app_name = "Visual Studio Code"
                elif "iTerm" in app_name:
                    app_name = "iTerm"
                elif "Terminal" in app_name:
                    app_name = "Terminal"
                
                print(f"Activating: {app_name}")
                os.system(f"osascript -e 'tell application \"{app_name}\" to activate'")
                return
            pid = int(subprocess.check_output(f"ps -p {pid} -o ppid=", shell=True).decode().strip())
    except Exception as e:
        print("Error:", e)

bring_terminal_to_front()
