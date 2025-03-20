import argparse
import csv
import json
import os
import re
from typing import List, Tuple
from pydub import AudioSegment
from pydub.generators import Sine
from vosk import Model, KaldiRecognizer, SetLogLevel
import whisper
from chat import chatlocal  # Custom local LLM API for PII detection

# =====================
# Functions
# =====================
def transcribe_with_whisper(audio_file: str, verbose: bool = False) -> str:
    """Transcribe audio using Whisper."""
    if verbose:
        print("Loading Whisper model for transcription...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file)
        transcript = result.get("text", "").strip()
        if not transcript and verbose:
            print("Warning: No transcription produced by Whisper.")
        if verbose:
            print(f"Whisper Transcript: {transcript}")
        return transcript
    except Exception as e:
        print(f"Error in Whisper transcription: {e}")
        return ""

def detect_pii_with_llm(transcript: str, verbose: bool = False) -> List[str]:
    """Detect PII in the transcript using an LLM, returning only PII values."""
    if not transcript:
        print("No transcript provided for PII detection.")
        return []
    
    # Define the prompt strictly instructing the LLM to return JSON
    prompt = f"""
    Analyze the transcript below and detect Personal Identifiable Information (PII).
    Return results ONLY in the following JSON format:
    {{
        "pii_list": ["VALUE1", "VALUE2", ...]
    }}
    Transcript:
    ---
    {transcript}
    ---
    """
    
    try:
        # Call the `chatlocal` LLM API
        raw_response = chatlocal(prompt, transcript)
        
        if verbose:
            print(f"Raw LLM Response:\n{raw_response}")
        
        # Check if response contains valid JSON
        json_match = re.search(r"\{.*?\}", raw_response, re.DOTALL)
        if not json_match:
            print("No valid JSON structure found in LLM response. Attempting fallback parsing.")
            
            # Fallback logic: If JSON is missing, extract potential PII by heuristics
            extracted_pii = []
            pii_pattern = r"[A-Z][a-z]+(?: [A-Z][a-z]+)*|[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z]+|\d+"  # Heuristic pattern
            for match in re.findall(pii_pattern, raw_response):
                extracted_pii.append(match.strip())
            
            if verbose:
                print(f"Fallback extracted PII values: {extracted_pii}")
            
            return extracted_pii
        
        # Parse the matched JSON object
        response_json = json.loads(json_match.group(0))
        pii_list = response_json.get("pii_list", [])
        
        # Validate list of PII
        if not isinstance(pii_list, list) or not all(isinstance(v, str) for v in pii_list):
            print("Invalid PII list format in extracted JSON. Returning fallback empty list.")
            return []
        
        if verbose:
            print(f"Detected PII Values: {pii_list}")
        
        return pii_list
    except json.JSONDecodeError as e:
        print(f"JSON decoding error in LLM response: {e}. Response: {raw_response}")
        return []
    except Exception as e:
        print(f"Unexpected error in PII detection: {e}")
        return []

def write_pii_to_csv(detected_pii: List[str], output_file: str = "detected_pii.csv", verbose: bool = False):
    """Write detected PII values to a CSV file."""
    if not detected_pii:
        print("No PII to write to CSV.")
        return

    try:
        with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["value"])  # Simplified header
            for pii_value in detected_pii:
                writer.writerow([pii_value])
        if verbose:
            print(f"PII values written to CSV file: {output_file}")
    except Exception as e:
        print(f"Error writing PII to CSV: {e}")

