## Introduction
This repository hosts the API that serves the ESP32. It runs the server using [FastAPI](https://fastapi.tiangolo.com/)

## Requirements
- [Open AI API Key](https://platform.openai.com/)
- [Google application credentials](https://developers.google.com/workspace/guides/create-credentials)

## Setup
- Copy `.env.example` file, then rename it to `.env`
- Modify the values inside it to your values.
- **RECOMMENDED: Create a virtual environment, we recommend [VirtualEnvWrapper](https://pypi.org/project/virtualenvwrapper/)**
- Install project requirements using `pip install -r requirements.txt`

## Usage
- Use `uvicorn index:app --reload` to run development server

## Deployment
You can have the project serve your ESP32 on a local network, or you can deploy to to a remote machine and have it serve your ESP32 remotely. Whatever you choose, make sure to update the `url` variable inside `esp` project's `index/index.ino`

Refer to [FastAPI deployment](https://fastapi.tiangolo.com/deployment/) for more information

If you want to use docker:
- Build a docker image `docker build -t voice-chat-image .`
- Run a container based off of created image `docker run -d --name voice-chat-container -p 9000:9000 voice-chat-image`.

Read `scripts/README.md` for a script that might make docker deployment more convenient for you.

## Notes
- `prompt.txt` Contains a fine tuned system prompt that is sent before the user prompt to GPT. You can modify this as you wish.
- All requests and responses are saved inside `media` directory. You can inspect them for more info.

