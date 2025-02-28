#!/bin/sh

base64 -d <<< "$FIREBASE_CONTENT" > /app/config.json;
flask run --host=0.0.0.0
