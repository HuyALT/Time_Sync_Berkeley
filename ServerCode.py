import tkinter as tk
from tkinter import ttk
import socket
import threading
import ctypes
import sys
import datetime
import subprocess

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
    list_client_addr = []
    list_client_socket = []
    list_different_time = []
    window_screen = tk.Tk()
    window_screen.title("Server Time Sync")
    window_screen.geometry('720x420')
    window_screen.resizable(False, False)

    label_1 = ttk.Label(master=window_screen, text="SERVER LOG", font="Time 12 bold", background="blue", foreground="white", width=50, anchor="center", padding=(0, 10))
    label_1.place(x=265, y=0)

    text_1 = tk.Text(window_screen,width=64, height=24, border=2, font="Time 9", relief=tk.SOLID)
    text_1.place(x=265, y=44)
    text_1.insert(tk.END, ">>Time sync server!\n")
    text_1.config(state=tk.DISABLED)

    frame_1 = tk.Frame(window_screen,width=265, height=420, background="#ff794d")
    frame_1.place(x=0, y=0)

    button_1 = tk.Button(frame_1, text="START SERVER", width=20, height=1, font="Time 11 bold", border=1, relief=tk.SOLID)
    button_1.place(x=30, y=30)

    button_2 = tk.Button(frame_1, text="LIST CLIENT", width=20, height=1, font="Time 11 bold", border=1, relief=tk.SOLID)
    button_2.place(x=30, y=100)

    button_3 = tk.Button(frame_1, text="TIME SYNC", width=20, height=1, font="Time 11 bold", border=1, relief=tk.SOLID)
    button_3.place(x=30, y=170)

    button_4 = tk.Button(frame_1, text="CLEAR LOG", width=20, height=1, font="Time 11 bold", border=1, relief=tk.SOLID)
    button_4.place(x=30, y=240)


    def handle_client(client_socket):
        ipaddr, port = client_socket.getsockname()
        text_1.config(state=tk.NORMAL)
        text_1.insert(tk.END, '>>Requires time synchronization\n')
        server_time = datetime.datetime.now()
        response = server_time.strftime('%m-%d-%Y %H:%M:%S')
        response = response+'A'
        client_socket.send(response.encode('utf-8'))

        request = client_socket.recv(1024)
        list_different_time.append(int(request))
        text_1.insert(tk.END, f'>>Time difference of {ipaddr} is {request} \n')
        text_1.config(state=tk.DISABLED)

    def time_avg():
        avg = 0
        for i in list_different_time:
            avg = avg+i
        avg = avg/len(list_different_time)
        server_time = datetime.datetime.now()
        server_time = server_time + datetime.timedelta(seconds=int(avg))
        text_1.config(state=tk.NORMAL)
        text_1.insert(tk.END, f'>>Average seconds is {avg}\n')
        text_1.config(state=tk.DISABLED)
        return server_time

    def time_sysnc_client(client_socket, server_time):
        ipaddr, port = client_socket.getsockname()
        server_time =  server_time.strftime('%m-%d-%Y %H:%M:%S')
        text_1.config(state=tk.NORMAL)
        text_1.insert(tk.END, f'Server time after change is {server_time}\n')

        message = server_time+'B'
        client_socket.send(message.encode('utf-8'))

        text_1.insert(tk.END, '>>Send time to client\n')
        text_1.config(state=tk.DISABLED)

        request = client_socket.recv(1024)
        text_1.config(state=tk.NORMAL)
        if not request:
            text_1.insert(tk.END, f'Client {ipaddr} update time fail\n')
        else:
            text_1.insert(tk.END, f'Client {ipaddr} update time successful\n')
        text_1.config(state=tk.DISABLED)

    def start_server():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('192.168.99.216', 12345))
        server_socket.listen(5)
        text_1.config(state=tk.NORMAL)
        text_1.insert(tk.END, ">>Server listening on 192.168.99.216:12345\n")
        text_1.config(state=tk.DISABLED)
        while True:
            # Accept a connection from a client
            client_socket, addr = server_socket.accept()
            text_1.config(state=tk.NORMAL)
            text_1.insert(tk.END, f">>Accept connect from {addr} \n")
            text_1.config(state=tk.DISABLED)
            if addr not in list_client_addr:
                list_client_addr.append(addr)

            if client_socket not in list_client_socket:
                list_client_socket.append(client_socket)


    def on_click_start_server():
        server_thread = threading.Thread(target=start_server)
        server_thread.start()

    def print_client_list():
        if list_client_addr==[]:
            text_1.config(state=tk.NORMAL)
            text_1.insert(tk.END, ">>No client connect\n")
            text_1.config(state=tk.DISABLED)
        else:
            text_1.config(state=tk.NORMAL)
            for i in list_client_addr:
                text_1.insert(tk.END,f">>{i}")
            text_1.insert(tk.END,"\n")
            text_1.config(state=tk.DISABLED)

    def time_sysnc():
        if list_client_socket==[]:
            text_1.config(state=tk.NORMAL)
            text_1.insert(tk.END, ">>No client connect\n")
            text_1.config(state=tk.DISABLED)
        else:
            for i in list_client_socket:
                handle_client(i)
            server_time = time_avg()
            set_system_time(server_time)
            set_system_date(server_time)
            for i in list_client_socket:
                time_sysnc_client(i, server_time)


    def clear_log():
        text_1.config(state=tk.NORMAL)
        text_1.delete('1.0', tk.END)
        text_1.config(state=tk.DISABLED)

    button_1.config(command=on_click_start_server)
    button_2.config(command=print_client_list)
    button_3.config(command=time_sysnc)
    button_4.config(command=clear_log)
    window_screen.mainloop()
