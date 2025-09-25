# Arabic Text-to-Speech with VITS

This project delivers a modern, responsive web interface for end-to-end Arabic text-to-speech synthesis powered by VITS (Conditional Variational Autoencoder with Adversarial Learning for End-to-End TTS).
It provides a smooth way to enter Arabic text and instantly generate natural, human-like speech.


## Installation
1. **Docker build**:
    ```bash
   docker compose build
   ```

2. **Start all services**:

   ```bash
   docker-compose up -d
   ```
Navigate to localhost:3000

## Usage

1. **Enter Text**: Type or paste your text in the text input area
2. **Click Generate IPA**: Click "Generate IPA", IPA of the input text will be generated
3. **Consult the IPA**: You can check the ipa and edit if necessary
4. **Synthesize**: Click "Synthesize Speech" , The speech will be synthesized
5. **Play Audio**: Use the built-in audio player to listen to the result 
6. **Download**: Save the audio file to your device if necessary

Made with Love.