import base64

with open("sample.mp3", "rb") as f:
    encoded = base64.b64encode(f.read()).decode()

print(encoded)
