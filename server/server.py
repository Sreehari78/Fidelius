from flask import Flask, request, jsonify
import requests
import os
from imagehandler import predict_image_entities, redact_image
from csvhandler import predictheaders, maskobfcsv
from pdfhandler import predictpdfheaders, maskobfpdf
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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)