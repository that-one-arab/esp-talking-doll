from dotenv import load_dotenv

# Load local .env file
load_dotenv()

from fastapi.responses import FileResponse
from fastapi import FastAPI, Request
import time
from util import get_messages, create_dir, get_current_datetime, transcribe_audio, write_text_to_local, chat_complete, get_tts, write_audio_to_local, remove_emojis_emoticons
import os

app = FastAPI()

messages = get_messages()

session_dir = create_dir(f'{dir}/input.txt')

@app.get("/hello")
def hello(request: Request):
    return {"Hello": "World"}

@app.post("/test")
async def test(request: Request):
    body = b''
    chunk_count = 0
    async for chunk in request.stream():
        chunk_count = chunk_count + 1
        body += chunk

    write_audio_to_local(body, "./test.wav")

    response_file = "./media/test-output.wav"

    file_size = os.path.getsize(response_file)
    headers = {'Content-Length': str(file_size)}
    return FileResponse(response_file, media_type='application/octet-stream', filename="output.wav", headers=headers)

@app.post("/talk")
async def talk(request: Request):
    start_time = time.time()  # Log how long the request takes

    body = b''
    async for chunk in request.stream():
        body += chunk

    dir = create_dir("./media/" + get_current_datetime())
    write_audio_to_local(body, f'{dir}/input.wav')
    audio_file= open(f'{dir}/input.wav', "rb")
    user_transcription = transcribe_audio(audio_file)
    messages.append(({"role": "user", "content": user_transcription}))
    response_text = chat_complete(messages)
    # filter out emoticons and emojis from text
    response_text = remove_emojis_emoticons(response_text)
    messages.append(({"role": "assistant", "content": response_text}))
    response_to_speech = get_tts(response_text)

    end_time = time.time()

    write_text_to_local(user_transcription, f'{dir}/input.txt')
    write_text_to_local(response_text, f'{dir}/output.txt')
    write_text_to_local(
        f"Elapsed time: {end_time - start_time} seconds", f'{dir}/log.txt')
    write_audio_to_local(response_to_speech, f'{dir}/output.wav')

    file_size = os.path.getsize(f'{dir}/output.wav')
    headers = {'Content-Length': str(file_size)}
    return FileResponse(f'{dir}/output.wav', media_type='application/octet-stream', filename="output.wav", headers=headers)
