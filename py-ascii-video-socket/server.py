import socket
import subprocess
import numpy as np
from PIL import Image
import threading
import argparse
import struct

# Constants
FPS = 8
# ASCII_CHARS = '$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^. ' # For inverted terminals
ASCII_CHARS = ' .^",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'


# ANSI color codes
ANSI_COLORS = [
    "\033[38;5;16m",  # Black
    "\033[38;5;88m",  # Dark Red
    "\033[38;5;22m",  # Dark Green
    "\033[38;5;130m", # Brown
    "\033[38;5;19m",  # Dark Blue
    "\033[38;5;54m",  # Dark Magenta
    "\033[38;5;58m",  # Dark Cyan
    "\033[38;5;244m", # Gray
    "\033[38;5;250m", # Light Gray
    "\033[38;5;196m", # Red
    "\033[38;5;46m",  # Green
    "\033[38;5;226m", # Yellow
    "\033[38;5;21m",  # Blue
    "\033[38;5;201m", # Magenta
    "\033[38;5;51m",  # Cyan
    "\033[38;5;231m"  # White
]
RESET_COLOR = "\033[0m"

def frame_to_ascii(frame, color_mode):
    img = Image.fromarray(frame).convert("RGB").resize((frame.shape[1], frame.shape[0]))
    ascii_frame = ""
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = img.getpixel((x, y))
            gray = int(0.3 * r + 0.59 * g + 0.11 * b)
            index = min(gray // 25, len(ASCII_CHARS) - 1)  # Ensure the index is within bounds
            char = ASCII_CHARS[index]

            if color_mode:
                color_index = (r // 51) * 36 + (g // 51) * 6 + (b // 51)
                color_code = f"\033[38;5;{16 + color_index}m"
                ascii_frame += f"{color_code}{char}{RESET_COLOR}"
            else:
                ascii_frame += char
        ascii_frame += "\n"
    return ascii_frame

def process_video(url, contrast, brightness, color_mode, width, height, video_conn, sync_event):
    ffmpeg_command = [
        "ffmpeg",
        "-re",
        "-i", url,
        "-vf", f"scale={width}:{height},eq=contrast={contrast}:brightness={brightness}",
        "-r", str(FPS),
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "pipe:1"
    ]
    video_process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    frame_size = width * height * 3

    try:
        while True:
            frame_bytes = video_process.stdout.read(frame_size)
            if not frame_bytes:
                break

            frame = np.frombuffer(frame_bytes, np.uint8).reshape((height, width, 3))
            ascii_frame = frame_to_ascii(frame, color_mode)
            frame_data = ascii_frame.encode()

            # Send the frame size followed by the frame data
            video_conn.sendall(struct.pack("I", len(frame_data)) + frame_data)
            sync_event.wait(1 / FPS)
    finally:
        video_process.stdout.close()
        video_conn.close()

def process_audio(url, audio_conn, sync_event):
    ffmpeg_audio_command = [
        "ffmpeg",
        "-re",
        "-i", url,
        "-f", "wav",
        "-ar", "8000",
        "-ac", "1",
        "-acodec", "pcm_u8",
        "pipe:1"
    ]
    audio_process = subprocess.Popen(ffmpeg_audio_command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    try:
        while True:
            audio_chunk = audio_process.stdout.read(1024)
            if not audio_chunk:
                break
            try:
                audio_conn.sendall(audio_chunk)
            except BrokenPipeError:
                print("Audio connection closed by client.")
                break
            sync_event.set()
            sync_event.clear()
    finally:
        audio_process.stdout.close()
        audio_conn.close()

def handle_client(video_conn, audio_conn):
    data = video_conn.recv(1024).decode().split()
    url = data[0]
    contrast = float(data[1])
    brightness = float(data[2])
    color_mode = bool(int(data[3]))
    width = int(data[4])
    height = int(data[5])
    print(f"Received URL: {url} with contrast={contrast}, brightness={brightness}, color_mode={color_mode}, width={width}, height={height}")

    sync_event = threading.Event()
    video_thread = threading.Thread(target=process_video, args=(url, contrast, brightness, color_mode, width, height, video_conn, sync_event))
    audio_thread = threading.Thread(target=process_audio, args=(url, audio_conn, sync_event))
    video_thread.start()
    audio_thread.start()
    video_thread.join()
    audio_thread.join()

def main():
    parser = argparse.ArgumentParser(description="ASCII Video Streaming Server")
    args = parser.parse_args()

    server_socket_video = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket_video.bind(("0.0.0.0", 12345))
    server_socket_audio.bind(("0.0.0.0", 12346))
    server_socket_video.listen(5)
    server_socket_audio.listen(5)

    print("Server listening on ports 12345 (video) and 12346 (audio)")

    while True:
        video_conn, video_addr = server_socket_video.accept()
        audio_conn, audio_addr = server_socket_audio.accept()
        print(f"Connected by {video_addr} for video and {audio_addr} for audio")
        handle_client(video_conn, audio_conn)

if __name__ == "__main__":
    main()

