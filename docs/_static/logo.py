from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a white background
img = Image.new('RGB', (200, 50), color='white')
d = ImageDraw.Draw(img)

# Draw text
d.text((10, 10), "pyBusPirateLite", fill='black')

# Save the image
img.save('logo.png') 