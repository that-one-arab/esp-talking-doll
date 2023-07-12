#!/bin/bash

sudo docker stop voice-chat-container
sudo docker rm voice-chat-container
sudo docker image rm voice-chat-image
docker build -t voice-chat-image .
sudo docker run -d --name voice-chat-container -p 9000:9000 voice-chat-image