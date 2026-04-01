import requests
import os

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/api/upload/"
# Change this to the actual path of an image on your computer
IMAGE_PATH = "D:/bike, beachh, dog.png"

def test_backend_upload():
    if not os.path.exists(IMAGE_PATH):
        print(f"[ERROR] File not found: {IMAGE_PATH}")
        return

    # 1. Prepare the file payload
    # The key 'image_file' MUST match your ImageStore model field name
    files = {
        'image_file': open(IMAGE_PATH, 'rb')
    }

    # 2. Prepare the data payload
    # 'source' is required by your model choices ('HUMAN' or 'AI')
    data = {
        'source': 'HUMAN',
        'generation_prompt': ''
    }

    print(f"[*] Sending '{IMAGE_PATH}' to {API_URL}...")

    try:
        # 3. Execute the POST request
        response = requests.post(API_URL, files=files, data=data)

        # 4. Analyze results
        if response.status_code == 201:
            print("[SUCCESS] Image uploaded and processed!")
            print("Response Data:", response.json())
        elif response.status_code == 207:
            print("[PARTIAL SUCCESS] Image saved, but AI inference failed.")
            print("Error Details:", response.json().get('error'))
        else:
            print(f"[FAILED] Status Code: {response.status_code}")
            print("Errors:", response.text)

    except Exception as e:
        print(f"[CONNECTION ERROR] Could not reach server: {e}")
    finally:
        files['image_file'].close()

if __name__ == "__main__":
    test_backend_upload()