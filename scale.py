import os
import argparse
import cv2
import sys

def scale_images(input_directory, output_directory, factor=None, width=None, height=None):
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp')):
            try:
                image_path = os.path.join(input_directory, filename)
                img = cv2.imread(image_path)
                
                if img is None:
                    print(f"Error loading {filename}. Skipping.")
                    continue

                h, w = img.shape[:2]
                
                # Determine new dimensions
                if factor:
                    new_w, new_h = int(w * factor), int(h * factor)
                elif width:
                    new_w = width
                    new_h = int(h * (width / w))
                elif height:
                    new_h = height
                    new_w = int(w * (height / h))
                else:
                    new_w, new_h = w, h

                # Choose interpolation algorithm
                # INTER_AREA is best for shrinking, INTER_CUBIC is best for zooming
                interpolation = cv2.INTER_AREA if (new_w < w) else cv2.INTER_CUBIC

                scaled_img = cv2.resize(img, (new_w, new_h), interpolation=interpolation)

                output_path = os.path.join(output_directory, filename)
                cv2.imwrite(output_path, scaled_img)

                print(f"Resized {filename} from {w}x{h} to {new_w}x{new_h}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scale images by factor, width, or height.")
    
    parser.add_argument("input_directory", help="Path to input images.")
    parser.add_argument("output_directory", help="Path to save output images.")
    
    # Mutually exclusive group ensures you only pick one scaling method
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--factor", type=float, help="Scaling factor (e.g., 0.5 for half, 2.0 for double).")
    group.add_argument("--width", type=int, help="Target width in pixels (aspect ratio preserved).")
    group.add_argument("--height", type=int, help="Target height in pixels (aspect ratio preserved).")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    scale_images(
        args.input_directory, 
        args.output_directory, 
        factor=args.factor, 
        width=args.width, 
        height=args.height
    )