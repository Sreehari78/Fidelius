from flask import Flask, request, jsonify
import requests
import os
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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)