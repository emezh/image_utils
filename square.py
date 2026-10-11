import os
import argparse
import cv2
import numpy as np
import sys

def hex_to_rgb(hex_str):
    """Converts #RRGGBB or RRGGBB to BGR for OpenCV."""
    hex_str = hex_str.lstrip('#')
    rgb = tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])  # OpenCV uses BGR

def grayscale_to_bgr(percent):
    """Converts 0.0-1.0 grayscale to BGR."""
    val = int(max(0, min(1.0, percent)) * 255)
    return (val, val, val)

def square_image(input_directory, output_directory, fill_color=(0, 0, 0)):
    # Normalize paths to accurately compare them
    abs_input = os.path.abspath(input_directory)
    abs_output = os.path.abspath(output_directory)
    same_dir = (abs_input == abs_output)

    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
            try:
                image_path = os.path.join(input_directory, filename)
                img = cv2.imread(image_path)
                
                if img is None:
                    continue

                h, w = img.shape[:2]
                side = max(h, w)

                # Calculate padding for centering
                pad_top = (side - h) // 2
                pad_bottom = side - h - pad_top
                pad_left = (side - w) // 2
                pad_right = side - w - pad_left

                squared_img = cv2.copyMakeBorder(
                    img, 
                    pad_top, pad_bottom, pad_left, pad_right, 
                    cv2.BORDER_CONSTANT, 
                    value=fill_color
                )

                # Handle filename logic
                if same_dir:
                    name, ext = os.path.splitext(filename)
                    out_filename = f"{name}_sq{ext}"
                else:
                    out_filename = filename

                output_path = os.path.join(output_directory, out_filename)
                cv2.imwrite(output_path, squared_img)
                print(f"Processed: {filename} -> {out_filename} ({side}x{side})")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Square images with custom fill and safety naming.")
    parser.add_argument("input_directory", help="Path to input images.")
    parser.add_argument("output_directory", help="Path to save output images.")
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--hex", help="Hex color code (e.g., FFFFFF).")
    group.add_argument("--gray", type=float, help="Grayscale percentage (0.0 to 1.0).")

    args = parser.parse_args()

    fill_bgr = (0, 0, 0)
    if args.hex:
        fill_bgr = hex_to_rgb(args.hex)
    elif args.gray is not None:
        fill_bgr = grayscale_to_bgr(args.gray)

    square_image(args.input_directory, args.output_directory, fill_bgr)