from flask import request, send_file, url_for
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
import os
import io
import re
from io import BytesIO
import base64

# Allowed extensions (including PDF)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}


def register_subpages():
    app_subpages = [
    ]

    return app_subpages


def register_database(db, app):
    pass


def app_logic(current_user, db, User, GasamApp, page, return_data):
    if page == 'sign_or_watermark':
        send_data = {'db_init': register_database,
                     # 'file_path_coin_gif_choice_undecided': file_path_coin_gif_choice_undecided,
                     }

        return send_data


def json_logic(current_user, db, User, GasamApp, json_data, files_data):
    if json_data['js_function'] == 'sign_or_watermark_ini':
        return js_function_sign_or_watermark_ini(current_user, db, User, GasamApp, json_data, files_data)
    if json_data['js_function'] == 'sign_or_watermark_merge_images':
        return js_function_sign_or_watermark_merge_images(current_user, db, User, GasamApp, json_data, files_data)


def js_function_sign_or_watermark_ini(current_user, db, User, GasamApp, json_data, files_data):
    file_path_upload_dir = os.path.join('apps', 'sign_or_watermark', 'static', 'images', 'uploaded')

    # Delete previous  files
    delete_all_files(file_path_upload_dir)

    # Check if files_data is not empty and contains the 'image' key
    if files_data and 'image' in files_data:
        file = files_data['image']


        # Ensure the file is properly accessed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path_upload_image = os.path.join('apps', 'sign_or_watermark', 'static', 'images', 'uploaded', filename)
            json_data['img_src'] = url_for('serve_app_static', app_url='sign_or_watermark', filename=f'images/uploaded/{filename}')

            if is_pdf(file.filename):
                pass
            else:
                image = Image.open(file.stream)
                image.save(file_path_upload_image)
                return json_data
    else:
        # Handle the case where 'image' is not in files_data
        print("No image file found in files_data")
        return {'error': 'No image file found in the request'}

    return json_data

def js_function_sign_or_watermark_merge_images(current_user, db, User, GasamApp, json_data, files_data):

    # Sort keys in descending order
    sorted_keys = sorted(json_data.keys(), reverse=False)
    # Create a new dictionary with sorted keys
    json_data = {key: json_data[key] for key in sorted_keys}


    file_path_processed_dir = os.path.join('apps', 'sign_or_watermark', 'static', 'images', 'processed')
    delete_all_files(file_path_processed_dir)

    # retrieving the name of the uploaded file
    uploaded_folder_path = os.path.join('apps', 'sign_or_watermark', 'static', 'images', 'uploaded')
    uploaded_files = os.listdir(uploaded_folder_path)
    if uploaded_files:
        uploaded_filename = uploaded_files[0]
        uploaded_file_path = os.path.join('apps', 'sign_or_watermark', 'static', 'images', 'uploaded', uploaded_filename )

        if is_pdf(uploaded_filename):
            print('this is pdf')
        else:
            print('not pdf')
        # Open the base image
        base_image = Image.open(uploaded_file_path)  # Replace with your image path

        # Get the actual image dimensions from the client
        img_width = json_data['imgWidth']
        img_height = json_data['imgHeight']

        # Resize the base image to match the dimensions from the client
        base_image = base_image.resize((img_width, img_height), Image.LANCZOS)

        # Create a new RGBA image for watermarking
        watermarked_image = base_image.convert('RGBA')  # Ensure RGBA for transparency

        # Create a new image for the watermark
        overlay = Image.new('RGBA', (img_width, img_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        print(json_data)

        for key in json_data:

            # Process watermark text
            if key.endswith('_text'):

                # Calculate font size and position
                font_size = int(float(json_data[key]['fontSize']) * img_height)
                #font = ImageFont.truetype(json_data[key]['fontFamily'], font_size)


                font_path = os.path.join('apps', 'sign_or_watermark', 'static', 'fonts', f'{json_data[key]["fontFamily"]}.ttf')  # Adjust path as necessary
                try:
                    font = ImageFont.truetype(font_path, font_size)
                except OSError:
                    font = ImageFont.load_default()  # Load a default font if the specified font fails

                x = int(float(json_data[key]['x']) * img_width)
                y = int(float(json_data[key]['y']) * img_height)

                # Parse color and opacity
                color = parse_color(json_data[key]['color'])
                opacity = int(float(json_data[key]['opacity']) * 255)

                # Add alpha channel to color
                color_with_opacity = color + (opacity,)

                # Draw the watermark text
                draw.text((x, y), json_data[key]['text'], font=font, fill=color_with_opacity)

            # Process image elements
            if key.endswith('_image'):

                image_data = json_data[key]['url']
                x = int(float(json_data[key]['x'])  * img_width)
                y = int(float(json_data[key]['y'])  * img_height)
                width = int(float(json_data[key]['width']) * img_width)
                height = int(float(json_data[key]['height']) * img_height)

                # Decode the Base64 image string
                image_data = re.sub('^data:image/.+;base64,', '', image_data)
                image_bytes = BytesIO(base64.b64decode(image_data))

                # Open the uploaded image with PIL
                attached_image = Image.open(image_bytes)

                # Resize the uploaded image to the captured width and height
                attached_image = attached_image.resize((width, height))

                # Paste the image onto the overlay
                overlay.paste(attached_image, (x, y), attached_image.convert('RGBA'))

        # Composite the watermark with the base image
        watermarked_image = Image.alpha_composite(watermarked_image, overlay)

        processed_filename = f'processed_{uploaded_filename}'
        file_path_processed_image = os.path.join('apps', 'sign_or_watermark', 'static', 'images', 'processed', processed_filename)
        watermarked_image.save(file_path_processed_image)

        json_data['img_src'] = url_for('serve_app_static', app_url='sign_or_watermark', filename=f'images/processed/{processed_filename}')
        json_data['download_img'] = url_for('download_file', directory=file_path_processed_dir, filename=processed_filename)

    return json_data

def delete_all_files(directory):
    # List all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Check if it's a file (and not a directory)
        if os.path.isfile(file_path):
            os.remove(file_path)
            # print(f"Deleted file: {file_path}")


def is_pdf(filename):
    return os.path.splitext(filename)[1].lower() == '.pdf'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_color(color_string):
    """Parse color string to RGB tuple."""
    # Remove any whitespace and convert to lowercase
    color_string = color_string.strip().lower()

    # Check if it's a hex color
    if color_string.startswith('#'):
        # Remove the '#' and ensure we have 6 characters
        color_string = color_string[1:]
        if len(color_string) == 3:
            color_string = ''.join(c * 2 for c in color_string)
        elif len(color_string) != 6:
            raise ValueError(f"Invalid hex color: {color_string}")

        return tuple(int(color_string[i:i + 2], 16) for i in (0, 2, 4))

    # Check if it's an RGB tuple
    rgb_match = re.match(r'rgb\((\d+),\s*(\d+),\s*(\d+)\)', color_string)
    if rgb_match:
        return tuple(map(int, rgb_match.groups()))

    # If it's not hex or RGB, assume it's a named color
    # You might want to add a dictionary of named colors here
    # For now, we'll just return black as a fallback
    print(f"Warning: Unrecognized color format '{color_string}'. Using black.")
    return (0, 0, 0)