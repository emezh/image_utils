import os
import argparse
import cv2
import sys

def crop_and_rotate_images(input_directory, output_directory, crop_box, rotation=0, count=None, use_offset=False):
    # Ensure output directory exists using makedirs
    os.makedirs(output_directory, exist_ok=True)

    processed_count = 0
# Sort filenames to ensure consistent ordering (e.g., alphabetical)
    filenames = sorted(os.listdir(input_directory))

    # Loop through each file in the input directory
    for filename in filenames:
        # Check if we have reached the specified count limit
        if count is not None and processed_count >= count:
            break

        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):  # Check for image files
            try:
                # Construct the full input image path
                image_path = os.path.join(input_directory, filename)

                # Read the image using OpenCV
                img = cv2.imread(image_path)
                if img is None:
                    print(f"Error loading image {filename}. Skipping.")
                    continue


                # Apply rotation if specified (90, 180, or 270 degrees clockwise)
                if rotation == 90:
                    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                elif rotation == 180:
                    img = cv2.rotate(img, cv2.ROTATE_180)
                elif rotation == 270:
                    # 270 degrees clockwise is equivalent to 90 degrees counter-clockwise
                    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

                # Check the size of the image
                height, width = img.shape[:2]
                #if height != 6000 or width != 4000:
                #    print(f"Image {filename} has dimensions {width}x{height}. Skipping processing.")
                #    continue

                #print(f"{width}x{height};   {crop_box}")
                box = crop_box
                if use_offset:
                    middle_x, bottom_y, final_w, final_h = crop_box
                    
                    box = ( middle_x - final_w//2, bottom_y - final_h,
                            middle_x + final_w//2, bottom_y)
                
                #print(f"                   {box}")

                # Crop the image using the provided crop box
                cropped_img = img[box[1]:box[3], box[0]:box[2]]

                # Construct the full output image path
                output_path = os.path.join(output_directory, filename)

                # Save the processed image to the output directory
                cv2.imwrite(output_path, cropped_img)

                processed_count += 1
                print(f"Processed image {(height, width)} with rotation {rotation}° saved as: {output_path}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Crop and optionally rotate images in a directory.")
    
    # Adding arguments
    parser.add_argument("input_directory", help="Path to the input directory containing images.")
    parser.add_argument("output_directory", help="Path to the output directory to save processed images.")
    parser.add_argument("crop_box", nargs=4, type=int, 
                        help="Crop box dimensions as four integers: left upper right lower.")
    parser.add_argument("--offset", action="store_true",
                        help="Treat crop box params as middle_x bottom_y final_width final_height")
    parser.add_argument("--rotate", type=int, choices=[0, 90, 180, 270], default=0,
                        help="Rotation angle clockwise (90, 180, 270). Default is 0.")
    parser.add_argument("--count", type=int, default=None,
                        help="Process only the first N images from the folder.")
                        
    # Check if no parameters were provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Parse the arguments
    args = parser.parse_args()

    # Unpack arguments
    input_dir = args.input_directory
    output_dir = args.output_directory
    crop_box = tuple(args.crop_box)
    rotation = args.rotate
    count = args.count

    # Call the crop and rotate function
    crop_and_rotate_images(input_dir, output_dir, crop_box, rotation, count, args.offset)