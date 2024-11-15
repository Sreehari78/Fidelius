from flask import Flask, request, jsonify, make_response
import os
from pdfhandler import predictpdfheaders, maskobfpdf
from csvhandler import predictheaders, maskobfcsv
from flask_cors import CORS

app = Flask(__name__)

# Allow CORS for all domains, origins and credentials
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route("/getcsvheader", methods=['POST', 'OPTIONS'])
def getcsvheader():
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
    else:
        return handle_post_request()

@app.route("/maskobfcsv", methods=['POST', 'OPTIONS'])
def maskcsv():
    if request.method == "OPTIONS":
        return build_cors_preflight_response()
    
    input_data = request.get_json()
    full_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output.csv')
    output = maskobfcsv(input_data)
    print(output)
    return jsonify({"output": "csv"})

# Handle CORS preflight response
def build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response

@app.route("/getpdfheader", methods=['GET', 'POST'])
def getpdfheader():
    pfile_path = request.get_json()['filePath']
    full_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', pfile_path)
    headers = predictpdfheaders(full_path)
    return jsonify({"headers": headers})

@app.route("/maskobfpdf", methods=['GET', 'POST'])
def maskpdf():
    input= request.get_json()
    print(input)
    maskobfpdf(input)
    return jsonify({"headers": "pdf"})

# Handle POST request
def handle_post_request():
    data = request.get_json()
    headers = process_csv_headers(data['filePath'])  # Example function
    return jsonify({"headers": headers})

# Example function to process the CSV headers
def process_csv_headers(file_path):
    try:
        with open(file_path, 'r') as file:
            headers = file.readline().strip().split(',')
        return headers
    except FileNotFoundError:
        return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
