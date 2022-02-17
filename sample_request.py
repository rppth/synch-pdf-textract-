import requests

def local_pdf_textract(input_file_path):
    url = "http://127.0.0.1:5000/local"

    with open(input_file_path, "rb") as file:
        files = {
            "input_pdf": file
        }
        response = requests.post(url, files=files)
        print(response.text)


def s3_pdf_textract(s3_uri):
    url = "http://127.0.0.1:5000/s3"
    args = {"s3_uri": s3_uri}

    response = requests.post(url, data=args)
    print(response.text)


if __name__ == "__main__":
    local_or_s3 = input("Type 'local' to input a local PDF file. Otherwise, type 's3' to input an S3 URI for your PDF file: ")
    if local_or_s3 == "local":
        input_file_path = "samplepages.pdf" #replace this with the local path of your document
        local_pdf_textract(input_file_path)
    elif local_or_s3 == "s3":
        s3_uri = "s3://{bucket_name}/sample.pdf" #replace this with the s3 uri of document
        s3_pdf_textract(s3_uri)
