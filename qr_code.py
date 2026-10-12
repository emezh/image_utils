import argparse
import sys
import qrcode
from PIL import Image, ImageDraw, ImageFont

def generate_qr(
    url, 
    output_file, 
    icon_path=None, 
    bottom_text=None, 
    bg_color="#C0C0C0", 
    fill_color="black"
):
    # 1. Configure QR code with high error correction to allow center logos
    qr = qrcode.QRCode(
        version=2,  
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # ~30% error correction
        box_size=10,
        border=2,
    )
    
    qr.add_data(url)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color=fill_color, back_color=bg_color).convert("RGBA")
    
    # 2. Add custom icon in the center if provided
    if icon_path:
        try:
            icon = Image.open(icon_path).convert("RGBA")
            icon_size = qr_img.width // 4
            icon = icon.resize((icon_size, icon_size), Image.Resampling.LANCZOS)
            
            pos_x = (qr_img.width - icon.width) // 2
            pos_y = (qr_img.height - icon.height) // 2
            
            padding = 8
            bg_patch = Image.new(
                "RGBA", 
                (icon.width + padding * 2, icon.height + padding * 2), 
                bg_color
            )
            patch_x = pos_x - padding
            patch_y = pos_y - padding
            qr_img.paste(bg_patch, (patch_x, patch_y), bg_patch)
            qr_img.paste(icon, (pos_x, pos_y), icon)
            
        except FileNotFoundError:
            print(f"Error: Icon file '{icon_path}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error loading icon: {e}", file=sys.stderr)
            sys.exit(1)

    # 3. Create the card layout if bottom text is provided
    if bottom_text:
        # Load font first to calculate dynamic height for multi-line text
        try:
            font = ImageFont.truetype("arial.ttf", size=28)
        except IOError:
            font = ImageFont.load_default()

        # Handle multi-line strings by replacing literal "\n" escape sequences with actual newlines
        formatted_text = bottom_text.replace("\\n", "\n")

        padding = 40
        white_box_margin = 25
        box_width = qr_img.width + (white_box_margin * 2)
        box_height = qr_img.height + (white_box_margin * 2)

        # Create a temporary draw object to measure multi-line text size
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)
        
        # multiline_textbbox calculates bounding box for multiple lines with spacing
        text_bbox = dummy_draw.multiline_textbbox((0, 0), formatted_text, font=font, spacing=6, align="center")
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Dynamically size the banner area based on how many lines of text there are
        banner_height = max(120, text_height + 50)
        
        card_width = qr_img.width + (padding * 2)
        card_height = qr_img.height + banner_height + (padding * 2)
        
        # Create card canvas
        card = Image.new("RGBA", (card_width, card_height), (35, 30, 28, 255))
        
        # White container box for QR code
        white_box = Image.new("RGBA", (box_width, box_height), "white")
        white_box.paste(qr_img, (white_box_margin, white_box_margin), qr_img)
        
        card_x = (card_width - box_width) // 2
        card_y = padding
        card.paste(white_box, (card_x, card_y))
        
        # Draw multi-line text centered in the banner area
        draw = ImageDraw.Draw(card)
        text_x = (card_width - text_width) // 2
        text_y = card_y + box_height + ((banner_height - text_height) // 2)
        
        draw.multiline_text(
            (text_x, text_y), 
            formatted_text, 
            fill="white", 
            font=font, 
            spacing=6, 
            align="center"
        )
        
        final_img = card
    else:
        final_img = qr_img

    # 4. Save output image
    if output_file.lower().endswith(('.jpg', '.jpeg')):
        final_img = final_img.convert("RGB")
        
    final_img.save(output_file)
    print(f"Success: Advanced QR code saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a stylized QR code with optional center icon and multi-line bottom text.")
    parser.add_argument("url", help="The target URL or text to encode")
    parser.add_argument("--icon", required=False, default=None, help="Path to center logo/icon image")
    parser.add_argument("--text", required=False, default=None, help="Optional text for bottom banner. Use '\\n' for new lines.")
    parser.add_argument("--out", required=False, default="styled_qr.png", help="Output file name")
    
    args = parser.parse_args()
    generate_qr(args.url, args.out, icon_path=args.icon, bottom_text=args.text)