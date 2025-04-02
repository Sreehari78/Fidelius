from chat import chatlocal
import csv
import pandas as pd
import os
import PyPDF2
import fitz # PyMuPDF
data_dict = {}


def predictpdfheaders(filename):
    filepath = filename
    pii_items = []
    data_dict.clear()  # Clear previous data to avoid conflicts

    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)

        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            systemprompt = "You are a tool to identify types of PII data in a pdf text document. Return only a list of all the types of PII present in the format 'headername: value' for each PII data, separated by commas."
            detected_pii = chatlocal(systemprompt, text + " from this text identify all the types of PII data present eg. email, phone number, name, address etc. Do not return any other text or values.")
            print("Detected PII:\n" + detected_pii)

            # Split by newlines instead of commas for consistency
            lines = detected_pii.strip().split(',')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    # Store as a single string, not a list
                    data_dict[key] = value
                else:
                    print(f"Skipping line (no colon found): {line}")

            pii_items = [line.split(':')[0].strip() for line in lines if ':' in line]
    
    print("Data dictionary:")
    print(data_dict)
    return [' '] + pii_items


def maskobfpdf(json_data):
    filepath = json_data['filePath']
    pdf_document = fitz.open(filepath)

    # Process each header/field
    for field in json_data['headers']:
        name = field['name']
        mode = field['mode']
        prompt = field.get('prompt', "")

        # Get the original value from data_dict
        original_value = data_dict.get(name, "")
        print(f"Original value for '{name}': {original_value}")

        if not original_value or not isinstance(original_value, str):
            print(f"Invalid original value for '{name}'. Skipping.")
            continue

        # Modify the value based on mode (only for obfuscate)
        if mode == 'obfuscate':
            systemprompt = "You are a tool that can modify the following data. Return the modified value only."
            modified_value = chatlocal(systemprompt, original_value + " " + prompt)
        # No modified_value needed for mask mode since we just black it out

        # Process each page to replace this field's value
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_instances = page.search_for(original_value)

            if not text_instances:
                print(f"No instances of '{original_value}' found on page {page_num + 1}. Skipping.")
                continue
            isMask = False
            for rect in text_instances:
                if mode == 'mask':
                    isMask = True
                    # For mask mode: just black out the original text
                    page.add_redact_annot(rect, fill=(0, 0, 0))  # Black fill only
                    page.apply_redactions()
                elif mode == 'obfuscate':
                    # For obfuscate mode: clear with white and write new text in black
                    page.add_redact_annot(rect, fill=(1, 1, 1))  # White fill to clear
                    page.apply_redactions()
                    adjusted_position = rect.tl + fitz.Point(0, rect.height * 0.8)
                    page.insert_text(
                        adjusted_position,
                        modified_value,
                        fontsize=12,
                        color=(0, 0, 0)  # Black text for clean look
                    )

    # Save the modified PDF
    if isMask:
        modified_pdf_path = os.path.join(os.path.dirname(filepath), "..", "pdf_output", "masked_" + os.path.basename(filepath))
        pdf_document.save(modified_pdf_path)
        pdf_document.close()
    else:
        obfuscated_pdf_path = os.path.join(os.path.dirname(filepath), "..", "pdf_output", "obfuscated_" + os.path.basename(filepath))
        pdf_document.save(obfuscated_pdf_path)
        pdf_document.close()

    return modified_pdf_path