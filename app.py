# app.py
from flask import Flask, request, jsonify, send_from_directory
import requests, os, time
from PIL import Image, ImageOps
from io import BytesIO

app = Flask(__name__)

# Settings
SAVE_DIR = "uploads"
DOMAIN = "https://pythoncode.unknownx1337.dev/removebg"  # আপনার আসল domain/subdomain বসান

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Dummy background remover using PIL (shared hosting friendly)
def remove_background_lightweight(img_data):
    try:
        img = Image.open(BytesIO(img_data)).convert("RGBA")
        # Make white background transparent (simple approximation)
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        img.putdata(newData)
        output = BytesIO()
        img.save(output, format="PNG")
        return output.getvalue()
    except Exception as e:
        raise e

# Rembg API (lightweight version)
@app.route("/rembg", methods=["POST", "GET"])
def rembg_api():
    image_url = request.args.get("image") or request.form.get("image")
    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    try:
        # Fetch image from URL
        img_data = requests.get(image_url, timeout=15).content

        # Remove background (lightweight)
        output = remove_background_lightweight(img_data)

        # Save PNG
        filename = f"{int(time.time())}.png"
        filepath = os.path.join(SAVE_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(output)

        resp = {
            "status": "success",
            "file": filename,
            "image": f"{DOMAIN}/uploads/{filename}"
        }
        return jsonify(resp)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve uploaded files
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(SAVE_DIR, filename)

# Optional home page
@app.route("/")
def home():
    return "Background Remover API is running! Use /rembg?image=IMAGE_URL"

if __name__ == "__main__":
    app.run(debug=True)
