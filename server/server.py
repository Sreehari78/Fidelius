from flask import Flask, request, jsonify
import os
from imagehandler import predict_image_entities, redact_image
from csvhandler import predictheaders, maskobfcsv
from pdfhandler import predictpdfheaders, maskobfpdf
import subprocess  # For running external Python scripts
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/getcsvheader", methods=['GET', 'POST'])
def getcsvheader():
    data = request.get_json()
    file_path = data.get('filePath')
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400
    
    try:
        headers = predictheaders(file_path)
        return jsonify({"headers": headers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/maskobfcsv', methods=['POST'])
def mask_obfuscate_csv():
    json_data = request.get_json()
    if not json_data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        output_file = maskobfcsv(json_data)  # Now expects inputPath
        return jsonify({
            'output': output_file,
            'filename': os.path.basename(output_file)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/getpdfheader", methods=['GET', 'POST'])
def getpdfheader():
    data = request.get_json()
    pfile_path = data.get('filePath')
    if not pfile_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        headers = predictpdfheaders(pfile_path)
        return jsonify({"headers": headers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/maskobfpdf", methods=['GET', 'POST'])
def maskpdf():
    input_data = request.get_json()
    if not input_data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        print(input_data)
        output = maskobfpdf(input_data)
        return jsonify({"output": output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route("/getimageentities", methods=['POST'])
def get_image_entities():
    data = request.get_json()
    file_path = data.get('filePath')
    output_path = data.get('outputPath', os.path.dirname(file_path) if file_path else None)
    
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400
    
    if not output_path:
        return jsonify({"error": "No output path provided"}), 400
    
    try:
        # Get entities and create redacted image
        entities = predict_image_entities(file_path)
        redacted_path = redact_image(
            file_path=file_path,
            fill_color=(255, 192, 203)  # Default pink color
        )
        
        return jsonify({
            "entities": entities,
            "output": redacted_path,
            "filename": os.path.basename(redacted_path)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/redactimage", methods=['POST'])
def redact_image_endpoint():
    json_data = request.get_json()
    
    if not json_data:
        return jsonify({'error': 'No data provided'}), 400
    
    file_path = json_data.get('filePath')
    entities = json_data.get('entities', None)  # Optional list of entities to redact
    fill_color = json_data.get('fillColor', (255, 192, 203))  # Default to pink from example
    
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    
    try:
        output_path = redact_image(file_path, entities_to_redact=entities, fill_color=tuple(fill_color))
        return jsonify({
            'output': output_path,
            'filename': os.path.basename(output_path)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/getfolderfiles', methods=['POST'])
def get_folder_files():
    data = request.get_json()
    folder_path = data.get('folderPath')
    
    if not folder_path or not os.path.isdir(folder_path):
        return jsonify({'error': 'Invalid folder path'}), 400
    
    try:
        files = []
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if filename.lower().endswith(('.csv', '.pdf', '.png', '.jpg', '.jpeg')):
                    files.append(full_path)
        
        if not files:
            return jsonify({'files': [], 'message': 'No supported files found'}), 200
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/getaudio', methods=['POST'])
def getaudio():
    """
    New route to process audio files for PII detection and masking.
    """
    data = request.get_json()
    AUDIO_FILE = "examples\pranav.mp3"  # Replace with your audio file path
    MODEL_PATH = "vosk-model-en-us-0.42-gigaspeech"           # Replace with your Vosk model path
    AUTO_DETECT = True                          # Enable LLM-based automated PII detection
    VERBOSE = True        # Optional, default to False
    
    # Validating input paths
    if not audio_file_path or not os.path.exists(audio_file_path):
        return jsonify({"error": "Invalid audio file path"}), 400

    if not model_path or not os.path.exists(model_path) or not os.path.isdir(model_path):
        return jsonify({"error": "Invalid model directory path"}), 400

    try:
        # Running the `run_audio_pii_censor.py` script using subprocess
        main(
            audio_file=AUDIO_FILE,
            model_path=MODEL_PATH,
            auto_detect=AUTO_DETECT,
            verbose=VERBOSE
        )
        print("\nAudio PII Censoring Tool execution completed.")

        # Execute the command and capture output
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            return jsonify({"error": "Error running PII censoring tool", "details": result.stderr}), 500

        # Parse the output (assuming the script provides outputs in a structured format)
        return jsonify({"message": "PII censoring completed successfully", "output": result.stdout})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)