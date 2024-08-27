import tekore as tk
from openai import OpenAI
import tiktoken
import json
import time
from dotenv import load_dotenv
import jinja2
import csv

load_dotenv()

SYSTEM_MSG = "system-message.txt"
GENRES = "genres.txt"

def get_playlist_titles(spotify, url):
    playlist_id = url.split("playlist/")[1].split('?')[0]
    playlist = spotify.playlist(playlist_id)
    tracks = playlist.tracks
    songs = []

    while tracks:
        songs.extend([(track.track.id, track.track.name, [x.name for x in track.track.artists]) for track in tracks.items if track.track is not None])
        for track in tracks.items:
            if track.track is None:
                continue

        tracks = spotify.next(tracks)
    
    return songs


def get_classify_message(songs):
    message = "Classify each of the following songs:\n"
    for song in songs:
        message += f"{song[1]} by {', '.join(song[2])}\n"
    return message

# Load system message and bins

with open(GENRES, 'r') as f:
    reader = csv.reader(f)
    genres = [x.strip().lower() for x in list(reader)[0]]

jinja = jinja2.Environment()

with open(SYSTEM_MSG, 'r') as f:
    system_message = jinja.from_string(f.read()).render(genres = genres)

# Initiate spotify and openai clients

token = tk.request_client_token("ebaedd8b26d04fa7a7bb1ff062eee318", "89a59af718b44419aebad2b618f63309")
sp = tk.Spotify()
client = OpenAI()

def classify_playlist(url):
    with sp.token_as(token):
        songs = get_playlist_titles(sp, url)

        start = time.time()
        completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_format = { "type": "json_object" },
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": get_classify_message(songs)}])
        end = time.time()

        out = json.loads(completion.choices[0].message.content)
        print(out)
        # print(completion.choices[0].message.content)
        print(f"Time: {end - start} seconds")

classify_playlist("https://open.spotify.com/playlist/37i9dQZEVXbLp5XoPON0wI?si=74c1bbc1b9584f6a")