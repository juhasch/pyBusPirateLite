from PIL import Image, ImageDraw

# Create a new image with a white background
img = Image.new('RGB', (32, 32), color='white')
d = ImageDraw.Draw(img)

# Draw a simple "P" shape
d.rectangle([(8, 8), (24, 24)], outline='black', width=2)
d.line([(12, 12), (12, 20), (20, 20), (20, 16), (12, 16)], fill='black', width=2)

# Save the image
img.save('favicon.ico') 