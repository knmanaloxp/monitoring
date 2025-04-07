from PIL import Image
import cairosvg
from io import BytesIO

# Convert SVG to PNG using cairosvg
png_data = cairosvg.svg2png(
    url="network_agent.svg",
    output_width=256,
    output_height=256
)

# Convert PNG to ICO
img = Image.open(BytesIO(png_data))
img.save('network_agent.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])