import socket
import subprocess
import time
import tkinter as tk
from tkinter import ttk
import threading
import ctypes
import sys
import datetime

def run_as_admin():
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def set_system_date(new_date):
    try:
        # doi format cho phu hop voi may client
        cmd = f"date {new_date.strftime('%m-%d-%Y')}"
        subprocess.call(cmd, shell=True)
        print("System time updated successfully.")
    except Exception as e:
        print(f"Error updating system time: {e}")

def set_system_time(new_time):
    try:
        # doi format cho phu hop voi may client
        cmd = f"time {new_time.strftime('%H:%M:%S')}"
        subprocess.call(cmd, shell=True)
        print("System time updated successfully.")
    except Exception as e:
        print(f"Error updating system time: {e}")

if run_as_admin():
    window_screen = tk.Tk()
    window_screen.title("Server Time Sync")
    window_screen.geometry('720x420')
    window_screen.resizable(False, False)

    label_1 = ttk.Label(master=window_screen, text="CLIENT LOG", font="Time 12 bold", background="blue", foreground="white",
                        width=50, anchor="center", padding=(0, 10))
    label_1.place(x=265, y=0)

    text_1 = tk.Text(window_screen, width=64, height=24, border=2, font="Time 9", relief=tk.SOLID)
    text_1.place(x=265, y=44)
    text_1.insert(tk.END, ">>Time sync server!\n")
    text_1.config(state=tk.DISABLED)

    frame_1 = tk.Frame(window_screen, width=265, height=420, background="#ff794d")
    frame_1.place(x=0, y=0)

    button_1 = tk.Button(frame_1, text="CONNECT SERVER", width=20, height=1, font="Time 11 bold", border=1, relief=tk.SOLID)
    button_1.place(x=30, y=30)

    button_2 = tk.Button(frame_1, text="CLEAR LOG", width=20, height=1, font="Time 11 bold", border=1, relief=tk.SOLID)
    button_2.place(x=30, y=100)


    def start_client():
        # Create a client socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        server_address = ('192.168.1.224', 12345)  # Change the address and port to match the server
        try:
            client_socket.connect(server_address)
            text_1.config(state=tk.NORMAL)
            text_1.insert(tk.END, ">>Connect server SUCCESSFUL\n")
            text_1.config(state=tk.DISABLED)
        except OSError:
            text_1.config(state=tk.NORMAL)
            text_1.insert(tk.END, ">>Connect server FAIL\n")
            text_1.config(state=tk.DISABLED)
        try:
            while True:
                # Receive a message from the server
                response = client_socket.recv(1024)
                text_response = response.decode('utf-8')
                if 'A' in text_response:
                    text_1.config(state=tk.NORMAL)
                    text_1.insert(tk.END, ">>Accept request time sysnc from server\n")
                    server_time = text_response[:-1]
                    client_time = datetime.datetime.now()

                    server_time = datetime.datetime.strptime(server_time, "%m-%d-%Y %H:%M:%S")
                    time_dif = client_time - server_time
                    totalSeconds = int(time_dif.total_seconds())
                    message = str(totalSeconds)
                    client_socket.send(message.encode('utf-8'))

                    client_time = client_time.strftime('%m-%d-%Y %H:%M:%S')

                    text_1.insert(tk.END, f'server time is {server_time}, client time is {client_time}\n')
                    text_1.insert(tk.END,f'Total seconds difference is {totalSeconds}\n')
                    text_1.config(state=tk.DISABLED)
                elif 'B' in text_response:
                    text_1.config(state=tk.NORMAL)
                    server_time = text_response[:-1]
                    text_1.insert(tk.END, f'Server time after change is {server_time} seconds\n')
                    server_time = datetime.datetime.strptime(server_time, '%m-%d-%Y %H:%M:%S')
                    client_time = datetime.datetime.now()
                    different_time = server_time - client_time
                    totalSeconds = int(different_time.total_seconds())
                    client_time = client_time + datetime.timedelta(seconds=totalSeconds)
                    set_system_time(client_time)
                    set_system_date(client_time)
                    client_time = client_time.strftime('%m-%d-%Y %H:%M:%S')
                    text_1.insert(tk.END,f'Client time after change is {client_time}, add {totalSeconds} seconds')
                    text_1.config(state=tk.DISABLED)

                    message = 'SUCCESS'
                    client_socket.send(message.encode('utf-8'))
                time.sleep(1)

        except KeyboardInterrupt:
            # Close the client socket when interrupted by the user
            text_1.config(state=tk.NORMAL)
            text_1.insert(tk.END, ">>SERVER CLOSE\n")
            text_1.config(state=tk.DISABLED)
            client_socket.close()


    def on_click_start_client():
        client_thread = threading.Thread(target=start_client)
        client_thread.start()

    def clear_log():
        text_1.config(state=tk.NORMAL)
        text_1.delete('1.0', tk.END)
        text_1.config(state=tk.DISABLED)

    button_1.config(command=on_click_start_client)
    button_2.config(command=clear_log)

    window_screen.mainloop()