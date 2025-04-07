from PIL import Image, ImageDraw

# Create a new image with a green background
size = 256
img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw green circle
circle_radius = int(size * 0.47)  # 120/256 ≈ 0.47
circle_center = (size // 2, size // 2)
draw.ellipse(
    [(size//2 - circle_radius, size//2 - circle_radius),
     (size//2 + circle_radius, size//2 + circle_radius)],
    fill='#4CAF50'
)

# Draw white checkmark
checkmark_points = [
    (int(size * 0.3), size // 2),  # Start point
    (int(size * 0.45), int(size * 0.65)),  # Middle point
    (int(size * 0.7), int(size * 0.35))  # End point
]
draw.line(checkmark_points, fill='white', width=int(size * 0.1), joint='curve')

# Save as ICO with multiple sizes
img.save('network_agent.ico', format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])