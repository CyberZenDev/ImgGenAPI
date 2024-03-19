import requests
import io
from PIL import Image, UnidentifiedImageError
from flask import Flask, render_template, request, send_file
import os
import tempfile

app = Flask(__name__)

API_URL = "https://frightened-dove-turtleneck-shirt.cyclic.app/proxy/https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    return response.content

@app.route("/", methods=["GET", "POST"])
def img():
    if request.method == "POST":
        input_prompt = request.form.get("prompt")
        if not input_prompt:
            return "No prompt provided", 400

        try:
            image_bytes = query({"inputs": input_prompt})
            image = Image.open(io.BytesIO(image_bytes))

            # Ensure the /img directory exists
            img_dir = os.path.join(app.root_path, 'img')
            os.makedirs(img_dir, exist_ok=True)

            # Create a unique file name for the image in the /img directory
            fd, temp_file_path = tempfile.mkstemp(suffix='.png', dir=img_dir)
            os.close(fd)  # Close the file descriptor

            # Save the image to the file
            image.save(temp_file_path, format='PNG')

            # Generate the path relative to the Flask app for serving
            relative_path = os.path.relpath(temp_file_path, start=app.root_path)

            return send_file(relative_path, mimetype='image/png')

        except UnidentifiedImageError:
            error_message = "Sorry, we couldn't generate the image. Please try again later."
            return render_template("index.html", error_message=error_message)

    # If not POST, show the form or a relevant page
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
