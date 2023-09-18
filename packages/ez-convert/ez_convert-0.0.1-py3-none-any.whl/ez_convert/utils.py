import subprocess
from PIL import Image

def make_output_filename(in_path, otype):
    return in_path.rsplit('.', 1)[0] + '.' + otype

def convert_mov_to_mp4(mov_path):
    mp4_path = make_output_filename(mov_path, 'mp4')
    subprocess.run(['ffmpeg', '-i', mov_path, mp4_path])
    return mp4_path

def jpg_to_pdf(input_path):
    # specify output path
    output_path = make_output_filename(input_path, 'pdf')
    # Open the image file
    with Image.open(input_path) as img:
        # Convert and save as PDF
        img.save(output_path, "PDF", resolution=100.0, quality=95)
    return output_path