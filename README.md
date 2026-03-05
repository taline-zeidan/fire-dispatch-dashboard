# Fire Dispatch Dashboard

Fire Dispatch Dashboard is a Streamlit-based frontend for a real-time emergency dispatch system.

The application connects to a Whisper-based speech recognition backend to transcribe emergency calls, display live transcripts, and extract key incident information to assist fire dispatchers in making faster and more informed decisions.

## Features

- Real-time transcription of emergency calls
- Dashboard interface for dispatch operators
- Structured incident information extraction
- Integration with Whisper speech recognition backend
- Streamlit-based interactive UI

## Project Architecture

This project is part of a larger system composed of:

- **Whisper Streaming Backend** – handles real-time speech recognition
- **Fire Dispatch Dashboard** – Streamlit frontend for visualization and interaction
- **Database Layer** – stores incidents and call transcripts
