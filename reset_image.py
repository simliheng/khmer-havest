from PIL import Image
import os

# Define the folder path and the desired size
folder_path = r'C:\Users\ASUS\OneDrive\Documents\khmer_rice\frontend\static\images'
new_size = (640, 640)

# Loop through all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(folder_path, filename)
        with Image.open(img_path) as img:
            resized_img = img.resize(new_size)
            resized_img.save(img_path)

print("All images have been resized.")
