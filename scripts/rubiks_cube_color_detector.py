# Importing necessary libraries
from PIL import Image, ImageEnhance  # PIL for image processing
import numpy as np  # NumPy for efficient array handling
import colorsys  # Colorsys for RGB to HSV conversion
from collections import Counter  # For counting pixel occurrences
import sys  # To handle command-line arguments
import json  # To output results as JSON

# Known color references for the Rubik's Cube (RGB values)
color_refs = {
    "orange": (232, 112, 0),
    "red": (220, 66, 47),
    "yellow": (245, 180, 0),
    "white": (243, 243, 243),
    "blue": (61, 129, 246),
    "green": (0, 157, 84),
}


def rgb_to_hsv(rgb):
    """
    Converts RGB values to HSV format.
    
    :param rgb: Tuple of RGB values (0-255 range)
    :return: HSV values (Hue, Saturation, Value)
    """
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return h * 360, s * 255, v * 255


def preprocess_image(image):
    """
    Enhances the contrast and brightness of the image.
    
    :param image: PIL Image object to be processed
    :return: Enhanced PIL Image object
    """
    # Increase contrast by 1.5 times
    contrast_enhancer = ImageEnhance.Contrast(image)
    image = contrast_enhancer.enhance(1.5)

    # Increase brightness by 1.2 times
    brightness_enhancer = ImageEnhance.Brightness(image)
    image = brightness_enhancer.enhance(1.2)

    return image


def calculate_dominant_color(sub_image):
    """
    Calculates the dominant color of a sub-image (a part of the main image).
    
    :param sub_image: Numpy array representing the sub-image (RGB format)
    :return: Dominant color (as RGB tuple)
    """
    flat_pixels = sub_image.reshape(-1, 3)
    most_common_color = Counter(map(tuple, flat_pixels)).most_common(1)[0][0]
    return np.array(most_common_color)


def classify_color(rgb_value):
    """
    Classifies a given RGB color into one of the predefined categories based on hue and saturation.
    
    :param rgb_value: RGB color value (tuple)
    :return: Color name as a string (e.g., "red", "blue")
    """
    value_hsv = rgb_to_hsv(rgb_value)

    # Extract hue, saturation, and value
    hue = value_hsv[0]
    saturation = value_hsv[1]
    value = value_hsv[2]

    # Specific color range classification (orange and yellow for simplicity)
    if 20 <= hue <= 40 and saturation > 200:
        return "orange"
    if 40 < hue <= 60 and value > 200:
        return "yellow"

    # Default distance-based classification for other colors
    min_distance = float("inf")
    closest_color = None

    for color_name, ref_rgb in color_refs.items():
        # Compute RGB distance between the current color and reference color
        rgb_distance = np.linalg.norm(np.array(rgb_value) - np.array(ref_rgb))
        ref_hsv = rgb_to_hsv(ref_rgb)

        # Compute the hue distance and add weight
        hue_distance = abs(value_hsv[0] - ref_hsv[0])
        total_distance = rgb_distance + 0.5 * hue_distance

        if total_distance < min_distance:
            min_distance = total_distance
            closest_color = color_name

    return closest_color


def detect_cube_colors(image_path):
    """
    Detects and classifies the dominant colors of a Rubik's Cube from a given image.
    
    :param image_path: Path to the image file
    :return: List of color classifications for the cube (3x3 grid of color names)
    """
    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        raise FileNotFoundError(f"Error opening image file: {image_path}. Error: {e}")

    # Preprocess the image (adjust contrast and brightness)
    image = preprocess_image(image)
    image_array = np.array(image)

    # Get the dimensions of the image
    height, width, _ = image_array.shape
    step_x = width // 3
    step_y = height // 3
    colors = []

    # Split the image into 3x3 sections and detect colors
    for i in range(3):
        row_colors = []
        for j in range(3):
            # Define the bounding box for the sub-image
            x_start = j * step_x
            x_end = (j + 1) * step_x
            y_start = i * step_y
            y_end = (i + 1) * step_y

            sub_image = image_array[y_start:y_end, x_start:x_end]
            dominant_color = calculate_dominant_color(sub_image)

            # Classify the dominant color
            color = classify_color(dominant_color)
            row_colors.append(color)
        colors.append(row_colors)

    return colors


# Receiving image paths as command-line arguments
image_paths = sys.argv[1:]

if not image_paths:
    print(json.dumps({"error": "No image paths provided."}))
    sys.exit(1)

# Dictionary to store results for each image
results = {}

# Process each image
for i, image_path in enumerate(image_paths, 1):
    try:
        cube_colors = detect_cube_colors(image_path)
        results[f"Image {i}"] = cube_colors
    except FileNotFoundError as e:
        results[f"Image {i}"] = {"error": str(e)}
    except Exception as e:
        results[f"Image {i}"] = {"error": f"An error occurred: {str(e)}"}

# Output the results as JSON
print(json.dumps(results))
