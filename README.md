# Voice-Based AI Chatbot

This is a Python-based voice-enabled AI chatbot that can answer factual questions using sources like Wikipedia, Google (via SerpAPI), and DuckDuckGo. It can also speak its responses and understand voice input using speech recognition.

## Features

- **Voice & Text Interaction**: Users can interact by speaking or typing.
- **Smart Q&A System**: Answers factual questions by searching:
  - Wikipedia
  - Google Search (via SerpAPI)
  - DuckDuckGo (fallback)
- **Casual Conversation**: Responds to greetings and simple casual phrases.
- **Weather Info**: Get live weather updates by city.
- **Memory**: Remembers previous questions and answers (stored in `responses.txt`).
- **Custom Learning**: Allows users to correct or add new responses.
- **Pronunciation Help**: Offers basic pronunciation for any word.
- **Time Queries**: Tells the current time.

## Requirements

- Python 3.6+
- Packages:
  - `requests`
  - `beautifulsoup4`
  - `wikipedia-api`
  - `serpapi`
  - `pyttsx3`
  - `SpeechRecognition`
  - `pyaudio` (may need manual install depending on OS)

Install dependencies using:

```bash
pip install 
