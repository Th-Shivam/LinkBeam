import customtkinter
import socket
from tkinter import filedialog
import os
import threading

# --- App Settings ---
APP_NAME = "LinkBeam"
WINDOW_SIZE = "450x550"
THEME = "dark"  # or "light"
ACCENT_COLOR = "blue"  # or "green", etc.
PORT = 12345
BUFFER_SIZE = 4096 * 4 # Increased buffer for speed

# --- Main Application Class ---
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Setup ---
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.resizable(False, False)
        customtkinter.set_appearance_mode(THEME)
        customtkinter.set_default_color_theme(ACCENT_COLOR)

        # --- State Variables ---
        self.file_to_send = ""
        self.is_receiving = False

        # --- Main Frame ---
        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # --- Title ---
        self.title_label = customtkinter.CTkLabel(self.main_frame, text=APP_NAME, font=customtkinter.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=10)

        # --- Mode Switcher ---
        self.mode_switcher = customtkinter.CTkSegmentedButton(self.main_frame, values=["Send", "Receive"], command=self.switch_mode)
        self.mode_switcher.pack(pady=10, padx=10, fill="x")
        self.mode_switcher.set("Send")

        # --- Send Frame ---
        self.send_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.send_frame.pack(fill="both", expand=True)

        self.select_file_button = customtkinter.CTkButton(self.send_frame, text="Select File", command=self.select_file)
        self.select_file_button.pack(pady=20)

        self.selected_file_label = customtkinter.CTkLabel(self.send_frame, text="No file selected", text_color="gray", wraplength=350)
        self.selected_file_label.pack(pady=5)

        self.ip_entry = customtkinter.CTkEntry(self.send_frame, placeholder_text="Enter Receiver's IP Address")
        self.ip_entry.pack(pady=20, padx=20, fill="x")

        self.send_button = customtkinter.CTkButton(self.send_frame, text="Send File", command=self.send_file_thread)
        self.send_button.pack(pady=10, side="bottom")


        # --- Receive Frame ---
        self.receive_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        # The receive_frame is packed when switching mode

        self.receive_status_label = customtkinter.CTkLabel(self.receive_frame, text="Ready to Receive Files", font=customtkinter.CTkFont(size=16))
        self.receive_status_label.pack(pady=20, padx=20)

        self.my_ip_label = customtkinter.CTkLabel(self.receive_frame, text=f"Your IP: {self.get_my_ip()}", text_color="gray")
        self.my_ip_label.pack(pady=10)

        # --- Progress & Status ---
        self.progress_bar = customtkinter.CTkProgressBar(self.main_frame, orientation="horizontal")
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(self.main_frame, text="", text_color="gray")


    def switch_mode(self, mode):
        """ Handles switching between Send and Receive modes """
        if mode == "Send":
            self.receive_frame.pack_forget()
            self.send_frame.pack(fill="both", expand=True)
            self.stop_receiving()
        else: # Receive mode
            self.send_frame.pack_forget()
            self.receive_frame.pack(fill="both", expand=True)
            self.start_receiving_thread()

    def select_file(self):
        """ Opens a dialog to select a file to send """
        self.file_to_send = filedialog.askopenfilename()
        if self.file_to_send:
            filename = os.path.basename(self.file_to_send)
            self.selected_file_label.configure(text=filename, text_color="white")
        else:
            self.selected_file_label.configure(text="No file selected", text_color="gray")

    def get_my_ip(self):
        """ Gets the local IP address of the machine """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    # --- Send Logic ---
    def send_file_thread(self):
        """ Starts the file sending process in a new thread """
        if not self.file_to_send:
            self.status_label.pack(pady=10, side="bottom", fill="x")
            self.status_label.configure(text="Please select a file first")
            return
        receiver_ip = self.ip_entry.get()
        if not receiver_ip:
            self.status_label.pack(pady=10, side="bottom", fill="x")
            self.status_label.configure(text="Please enter the receiver's IP")
            return

        threading.Thread(target=self.send_file, args=(receiver_ip,)).start()


    def send_file(self, receiver_ip):
        """ Handles the logic of sending a file """
        try:
            self.send_button.configure(state="disabled")
            self.status_label.pack(pady=10, side="bottom", fill="x")
            self.progress_bar.pack(pady=10, padx=20, fill="x")
            self.progress_bar.set(0)
            self.status_label.configure(text=f"Connecting to {receiver_ip}...")

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((receiver_ip, PORT))

            # Send file info
            filename = os.path.basename(self.file_to_send)
            filesize = os.path.getsize(self.file_to_send)
            s.send(f"{filename}|{filesize}".encode())

            # Wait for receiver's confirmation
            s.recv(BUFFER_SIZE)

            # Send file data
            sent_total = 0
            with open(self.file_to_send, "rb") as f:
                while True:
                    bytes_read = f.read(BUFFER_SIZE)
                    if not bytes_read:
                        break # file transfer is done
                    s.sendall(bytes_read)
                    sent_total += len(bytes_read)
                    progress = (sent_total / filesize)
                    self.progress_bar.set(progress)
                    self.status_label.configure(text=f"Sending... {int(progress*100)}%")

            self.status_label.configure(text="File sent successfully!", text_color="green")

        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="red")
        finally:
            s.close()
            self.send_button.configure(state="normal")
            self.progress_bar.after(3000, self.progress_bar.pack_forget)
            self.status_label.after(3000, lambda: self.status_label.configure(text=""))

    # --- Receive Logic ---
    def start_receiving_thread(self):
        """ Starts the file receiving listener in a new thread """
        if not self.is_receiving:
            self.is_receiving = True
            threading.Thread(target=self.receive_files, daemon=True).start()

    def stop_receiving(self):
        self.is_receiving = False
        # This is a simplified stop. A more robust implementation might need to
        # forcefully close the listening socket if it's blocked on accept().
        self.receive_status_label.configure(text="Receiver stopped.")

    def receive_files(self):
        """ Listens for and receives incoming files """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_socket.bind(('', PORT))
            server_socket.listen(1)
            # This allows the socket to be non-blocking
            server_socket.settimeout(1)

            self.receive_status_label.configure(text="Listening for incoming files...")

            while self.is_receiving:
                try:
                    conn, addr = server_socket.accept()
                    with conn:
                        self.status_label.pack(pady=10, side="bottom", fill="x")
                        self.progress_bar.pack(pady=10, padx=20, fill="x")
                        self.progress_bar.set(0)
                        self.status_label.configure(text=f"Connection from {addr[0]}")

                        # Receive file info
                        received_data = conn.recv(BUFFER_SIZE).decode()
                        filename, filesize = received_data.split('|')
                        filesize = int(filesize)
                        
                        # Tell sender we're ready
                        conn.send("OK".encode())

                        # Create a 'downloads' directory if it doesn't exist
                        if not os.path.exists('downloads'):
                            os.makedirs('downloads')
                        
                        filename = os.path.join('downloads', os.path.basename(filename))

                        # Receive file data
                        received_total = 0
                        with open(filename, "wb") as f:
                            while received_total < filesize:
                                bytes_read = conn.recv(BUFFER_SIZE)
                                if not bytes_read:
                                    break
                                f.write(bytes_read)
                                received_total += len(bytes_read)
                                progress = (received_total / filesize)
                                self.progress_bar.set(progress)
                                self.status_label.configure(text=f"Receiving... {int(progress*100)}%")

                        self.status_label.configure(text=f"File '{os.path.basename(filename)}' received!", text_color="green")
                except socket.timeout:
                    # Just loop again to check the self.is_receiving flag
                    continue
                except Exception as e:
                    self.status_label.configure(text=f"Error: {e}", text_color="red")
                finally:
                    # Clean up UI for the next transfer
                    self.progress_bar.after(3000, self.progress_bar.pack_forget)
                    self.status_label.after(3000, lambda: self.status_label.configure(text=""))
                    self.receive_status_label.configure(text="Listening for incoming files...")


        except Exception as e:
            # This might catch errors like "address already in use"
             self.receive_status_label.configure(text=f"Listener Error: {e}", text_color="red")
        finally:
            server_socket.close()
            # If the loop is exited, we are no longer receiving
            self.is_receiving = False
            # Update UI if we are still in receive mode
            if self.mode_switcher.get() == "Receive":
                 self.receive_status_label.configure(text="Receiver stopped. Restart app if needed.", text_color="orange")



if __name__ == "__main__":
    app = App()
    app.mainloop()
