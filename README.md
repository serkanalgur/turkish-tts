# tr--pipe-tts

A multilingual Text-to-Speech (TTS) service for **Turkish (tr-TR)** and **Azerbaijani (az-AZ)** using [Piper TTS](https://github.com/rhasspy/piper).

## Features
- Turkish and Azerbaijani number, date, time, currency formatting
- High-quality ONNX-based neural TTS
- REST API for speech synthesis
- Web frontend included

## Prerequisites
- Docker (recommended)

## Usage

```bash
docker build -t pipe-tts .
docker run -p 5000:5000 pipe-tts
