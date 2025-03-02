from chat import chatlocal
import csv
import pandas as pd
import json
import os

def predictheaders(file_path):
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            datatypes = next(reader)
        print(f"Headers from {file_path}: {datatypes}")
        return [' '] + datatypes
    except Exception as e:
        raise Exception(f"Error reading CSV headers from {file_path}: {str(e)}")

def maskobfcsv(json_data):
    filename = json_data['fileName']
    input_path = json_data.get('inputPath', '')  # Get inputPath from JSON
    if not input_path:
        input_path = os.path.join('..', 'data', filename)  # Fallback to default
    else:
        input_path = os.path.join(input_path, filename)  # Use provided inputPath
    
    # Validate input file exists
    if not os.path.exists(input_path):
        raise Exception(f"Input file not found: {input_path}")
    
    df = pd.read_csv(input_path)
    
    # Generate output filename using outputPath if provided
    output_path = json_data.get('outputPath', '')
    base_name = os.path.splitext(filename)[0]
    output_filename = f"{base_name}-output.csv"
    csv_output_file = os.path.join(
        output_path if output_path else os.path.join('..', 'client', 'public'),
        output_filename
    )
    
    updated_df = df.copy()
    og_headers = set(df.columns.tolist())
    column_info = json_data['headers']

    for col in column_info:
        column_name = col['name']
        mode = col['mode']
        instruction = col['prompt']

        if column_name in og_headers:
            if mode == "mask":
                print(f"Masking the data in column {column_name}")
                updated_df[column_name] = df[column_name].apply(lambda x: '#' * len(str(x)))
                print(f"Data masked for {column_name}")
            elif mode == "obfuscate":
                print(f"Obfuscating the data in column {column_name}")
                csvCol = df[column_name]
                data_string = ','.join(csvCol.astype(str))
                modified_data_string = chatlocal(instruction, data_string)
                modified_chunk = modified_data_string.split(',')

                for x in range(min(len(csvCol), len(modified_chunk))):
                    updated_df.loc[x, column_name] = modified_chunk[x]
    
    updated_df = updated_df.iloc[1:]
    os.makedirs(os.path.dirname(csv_output_file), exist_ok=True)
    updated_df.to_csv(csv_output_file, index=False)
    
    print(f"Output saved to: {csv_output_file}")
    return csv_output_file