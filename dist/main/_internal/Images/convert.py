from PIL import Image

img = Image.open("Images/anydesk_icon.png")
img.save("Images/anydesk_icon.ico", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])