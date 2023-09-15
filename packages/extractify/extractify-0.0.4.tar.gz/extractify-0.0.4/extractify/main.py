import os
import argparse
import boto3
from tqdm import tqdm
from .converters import convert_pdf, convert_doc, convert_xlsx, convert_txt, save_as_txt

def process_file(file_path, output_path, file_name, omit_pdf):
    if file_name.endswith(".pdf") and not omit_pdf:
        content = convert_pdf(file_path)
    elif file_name.endswith(".doc") or file_name.endswith(".docx"):
        content = convert_doc(file_path)
    elif file_name.endswith(".xlsx"):
        content = convert_xlsx(file_path)
    elif file_name.endswith(".txt"):
        content = convert_txt(file_path)
    else:
        return

    save_as_txt(content, output_path)

def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(description="Convert documents to plain text.")
    parser.add_argument("input", help="Input directory containing documents or S3 bucket path (s3://bucket-name/prefix).")
    parser.add_argument("--omit-pdf", action="store_true", help="Omit PDF file formats.")
    args = parser.parse_args()

    # Check if the input is an S3 bucket
    if args.input.startswith("s3://"):
        s3 = boto3.client("s3")
        args.input = args.input.rstrip('/')  # Strip the trailing '/' from the input S3 URI
        bucket_name, prefix = args.input[5:].split("/", 1)

        # Iterate through files in the S3 bucket with a progress bar
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            for obj in tqdm(page.get("Contents", []), desc="Converting files"):
                if obj["Size"] == 0:  # Skip directories or empty objects
                    continue

                file_name = obj["Key"].split("/")[-1]
                file_path = f"/tmp/{file_name}"
                output_path = f"/tmp/txt-{file_name}.txt"

                s3.download_file(bucket_name, obj["Key"], file_path)
                
                if os.path.isfile(file_path):  # Check if the file exists before processing it
                    process_file(file_path, output_path, file_name, args.omit_pdf)
                    
                    if os.path.isfile(output_path):  # Check if the output file exists before uploading it
                        s3.upload_file(output_path, bucket_name, f"{prefix}/txt/{file_name}.txt")

    else:
        # Create 'txt' subdirectory
        output_dir = os.path.join(args.input, "txt")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get a list of files in the input directory
        files = os.listdir(args.input)

        # Iterate through files in the input directory with a progress bar
        for file_name in tqdm(files, desc="Converting files"):
            file_path = os.path.join(args.input, file_name)
            output_path = os.path.join(output_dir, os.path.splitext(file_name)[0] + ".txt")

            process_file(file_path, output_path, file_name, args.omit_pdf)

if __name__ == "__main__":
    main()