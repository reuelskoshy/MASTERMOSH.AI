# MASTERMOSH.AI - Multilingual Voice Assistant

ChattyBot is a lightweight, real-time multilingual voice assistant web application built using Flask, OpenAI's Whisper, OpenRouter's Gemma 3.4B model, and gTTS. It allows users to interact in English or Hindi through voice, delivering smart AI-generated replies with natural voice responses. The system features auto language detection, silence-based recording, efficient audio processing, and automatic file cleanup for a smooth and deployable experience.

---

## 🔑 Features

- **Multilingual Support**  
  Automatically detects and processes English and Hindi speech.

- **Speech Recognition**  
  Converts speech to text using OpenAI Whisper (base model).

- **AI-Powered Responses**  
  Utilizes OpenRouter’s Gemma 3.4B model for generating intelligent responses.

- **Voice Feedback**  
  Converts AI-generated text to natural-sounding speech using gTTS (Google Text-to-Speech).

- **Smart Recording**  
  Automatically stops recording after 2 seconds of silence.

- **Efficient Audio Pipeline**  
  Converts audio from WebM → WAV → MP3 using FFmpeg.

- **Automatic Cleanup**  
  Deletes temporary input/output files regularly to conserve space.

---

## 🛠 Technology Stack

- **Backend**: Python (Flask)
- **Speech-to-Text**: OpenAI Whisper
- **AI Engine**: OpenRouter API (Gemma 3.4B)
- **Text-to-Speech**: gTTS (Google Text-to-Speech)
- **Audio Conversion**: FFmpeg
- **Frontend**: Vanilla JavaScript + Web Audio API

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or later  
- FFmpeg (Install via `sudo apt install ffmpeg` on Debian/Ubuntu)

### Setup Instructions

```bash
# Clone the repository
git clone https://github.com/reuelskoshy/voice-assistant.git
cd voice-assistant

# Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py
