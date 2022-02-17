import os
import boto3
from io import BytesIO
from itertools import repeat
from flask import Flask, request
from pdf2image import convert_from_bytes, convert_from_path
from werkzeug.utils import secure_filename
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def call_image_textract(image_item, textract):
    i, image = image_item
    buf = BytesIO()
    image.save(buf, format='JPEG')
    byte_string = buf.getvalue()
    image_json = textract.analyze_document(
        Document={
            "Bytes": byte_string
        },
        FeatureTypes=["TABLES", "FORMS"]
    )
    return (f"Page {i}", image_json)

@app.route("/s3", methods=["POST"])
def process_file_s3():
    s3_uri = request.form.get("s3_uri")

    s3 = boto3.client('s3')
    textract = boto3.client('textract')
    bucket_name, key = s3_uri.replace("s3://", "").split("/", 1)
    s3_response_object = s3.get_object(Bucket=bucket_name, Key=key)
    object_content = s3_response_object['Body'].read()

    images = convert_from_bytes(object_content)
    with ThreadPoolExecutor() as executor:
        all_image_jsons = executor.map(call_image_textract, enumerate(images), repeat(textract))
        return dict(sorted(dict(all_image_jsons).items()))


@app.route("/local", methods=["POST"])
def process_file_local():
    file = request.files["input_pdf"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(os.path.dirname(__file__), filename)
    file.save(filepath)

    textract = boto3.client('textract')
    images = convert_from_path(filepath)
    with ThreadPoolExecutor() as executor:
        all_image_jsons = executor.map(call_image_textract, enumerate(images), repeat(textract))
        return dict(sorted(dict(all_image_jsons).items()))


if __name__ == "__main__":
    app.run()
