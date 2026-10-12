import argparse
import sys
import qrcode
from PIL import Image

def generate_qr(url, output_file, background_img_path=None, bg_color="white"):
    # 1. Configure the QR code properties
    qr = qrcode.QRCode(
        version=1,                   # Controls the size (1 is 21x21 matrix, up to 40)
        error_correction=qrcode.constants.ERROR_CORRECT_M,  # About 15% error tolerance
        box_size=10,                 # How many pixels each "box" of the QR code is
        border=2,                    # Thickness of the border (minimum is 4)
    )

    # 2. Add your text or URL data
    qr.add_data(url)
    qr.make(fit=True)

    if background_img_path:
        # 3. Create the QR code image with a transparent background
        # Using 'transparent' background allows your image to show through the borders
        qr_img = qr.make_image(fill_color="black", back_color="transparent").convert("RGBA")

        # 4. Load the background image file
        try:
            img = Image.open(background_img_path).convert("RGBA")
        except FileNotFoundError:
            print(f"Error: The background image file '{background_img_path}' was not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading background image: {e}", file=sys.stderr)
            sys.exit(1)

        # 5. Position and blend the QR code onto the background
        # Option A: Resize the background to match the QR code size
        # img = img.resize(qr_img.size)
        # img.paste(qr_img, (0, 0), qr_img)
        
        # Option B: Center a smaller QR code on top of a larger background image
        if img.width < qr_img.width or img.height < qr_img.height:
            # If background is too small, shrink the QR code to fit it
            scale_factor = min(img.width, img.height) // 2
            qr_img = qr_img.resize((scale_factor, scale_factor), Image.Resampling.LANCZOS)

        # Calculate center position coordinates
        x_pos = (img.width - qr_img.width) // 2
        y_pos = (img.height - qr_img.height) // 2

        # Paste the QR code onto the background (using qr_img as the mask preserves transparency)
        img.paste(qr_img, (x_pos, y_pos), qr_img)

        # 6. Save the final image
        # If saving as JPEG, convert back to RGB first. PNG supports RGBA directly.
        if output_file.lower().endswith(('.jpg', '.jpeg')):
            img = img.convert("RGB")
            
        img.save(output_file)
        print(f"Success: Combined image saved to {output_file}")

    else:

        # Create the image with custom styling
        # Note: 'background_img' from your arguments specifies 'back_color' here
        try:
            img = qr.make_image(fill_color="black", back_color=bg_color).convert("RGB")
        except ValueError:
            print(f"Error: '{background_img}' is not a recognized color name.", file=sys.stderr)
            sys.exit(1)

    img.save(output_file)
    print(f"Success: QR Code saved to {output_file}")

if __name__ == "__main__":
    # Set up argument parsing 
    parser = argparse.ArgumentParser(description="Generate a customized QR code from a URL.")
    
    # Positional argument for the URL
    parser.add_argument("url", help="The target URL or text to encode in the QR code")
    
    # Optional keyword arguments matching your signature
    parser.add_argument("--bg_color", required=False, default="white", help="The background color for the QR code (e.g., 'white', 'yellow')")
    parser.add_argument("--image", required=False, default=None, help="The background image for the QR code (e.g., 'background.png'). If provided, this will override the background color.")
    parser.add_argument("--out", required=False, default="qr.png", help="The output file name for the generated image (e.g., 'qr.png')")
    
    args = parser.parse_args()
    
    # Execute generator
    generate_qr(args.url, args.out, args.image, args.bg_color)
