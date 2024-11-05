import socket
import sys
import os
import pyaudio
import threading
import argparse
import struct
import termios
import tty

# Global variable for volume control
volume = 1.0

def play_audio(audio_socket):
    """ Function to continuously play audio data received from the server """
    global volume
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paUInt8,  # 8-bit unsigned format
                    channels=1,              # Mono audio
                    rate=8000,               # 8000 Hz sample rate
                    output=True)

    try:
        while True:
            audio_chunk = audio_socket.recv(1024)
            if not audio_chunk:
                break
            # Adjust the volume of the audio chunk
            adjusted_chunk = bytes(min(int(sample * volume), 255) for sample in audio_chunk)
            stream.write(adjusted_chunk)
    except Exception as e:
        print(f"Error playing audio: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def handle_key_input(video_socket, audio_socket):
    """ Function to handle key input for quitting and volume control """
    global volume

    # Save the terminal settings
    original_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())  # Set the terminal to cbreak mode for unbuffered input

    try:
        while True:
            key = sys.stdin.read(1)  # Read a single character
            if key.lower() == 'q':   # Quit on 'q' or 'Q'
                print("Quitting...")
                video_socket.close()
                audio_socket.close()
                break
            elif key == '+':         # Increase volume on '+'
                volume = min(volume + 0.1, 2.0)  # Cap volume at 2.0
                print(f"Volume increased to {volume}")
            elif key == '-':         # Decrease volume on '-'
                volume = max(volume - 0.1, 0.0)  # Floor volume at 0.0
                print(f"Volume decreased to {volume}")
    finally:
        # Restore the terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original_settings)

def main():
    parser = argparse.ArgumentParser(description="ASCII Video Client")
    parser.add_argument("video_url", help="URL of the video to stream")
    parser.add_argument("server_ip", help="IP address of the server")
    parser.add_argument("port", type=int, help="Port number of the server")
    parser.add_argument("contrast", type=float, nargs="?", default=1.0, help="Contrast adjustment (default: 1.0)")
    parser.add_argument("brightness", type=float, nargs="?", default=0.0, help="Brightness adjustment (default: 0.0)")
    parser.add_argument("-c", "--color", action="store_true", help="Enable color mode using ANSI color codes")

    args = parser.parse_args()

    # Get the terminal size
    terminal_size = os.get_terminal_size()
    width = terminal_size.columns
    height = terminal_size.lines

    # Connect to the server for video
    try:
        video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        video_socket.connect((args.server_ip, args.port))
        print("Connected to video server successfully.")
    except Exception as e:
        print(f"Failed to connect to video server: {e}")
        return

    # Send the video URL, contrast, brightness, color flag, and terminal size
    color_mode = "1" if args.color else "0"
    video_socket.send(f"{args.video_url} {args.contrast} {args.brightness} {color_mode} {width} {height}".encode())

    # Connect to the server for audio
    try:
        audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        audio_socket.connect((args.server_ip, args.port + 1))
        print("Connected to audio server successfully.")
    except Exception as e:
        print(f"Failed to connect to audio server: {e}")
        return

    # Start a separate thread for playing audio
    audio_thread = threading.Thread(target=play_audio, args=(audio_socket,))
    audio_thread.start()

    # Handle key input in the main thread
    key_thread = threading.Thread(target=handle_key_input, args=(video_socket, audio_socket))
    key_thread.start()

    try:
        while True:
            # Receive the frame size
            frame_size_data = video_socket.recv(4)
            if not frame_size_data:
                break
            frame_size = struct.unpack("I", frame_size_data)[0]

            # Receive the full frame data
            frame_data = b""
            while len(frame_data) < frame_size:
                chunk = video_socket.recv(frame_size - len(frame_data))
                if not chunk:
                    print("Failed to receive full frame data. Connection may be closed.")
                    return
                frame_data += chunk

            # Clear the terminal and display the frame
            os.system('clear' if os.name == 'posix' else 'cls')
            print(frame_data.decode(), end="\r")
    except Exception as e:
        print(f"Error during video reception: {e}")
    finally:
        video_socket.close()
        audio_socket.close()
        audio_thread.join()
        key_thread.join()

if __name__ == "__main__":
    main()

