# ghost-meeting

Here is a complete, ready-to-use `README.md` file for your repository. It covers everything from the core concept to the installation steps so anyone checking out your project knows exactly how to get it running.

***

# 👻 Ghost-Meeting Summarizer

Stay on mute, focus on your deep work, and let your local AI handle the rest. 

The **Ghost-Meeting Summarizer** is a privacy-first, fully local application that listens to your system's audio during virtual meetings, transcribes the conversation in real-time, and generates a concise summary of *only* the moments you were mentioned or assigned an action item. 

Zero cloud APIs. Zero subscription fees. 100% of your company data stays on your machine.

## ✨ Features

* **Real-Time Transcription:** Uses OpenAI's lightweight Whisper model to convert meeting audio to text on the fly.
* **Keyword Filtering:** Constantly scans the live transcript for your name, specific project titles, or trigger words (like "deadline" or "action item").
* **Local AI Digests:** Feeds the relevant transcript snippets to a local LLM (via Ollama) to generate a clean, 3-bullet-point summary of what you actually need to know.
* **Privacy-First:** Everything runs locally on your hardware. No audio or text is ever sent to external servers.
* **Lightweight UI:** Powered by Streamlit for a clean, distraction-free dashboard.

## 🛠️ Tech Stack

* **Language:** Python 3.9+
* **Audio Capture:** `PyAudio` / `sounddevice`
* **Transcription:** `openai-whisper`
* **Local LLM Engine:** Ollama (running `phi3` or `llama3`)
* **Frontend:** Streamlit

## ⚙️ Prerequisites

Before installing, you need a few things set up on your machine:

1. **Python 3.9+** installed.
2. **Ollama** installed and running. ([Download here](https://ollama.com/))
3. **A Local LLM Model:** Open your terminal and pull a lightweight model:
   ```bash
   ollama run phi3
   ```
4. **Virtual Audio Cable (Optional but Recommended):** To capture the audio coming *out* of your speakers (what the meeting is saying), you may need a virtual audio routing tool. 
    * **Mac:** Install [BlackHole](https://existential.audio/blackhole/).
    * **Windows:** Enable "Stereo Mix" in your sound settings, or use [VB-Audio Cable](https://vb-audio.com/Cable/).

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ghost-meeting-summarizer.git
   cd ghost-meeting-summarizer
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. **Start the Ollama server** in the background (if it isn't running already).
2. **Launch the Streamlit app:**
   ```bash
   streamlit run app.py
   ```
3. **Configure your settings:** In the web UI, type in your name and any specific keywords you want the AI to listen for.
4. **Select your audio device:** Choose your system loopback or virtual audio cable from the dropdown menu.
5. **Start Ghosting:** Click "Start Listening." Join your meeting, mute your mic, and get back to your deep work. 
6. **Get your Digest:** Click "End Meeting" to automatically generate your personalized action-item summary.

## 🗺️ Roadmap

- [ ] Add explicit speaker detection (Diarization).
- [ ] Implement a system-tray "Wake Up" notification when your name is called.
- [ ] Add Notion/Todoist API integration for one-click task export.
- [ ] Save contextual audio snippets (30 seconds before/after a trigger word).

## ⚠️ Disclaimer

**Please check your local laws and company policies regarding recording meetings.** Even though this tool processes everything locally and does not store the permanent audio, capturing meeting audio may require two-party consent depending on your jurisdiction. Use responsibly!

***

Would you like me to write the `requirements.txt` file next, or should we draft the core Python script for the audio capture?