def transcribe_audio_with_timestamps(audio_file: str, model_path: str, verbose: bool = False) -> Tuple[str, List[dict]]:
    """Transcribe audio with Vosk and get word-level timestamps."""
    if verbose:
        print(f"Transcribing audio with Vosk: {audio_file} using model: {model_path}")
    try:
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        recognizer.SetWords(True)

        wf = open(audio_file, "rb")
        if len(wf.read(44)) != 44:  # Check WAV header
            print("Invalid WAV file header.")
            return "", []
        wf.seek(44)  # Reset to after header

        all_words = []
        while True:
            data = wf.read(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                if "result" in result:
                    all_words.extend(result["result"])

        final_result = json.loads(recognizer.FinalResult())
        if "result" in final_result:
            all_words.extend(final_result["result"])

        transcript = " ".join(word["word"] for word in all_words if "word" in word)
        if verbose:
            print(f"Vosk Transcript: {transcript[:100]}... ({len(all_words)} words)")
        return transcript, all_words
    except Exception as e:
        print(f"Error in Vosk transcription: {e}")
        return "", []

def find_pii_timestamps(vosk_words: List[dict], pii_terms: List[str], verbose: bool = False) -> List[Tuple[int, int]]:
    """Find timestamps for PII terms in Vosk transcription."""
    if not vosk_words or not pii_terms:
        return []

    timestamps = []
    normalized_pii = set()
    for term in pii_terms:
        normalized_pii.update(re.findall(r"\b\w+\b", term.lower()))

    if verbose:
        print(f"Normalized PII terms for matching: {normalized_pii}")

    for word_info in vosk_words:
        if "word" not in word_info or "start" not in word_info or "end" not in word_info:
            continue
        word = word_info["word"].lower()
        if word in normalized_pii:
            start_ms = int(word_info["start"] * 1000)
            end_ms = int(word_info["end"] * 1000)
            timestamps.append((start_ms, end_ms))
            if verbose:
                print(f"Matched '{word}' at {start_ms}-{end_ms}ms")

    if timestamps and verbose:
        print(f"Found {len(timestamps)} PII timestamps")
    return timestamps

def beep_pii_segments(audio: AudioSegment, pii_timestamps: List[Tuple[int, int]], verbose: bool = False) -> AudioSegment:
    """Replace PII segments with beep tones."""
    if not pii_timestamps:
        if verbose:
            print("No PII timestamps to mask.")
        return audio

    censored_audio = audio
    for start, end in sorted(pii_timestamps, reverse=True):  # Reverse to avoid overlap issues
        if end <= start or start < 0 or end > len(audio):
            if verbose:
                print(f"Invalid timestamp range: {start}-{end}ms")
            continue
        duration = end - start
        beep = Sine(1000).to_audio_segment(duration=duration).apply_gain(-10)
        censored_audio = censored_audio[:start] + beep + censored_audio[end:]
        if verbose:
            print(f"Masked audio from {start}ms to {end}ms")
    return censored_audio

# =====================
# Main Workflow
# =====================
def main(audio_file: str, model_path: str, auto_detect: bool, verbose: bool):
    """Detect PII, write to CSV, and mask audio with beeps."""
    SetLogLevel(-1)  # Reduce Vosk logging
    print(audio_file)
    # Validate input audio file
    if not os.path.exists(audio_file):
        print(f"Audio file not found: {audio_file}")
        return

    # Step 1: Transcribe with Whisper for PII detection
    transcript = transcribe_with_whisper(audio_file, verbose)
    if not transcript:
        print("Transcription failed. Cannot proceed with PII detection.")
        return

    # Step 2: Detect PII and write to CSV
    detected_pii = []
    if auto_detect:
        detected_pii = detect_pii_with_llm(transcript, verbose)
    if not detected_pii:
        print("No PII detected. Exiting.")
        return

    csv_file = "detected_pii.csv"
    write_pii_to_csv(detected_pii, csv_file, verbose)

    # Step 3: Load audio and prepare for Vosk
    try:
        audio = AudioSegment.from_file(audio_file)
        if audio.frame_rate != 16000 or audio.channels != 1 or audio.sample_width != 2:
            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            temp_wav = "temp_vosk_input.wav"
            audio.export(temp_wav, format="wav")
            vosk_audio_file = temp_wav
            if verbose:
                print(f"Converted audio to {temp_wav} for Vosk compatibility")
        else:
            vosk_audio_file = audio_file
    except Exception as e:
        print(f"Error preparing audio for Vosk: {e}")
        return

    # Step 4: Transcribe with Vosk for timestamps
    _, vosk_words = transcribe_audio_with_timestamps(vosk_audio_file, model_path, verbose)
    if not vosk_words:
        print("Vosk transcription failed. Cannot proceed with masking.")
        if vosk_audio_file != audio_file and os.path.exists(vosk_audio_file):
            os.remove(vosk_audio_file)
        return

    # Step 5: Find PII timestamps
    pii_timestamps = find_pii_timestamps(vosk_words, detected_pii, verbose)

    # Clean up temporary file
    if vosk_audio_file != audio_file and os.path.exists(vosk_audio_file):
        os.remove(vosk_audio_file)
        if verbose:
            print(f"Removed temporary file: {vosk_audio_file}")

    # Step 6: Mask audio with beeps
    if pii_timestamps:
        censored_audio = beep_pii_segments(audio, pii_timestamps, verbose)
        output_file = f"{os.path.splitext(audio_file)[0]}_censored.wav"
        censored_audio.export(output_file, format="wav")
        print(f"Masked audio saved to: {output_file}")
    else:
        print("No PII timestamps found. Audio unchanged.")

# =====================
# Command-line Interface
# =====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio PII Censoring Tool: Detect PII and Beep")
    parser.add_argument("--audio_file", required=True, help="Path to the input audio file")
    parser.add_argument("--model_path", required=True, help="Path to the Vosk model directory")
    parser.add_argument("--auto_detect", action="store_true", help="Enable automated PII detection using LLM")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    main(args.audio_file, args.model_path, args.auto_detect, args.verbose)