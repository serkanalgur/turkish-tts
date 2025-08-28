# Turkish TTS with Piper TTS

A multilingual Text-to-Speech (TTS) service for **Turkish (tr-TR)** using [Piper TTS](https://github.com/rhasspy/piper).

## Features
- Turkish number, date, time, currency formatting
- High-quality ONNX-based neural TTS
- REST API for speech synthesis
- Web frontend included

## Prerequisites
- Docker (recommended)

## Usage

```bash
docker build -t turkish-tts .
docker run -p 5000:5000 --name turkish-tts turkish-tts
