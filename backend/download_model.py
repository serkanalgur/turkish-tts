# backend/download_model.py
import os
import subprocess

MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/dfki/medium/tr_TR-dfki-medium.onnx"
CONFIG_URL = f"{MODEL_URL}.json"
MODEL_2_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/tr/tr_TR/fahrettin/medium/tr_TR-fahrettin-medium.onnx"
CONFIG_2_URL = f"{MODEL_2_URL}.json"
MODELS_DIR = "/app/models"

os.makedirs(MODELS_DIR, exist_ok=True)

print("Downloading Turkish TTS models...")
subprocess.run(["wget", "-O", f"{MODELS_DIR}/tr_TR-dfki-medium.onnx", MODEL_URL])
subprocess.run(["wget", "-O", f"{MODELS_DIR}/tr_TR-dfki-medium.onnx.json", CONFIG_URL])
subprocess.run(["wget", "-O", f"{MODELS_DIR}/tr_TR-fahrettin-medium.onnx", MODEL_2_URL])
subprocess.run(
    ["wget", "-O", f"{MODELS_DIR}/tr_TR-fahrettin-medium.onnx.json", CONFIG_2_URL]
)
print("Models downloaded.")
