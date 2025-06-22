import os
from PIL import Image

path = os.path.join(os.getcwd(), "static", "aqua_logo.png")
print("Resolved path:", path)

try:
    img = Image.open(path)
    print("✅ Image loaded successfully!")
except Exception as e:
    print("❌ Error:", e)
