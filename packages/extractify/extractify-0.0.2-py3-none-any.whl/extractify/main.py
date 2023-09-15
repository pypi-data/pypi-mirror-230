import os
import argparse
from .converters import convert_pdf, convert_doc, convert_xlsx, convert_txt, save_as_txt

def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Convert documents to plain text.")
    parser.add_argument("input_dir", help="Input directory containing documents.")
    args = parser.parse_args()

    # Create 'textified' subdirectory
    output_dir = os.path.join(args.input_dir, "txt")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Iterate through files in the input directory
    for file_name in os.listdir(args.input_dir):
        file_path = os.path.join(args.input_dir, file_name)
        output_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + ".txt")

        if file_name.endswith(".pdf"):
            content = convert_pdf(file_path)
        elif file_name.endswith(".doc") or file_name.endswith(".docx"):
            content = convert_doc(file_path)
        elif file_name.endswith(".xlsx"):
            content = convert_xlsx(file_path)
        elif file_name.endswith(".txt"):
            content = convert_txt(file_path)
        else:
            continue

        save_as_txt(content, output_path)

if __name__ == "__main__":
    main()