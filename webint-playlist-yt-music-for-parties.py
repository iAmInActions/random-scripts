import sys
import json
import threading
import subprocess
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
queue = []
current_process = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Musikwünsche Playlist</title>
    <style>
        body {
            background-color: #121212;
            color: #00ff00;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 20px;
        }
        h1 {
            border-bottom: 2px solid #00ff00;
            display: inline-block;
            padding-bottom: 5px;
        }
        form {
            margin: 20px 0;
        }
        input {
            width: 70vw;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #00ff00;
            background-color: #222;
            color: #00ff00;
            border-radius: 5px;
        }
        button {
            padding: 10px 15px;
            font-size: 16px;
            border: none;
            background-color: #00ff00;
            color: #121212;
            cursor: pointer;
            border-radius: 5px;
            margin-left: 5px;
        }
        button:hover {
            background-color: #00cc00;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background-color: #222;
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .remove-btn {
            background-color: red;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
        }
        .remove-btn:hover {
            background-color: darkred;
        }
    </style>
</head>
<body>
    <h1>Song Hinzufügen</h1>
    <form action="/add" method="post">
        <input type="text" name="query" placeholder="Song oder YouTube URL eingeben" required>
        <button type="submit">+</button>
    </form>
    <h1>Musikwünsche Playlist</h1>
    <p>Nach Entfernen bitte neu laden</p>
    <ul>
        {% for song in queue %}
            <li>{{ song['title'] }} <button class="remove-btn" onclick="location.href='/skip'">-</button></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_video_info(query):
    if "youtube.com" in query or "youtu.be" in query:
        command = f'yt-dlp --print "%(id)s:%(title)s" --quiet --no-warnings "{query}"'
    else:
        command = f'yt-dlp "ytsearch:{query}" --print "%(id)s:%(title)s" --quiet --no-warnings'
    output = run_command(command)
    if not output:
        return None
    video_id, title = output.split(":", 1)
    audio_url = run_command(f'yt-dlp -f "bestaudio/best" --get-url --quiet --no-warnings "{video_id}"')
    return {'title': title, 'url': audio_url}

def play_next():
    global current_process
    while queue:
        song = queue[0]
        current_process = subprocess.Popen(["ffplay", "-nodisp", "-autoexit", song['url']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        current_process.wait()
        queue.pop(0)
    current_process = None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, queue=queue)

@app.route('/add', methods=['POST'])
def add_song():
    query = request.form['query']
    song = get_video_info(query)
    if song:
        queue.append(song)
        if not current_process:
            threading.Thread(target=play_next, daemon=True).start()
    return redirect('/')

@app.route('/skip')
def skip_song():
    global current_process
    if current_process:
        current_process.terminate()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)

