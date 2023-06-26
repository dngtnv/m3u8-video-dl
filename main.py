import tkinter as tk
import customtkinter as ctk
import os
import subprocess
from subprocess import CREATE_NO_WINDOW
from tkinter import filedialog
import threading
import signal
from pathlib import Path
from PIL import ImageTk


class App:
    def __init__(self, master):
        # init vars
        self.process = None
        self.output_folder = "."
        self.stop_flags = False
        # System settings
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # app frame
        self.master = master
        master.geometry("540x480")
        # create grid system
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        master.columnconfigure(3, weight=1)
        master.columnconfigure(4, weight=1)

        master.resizable(False, False)
        master.iconbitmap(r"D:\Playground\m3u8-dl\octopus_logo.ico")
        # master.iconphoto(False, tk.PhotoImage(file="octopus_2.png"))
        master.title("M3U8 Downloader - dngtnv")

        self.app_label = ctk.CTkLabel(
            master, text="M3U8 DL", font=("Helventica Neue", 24)
        )

        # Create a text box for the user to enter the m3u8 link
        self.link_label = ctk.CTkLabel(
            master,
            text="Enter m3u8 link:",
            font=("Helventica Neue", 14),
        )
        self.link = ctk.CTkEntry(
            master,
            height=38,
            font=("Helventica Neue", 14),
            placeholder_text="https//_.m3u8",
        )

        # Create a text box for the user to enter the file name
        self.file_label = ctk.CTkLabel(
            master,
            text="Enter file name:",
            font=("Helventica Neue", 14),
        )
        # Enter output name
        self.input_file_name = ctk.CTkEntry(
            master,
            height=38,
            font=("Helventica Neue", 14),
            placeholder_text="Enter file name",
        )

        # Create a label to display the download status
        self.status_label = ctk.CTkLabel(master, text="")

        # Show selected path
        self.file_path = ctk.CTkTextbox(
            master, height=38, font=("Helventica Neue", 14), activate_scrollbars=False
        )

        # Browser folder
        self.select_folder_button = ctk.CTkButton(
            master,
            text="Select folder",
            height=38,
            command=self.select_output_folder,
        )

        # Create a "Start Download" button
        self.download_button = ctk.CTkButton(
            master,
            text="Download",
            height=38,
            command=self.start_download,
        )

        # Create a "Stop" button
        self.stop_button = ctk.CTkButton(
            master,
            text="Stop/Restart",
            height=38,
            command=self.stop_download,
        )
        # Initially disable the Stop button
        self.stop_button.configure(state="disabled")

        self.log_text = ctk.CTkTextbox(master, width=50, height=200)

        # layout widgets
        self.app_label.grid(row=0, column=0, columnspan=5, sticky="nesw")
        self.link_label.grid(row=1, column=0, sticky="ew")
        self.link.grid(row=1, column=1, columnspan=4, sticky="ew")
        self.file_label.grid(row=2, column=0, sticky="ew")
        self.input_file_name.grid(row=2, column=1, columnspan=4, sticky="ew")
        self.status_label.grid(row=3, column=0, columnspan=5, sticky="nesw")
        self.file_path.grid(row=4, column=0, columnspan=4, sticky="ew")
        self.select_folder_button.grid(row=4, column=4, sticky="WE")
        self.download_button.grid(row=5, column=0, columnspan=3, sticky="ew")
        self.stop_button.grid(row=5, column=3, columnspan=2, sticky="ew")
        self.log_text.grid(row=6, column=0, columnspan=5, sticky="nesw")

        for widget in master.winfo_children():
            widget.grid_configure(padx=10, pady=5)

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.file_path.insert("0.0", f"{self.output_folder}")
        self.file_path.configure(state="disabled")

    def start_download(self):
        threading.Thread(target=self.download).start()

    def download(self):
        # Update the status label
        self.status_label.configure(text="")
        self.stop_flags = False
        while not self.stop_flags:
            # Get the link entered by the user
            link = self.link.get().strip()
            file_name = self.input_file_name.get().strip()
            if len(link) == 0 or len(file_name) == 0:
                # Update the status label
                self.status_label.configure(
                    text="⚠ Please insert a valid link and file name!",
                    text_color="#C73E1D",
                )
                break
            else:
                # Construct the ffmpeg command to download the video file
                output_file = os.path.join(self.output_folder, f"{file_name}.mp4")
                # Check exists file
                if Path(output_file).is_file():
                    # If the file is exists
                    # Update the status label
                    self.status_label.configure(
                        text="The file is already exists!", text_color="orange"
                    )
                    break
                else:
                    command = f'ffmpeg -hide_banner -headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36)" -n -i {link} -c copy -bsf:a aac_adtstoasc -c:v copy {output_file}'
                    # Start the ffmpeg process to download the video file
                    self.process = subprocess.Popen(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        # creationflags=CREATE_NO_WINDOW,
                        shell=True,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                    )

                    # Disable the start download button and enable the stop download button
                    self.download_button.configure(state="disabled")
                    self.stop_button.configure(state="normal")
                    self.select_folder_button.configure(state="disabled")

                    while True:
                        output = self.process.stdout.readline()
                        if "No such file or directory" in output.decode("utf-8"):
                            # Update the status label
                            self.status_label.configure(
                                text="The link is invalid!", text_color="#C73E1D"
                            )
                            return
                        if output == b"" and self.process.poll() is not None:
                            break
                        if output:
                            self.log_text.insert(
                                tk.END, output.decode("utf-8")
                            )  # reads the output from the pipe line by line and appends it to the Text widget
                            self.log_text.see(
                                tk.END
                            )  # stays scrolled to the end to show the most recent output
                            root.update_idletasks()  # allows the GUI to update in real-time.

                    # Update the status label
                    self.status_label.configure(
                        text="Download Complete!", text_color="green"
                    )

    def stop_download(self):
        self.stop_flags = True
        # Send the signal to all the process groups
        os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)  # signal.CTRL_BREAK_EVENT
        # subprocess.run(["taskkill", "/F", "/PID", str(self.process.pid)])
        # if self.process and isinstance(self.process, subprocess.Popen):
        #     self.process.terminate()
        #     self.process.wait()

        # Reset the UI
        self.download_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.select_folder_button.configure(state="normal")
        self.log_text.delete(tk.END)

        # Update the status label
        self.status_label.configure(text="Download stopped.", text_color="orange")


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
