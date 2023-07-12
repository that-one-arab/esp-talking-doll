import openai
import re
import os
import datetime
# import tiktoken
# from google.oauth2 import service_account
from google.cloud import texttospeech

def read_text(path):
    with open(path, 'r') as file:
        return file.read()

def get_messages():
    return [
        {"role": "system", "content": read_text("./prompt.txt")},
    ]

def get_current_datetime():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d-%H-%M-%S")

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def write_text_to_local(text, path):
    with open(path, 'w') as file:
        file.write(text)

def transcribe_audio(audio_file):
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    input = transcript.text
    return input

def chat_complete(messages):
    completion = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=messages
    )
    response = completion.choices[0].message.content
    # tokens_used = completion.usage.prompt_tokens # Amount of tokens used
    return response

def get_tts(text):
    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # # Build the voice request
    # voice = texttospeech.VoiceSelectionParams(
    #     language_code="tr-TR", name="tr-TR-Standard-C", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    # )

    # Build the voice request
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", name="en-US-Neural2-H", ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3, pitch=2.4
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary fyi
    return response.audio_content

def write_audio_to_local(audio_content, filepath):
    # The response's audio_content is binary.
    with open(filepath, "wb") as out:
        # Write the response to the output file.
        out.write(audio_content)

def remove_emojis_emoticons(text):
    # Unicode emojis pattern
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"  # Dingbats
        u"\U000024C2-\U0001F251"  # Enclosed characters
        u"\U0001f926-\U0001f937"  # Gesture symbols
        u"\U00010000-\U0010ffff"  # Supplementary characters
                           "]+", flags=re.UNICODE)
    
    # Emoticons pattern
    emoticons_pattern = re.compile(r'(?::|;|=)(?:-)?(?:\)|\(|D|P)')
    
    # Remove emojis
    text = emoji_pattern.sub(r'', text)
    
    # Remove emoticons
    text = emoticons_pattern.sub(r'', text)
    
    return text

# def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
#     """Returns the number of tokens used by a list of messages."""
#     try:
#         encoding = tiktoken.encoding_for_model(model)
#     except KeyError:
#         encoding = tiktoken.get_encoding("cl100k_base")
#     if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
#         num_tokens = 0
#         for message in messages:
#             # every message follows <im_start>{role/name}\n{content}<im_end>\n
#             num_tokens += 4
#             for key, value in message.items():
#                 num_tokens += len(encoding.encode(value))
#                 if key == "name":  # if there's a name, the role is omitted
#                     num_tokens += -1  # role is always required and always 1 token
#         num_tokens += 2  # every reply is primed with <im_start>assistant
#         return num_tokens
#     else:
#         raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
#   See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")



# def list_voices(language_code=None):
#     client = texttospeech.TextToSpeechClient()
#     response = client.list_voices(language_code=language_code)
#     voices = sorted(response.voices, key=lambda voice: voice.name)

#     print(f" Voices: {len(voices)} ".center(60, "-"))
#     for voice in voices:
#         languages = ", ".join(voice.language_codes)
#         name = voice.name
#         gender = texttospeech.SsmlVoiceGender(voice.ssml_gender).name
#         rate = voice.natural_sample_rate_hertz
#         print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")

# def get_google_credentials():
#     SCOPES = ['https://www.googleapis.com/auth/sqlservice.admin']
#     SERVICE_ACCOUNT_FILE = './google-key.json'

#     credentials = service_account.Credentials.from_service_account_file(
#         SERVICE_ACCOUNT_FILE, scopes=SCOPES)

#     return credentials
