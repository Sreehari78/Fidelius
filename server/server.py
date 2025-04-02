from flask import Flask, request, jsonify
import os
from imagehandler import predict_image_entities, redact_image, obfuscate_image, load_model
from csvhandler import predictheaders, maskobfcsv
from pdfhandler import predictpdfheaders, maskobfpdf
from flask_cors import CORS
import easyocr
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
app = Flask(__name__)
CORS(app)

# CSV handling endpoints
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
    


# PDF handling endpoints

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
    """
    Mask or obfuscate sensitive information in a PDF file.
    """
    input_data = request.get_json()
    print("Received input data:", input_data)  # Debugging log

    if not input_data:
        return jsonify({'error': 'No data provided'}), 400

    file_path = input_data.get('filePath')
    print("File path:", file_path)  # Debugging log

    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400

    try:
        print("Calling maskobfpdf with input data...")
        output = maskobfpdf(input_data)  # Pass the input data to the function
        print("Output from maskobfpdf:", output)  # Debugging log
        return jsonify({"output": output})
    except Exception as e:
        print("Error occurred:", str(e))  # Debugging log
        return jsonify({"error": str(e)}), 500

# Image handling endpoints
reader = load_model()

# Endpoint to detect headers (PII types) in an image
@app.route("/getimageentities", methods=['POST'])
def get_image_entities():
    """
    Detect headers (PII types) in an image.
    """
    data = request.get_json()
    file_path = data.get('filePath')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400

    try:
        entities = predict_image_entities(file_path)
        return jsonify({"entities": entities})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
# Endpoint to redact sensitive information in an image
@app.route("/redactimage", methods=['POST'])
def redact_image_endpoint():
    """
    Redact sensitive information in an image.
    """
    data = request.get_json()
    file_path = data.get('filePath')
    entities = data.get('entities', None)
    fill_color = data.get('fillColor', (255, 192, 203))  # Default pink color

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

# Endpoint to obfuscate sensitive information in an image
@app.route("/obfuscateimage", methods=['POST'])
def obfuscate_image_endpoint():
    """
    Obfuscate sensitive information in an image.
    """
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        output_path = obfuscate_image(data, reader)
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
                if filename.lower().endswith(('.csv', '.pdf')):
                    files.append(full_path)
        
        if not files:
            return jsonify({'files': [], 'message': 'No supported files found'}), 200
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Audio handling
@app.route('/getaudio',methods=['POST'])
def getaudio():
    """"
    Process audio files for PII detection and masking
    """""
    data = request.get_json()
    print(data)
    AUDIO_FILE = data.get('filePath')
    print(AUDIO_FILE)
    MODEL_PATH = "vosk-model-en-us-0.42-gigaspeech"
    AUTO_DETECT = True
    VERBOSE = True

    #Validating input paths
    if not AUDIO_FILE or not os.path.exists(AUDIO_FILE):
        return jsonify({'error': ' Invalid audio file path'}), 400
    if not MODEL_PATH or not os.path.exists(MODEL_PATH) or not os.path.isdir(MODEL_PATH):
        return jsonify({'error': 'Invalid model directory path'}), 400
    
    try:
        #Running the 'run_audio_pii_censor.py' script using subprocess
        main(
            audio_file = AUDIO_FILE,
            model_path = MODEL_PATH,
            auto_detect = AUTO_DETECT,
            verbose = VERBOSE
        )
        print("\nAudio PII Censoring Tool execution completed.")

        #Execute the command and capture output
        result = subprocess.run(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE, text=True)
        print(result)
        if result.returncode !=0 :
            return jsonify({'error': "Error running PII censoring tool", "details": result.stderr}), 500

        return jsonify({'message':"PII censoring completed successfully", "output": result.stdout})
    except Exception as e:
        return jsonify({'error':str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)