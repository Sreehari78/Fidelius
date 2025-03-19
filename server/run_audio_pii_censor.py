import os
from audio_censor import main  # Import the main function from the script

# Configuration
AUDIO_FILE = "examples\pranav.mp3"  # Replace with your audio file path
MODEL_PATH = "vosk-model-en-us-0.42-gigaspeech"           # Replace with your Vosk model path
AUTO_DETECT = True                          # Enable LLM-based automated PII detection
VERBOSE = True                              # Enable verbose logging

def run_pii_censoring():
    """Programmatically run the PII censoring tool."""
    print("Starting the Audio PII Censoring Tool...\n")

    # Check if files exist before running
    if not os.path.exists(AUDIO_FILE):
        print(f"Error: The audio file does not exist: {AUDIO_FILE}")
        return

    if not os.path.exists(MODEL_PATH) or not os.path.isdir(MODEL_PATH):
        print(f"Error: The Vosk model path is invalid: {MODEL_PATH}")
        return

    # Run the main function of the PII censoring script
    main(
        audio_file=AUDIO_FILE,
        model_path=MODEL_PATH,
        auto_detect=AUTO_DETECT,
        verbose=VERBOSE
    )
    print("\nAudio PII Censoring Tool execution completed.")

if __name__ == "__main__":
    run_pii_censoring()