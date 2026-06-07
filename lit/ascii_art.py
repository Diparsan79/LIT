import requests
from PIL import Image
from io import BytesIO

ASCII_RAMP = '`^",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$'

def brightness_to_char(brightness):
    index = int((brightness / 255) * (len(ASCII_RAMP) - 1))
    return ASCII_RAMP[index]

#converting rgb values into single brightness number
def pixel_to_brightness(r, g, b):
    return int(0.21 * r + 0.72 * g + 0.07 * b)

def url_to_ascii(image_url, width=60):
    try:
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()

        image= Image.open(BytesIO(response.content))

        original_width, original_height = image.size
        aspect_ratio = original_height / original_width
        height = int(width * aspect_ratio / 2.5)

        image = image.resize((width, height))

        image = image.convert("RGB")

        rows = []
        pixels = image.load()


        for y in range(height):
            row = ""
            for x in range(width):
                r, g, b = pixels[x, y]
                brightness = pixel_to_brightness(r, g, b)
                char = brightness_to_char(brightness)
                row += char * 2
            rows.append(row)
        return rows

    except Exception:
        return None
    
def poster_url_to_ascii(poster_path, width=55):
    if not poster_path:
        return None
    full_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return url_to_ascii(full_url, width=width)
