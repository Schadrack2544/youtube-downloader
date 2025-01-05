import tkinter as tk
from tkinter import ttk, messagebox
from pytubefix import YouTube
from threading import Thread
from pathlib import Path
import os
import subprocess



def start_download():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube link")
        return

    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video_stream = yt.streams.filter(adaptive=True, file_extension="mp4", only_video=True).order_by("resolution").desc().first()
        audio_stream = yt.streams.filter(adaptive=True, file_extension="mp4", only_audio=True).first()

        if not video_stream or not audio_stream:
            messagebox.showerror("Error", "Unable to find suitable video or audio streams")
            return

        progress_label.config(text="Downloading video...")
        progress_bar['value'] = 0

        # Run download in separate threads
        Thread(target=download_and_merge, args=(video_stream, audio_stream, yt.title)).start()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch video. Error: {str(e)}")


def download_and_merge(video_stream, audio_stream, title):
    try:
        video_file = f"{title}_video.mp4"
        audio_file = f"{title}_audio.mp4"
        output_file = f"{title}.mp4"
        downloads_folder = str(Path.home() / "Downloads")
        video_stream.download(output_path=downloads_folder, filename=video_file)
        progress_label.config(text="Downloading audio...")
        audio_stream.download(output_path=downloads_folder, filename=audio_file)

        # Merge video and audio using FFmpeg
        progress_label.config(text="Merging video and audio...")
        command = f'ffmpeg -i "{os.path.join(downloads_folder, video_file)}" -i "{os.path.join(downloads_folder, audio_file)}" -c:v copy -c:a aac -strict experimental "{os.path.join(downloads_folder, output_file)}" -y'

        subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Clean up temporary files
        os.remove(os.path.join(downloads_folder, video_file))
        os.remove(os.path.join(downloads_folder, audio_file))

        progress_label.config(text="Download Complete!")
        messagebox.showinfo("Success", f"Video downloaded successfully: {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download or merge video. Error: {str(e)}")

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    downloaded = total_size - bytes_remaining

    progress_percent = (downloaded / total_size) * 100

    # Update progress bar and label
    progress_bar['value'] = progress_percent
    progress_label.config(text=f"Downloaded: {progress_percent:.2f}%")

# GUI Setup
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("500x250")
root.resizable(False, False)

# Styles
style = ttk.Style()
style.configure("TButton", font=("Arial", 12))
style.configure("TLabel", font=("Arial", 12))
style.configure("TEntry", font=("Arial", 12))

# Widgets
url_label = ttk.Label(root, text="Enter YouTube Link:")
url_label.pack(pady=10)

url_entry = ttk.Entry(root, width=50)
url_entry.pack(pady=5)

start_button = ttk.Button(root, text="Start Download", command=start_download)
start_button.pack(pady=15)

progress_label = ttk.Label(root, text="Progress: Not started")
progress_label.pack(pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

# Run the application
root.mainloop()
