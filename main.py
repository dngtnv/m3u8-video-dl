import tkinter as tk
import customtkinter as ctk
import os
import subprocess
from tkinter import filedialog
import threading
import signal
from pathlib import Path


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
        master.geometry("540x490")
        # create grid system
        # Setting equal width for the four columns
        master.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")

        master.resizable(False, False)
        master.iconbitmap(r"D:\Playground\m3u8-dl\octopus_logo.ico")
        master.title("M3U8 Downloader - dngtnv")

        self.app_label = ctk.CTkLabel(
            master, text="Octopuss", font=("Arial", 28), pady=5,
        )

        self.input_frame = ctk.CTkFrame(master)
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.columnconfigure(1, weight=6)

        # Create a text box for the user to enter the m3u8 link
        self.link_label = ctk.CTkLabel(
            self.input_frame,
            text="Enter m3u8 url",
            font=("Arial", 14),
        )
        self.link = ctk.CTkEntry(
            self.input_frame,
            height=38,
            font=("Arial", 14),
            placeholder_text="https//_.m3u8",
        )

        # Create a text box for the user to enter the file name
        self.file_label = ctk.CTkLabel(
            self.input_frame,
            text="Enter file name",
            font=("Arial", 14),
        )
        # Enter output name
        self.input_file_name = ctk.CTkEntry(
            self.input_frame,
            height=38,
            font=("Arial", 14),
            placeholder_text="e.g: name_01",
        )

        # Create a label to display the download status
        self.status_label = ctk.CTkLabel(master, text="")

        # Show selected path
        self.file_path = ctk.CTkTextbox(
            master, height=38, font=("Arial", 14), activate_scrollbars=False
        )
        self.file_path.configure(state="disabled")

        # Browser folder
        self.select_folder_button = ctk.CTkButton(
            master,
            text="Select folder",
            height=38,
            font=("Arial", 14),
            command=self.select_output_folder,
        )

        # Create a "Start Download" button
        self.download_button = ctk.CTkButton(
            master,
            text="Download",
            height=38,
            font=("Arial", 14),
            command=self.start_download,
        )

        # Create a "Stop" button
        self.stop_button = ctk.CTkButton(
            master,
            text="Stop",
            height=38,
            font=("Arial", 14),
            command=self.stop_download,
        )
        # Initially disable the Stop button
        self.stop_button.configure(state="disabled")

        self.log_text = ctk.CTkTextbox(master, text_color='#20C20E', width=50, height=200)

        # layout widgets
        self.app_label.grid(row=0, column=0, columnspan=5, sticky="nesw")
        self.input_frame.grid(row=1, column=0, columnspan=5, sticky="nesw")
        #-----input frame------#
        self.link_label.grid(row=0, column=0, sticky="ew")
        self.link.grid(row=0, column=1, sticky="ew")
        self.file_label.grid(row=1, column=0, sticky="ew")
        self.input_file_name.grid(row=1, column=1, sticky="ew")
        #-----main frame-------#
        self.status_label.grid(row=3, column=0, columnspan=4, sticky="nesw")
        self.file_path.grid(row=4, column=0, columnspan=3, sticky="ew")
        self.select_folder_button.grid(row=4, column=3, sticky="WE")
        self.download_button.grid(row=5, column=0, columnspan=2, sticky="ew")
        self.stop_button.grid(row=5, column=2, columnspan=2, sticky="ew")
        self.log_text.grid(row=6, column=0, columnspan=4, sticky="nesw")

        for widget in self.input_frame.winfo_children():
            widget.grid_configure(pady=5, padx=10)

        for widget in master.winfo_children():
            widget.grid_configure(pady=5, padx=10)

        # def reset_focus():
        #     x,y = master.winfo_pointerxy()
        #     widget = master.winfo_containing(x,y)
        #     if (widget == self.link) != False :
        #         print(widget)
        #         print(self.link)
        #         master.focus()
        # master.bind("<Button-1>", reset_focus)

    def select_output_folder(self):
        self.output_folder = filedialog.askdirectory()
        self.file_path.configure(state="normal")  # configure textbox to be read-only
        self.file_path.delete("0.0", "end")
        self.file_path.insert("0.0", f"{self.output_folder}")
        self.file_path.configure(state="disabled")

    def start_download(self):
        threading.Thread(target=self.download).start()

    def download(self):
        if self.log_text.get(tk.END, "end"):
            self.log_text.delete(tk.END, "end")
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
                    text="Please insert a valid link and file name!",
                    text_color="#C73E1D",
                )
                break

            # Construct the ffmpeg command to download the video file
            output_file = os.path.join(self.output_folder, f"{file_name}.mp4")
            # Check if the file already exists
            if Path(output_file).is_file():
                # Update the status label
                self.status_label.configure(
                    text="The file is already exists!", text_color="orange"
                )
                break

            command = f'ffmpeg -hide_banner -headers "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36)" -n -i {link} -c copy -bsf:a aac_adtstoasc -c:v copy {output_file}'
            # Start the ffmpeg process to download the video file
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=True,
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
                    break
                if output == b"" and self.process.poll() is not None:
                    # finished the download
                    # self.stop_flags = True
                    # Update the status label
                    self.status_label.configure(
                        text="Download Complete!", text_color="green"
                    )
                    break
                if output:
                    self.log_text.insert(
                        tk.END, output.decode("utf-8")
                    )  # reads the output from the pipe line by line and appends it to the Text widget
                    self.log_text.see(
                        tk.END
                    )  # stays scrolled to the end to show the most recent output
                    root.update_idletasks()  # allows the GUI to update in real-time.

    def stop_download(self):
        # Update the status label
        self.status_label.configure(text="Download stopped.", text_color="orange")
        # Reset the UI
        self.download_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.select_folder_button.configure(state="normal")

        self.stop_flags = True
        try:
            # Terminate the process gracefully
            # os.kill(self.process.pid, signal.CTRL_BREAK_EVENT)
            # subprocess.run("TASKKILL /PID {pid} /T".format(pid=self.process.pid))
            self.process.send_signal(signal.CTRL_BREAK_EVENT)
            # self.process.terminate()
            # self.process.wait()  # Wait for termination
        except KeyboardInterrupt:
            # Handle any exceptions if the termination fails
            pass


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
