import click
import os
import subprocess
import pyperclip
import sys; sys.path.append('./')
from utils import *

# add a command for the user defined output file type (--otype)
@click.command()
@click.option('--otype', help='Output file type')

def main(otype):
    # Get path from clipboard
    in_path = pyperclip.paste().strip()

    if not os.path.exists(in_path):
        click.echo("Invalid file path from clipboard. Please copy a valid file path to convert.")
        return
    
    # Get file extension
    ext = in_path.rsplit('.', 1)[-1]

    if ext == 'mov': 
        out_path = convert_mov_to_mp4(in_path)
    elif ext == 'jpg':
        out_path = jpg_to_pdf(in_path)
    else:
        # raise a Not Implemented Error
        raise NotImplementedError(f"Conversion from {ext} to {otype} is not yet supported.")
    
    click.echo(f"Converted {in_path} to {out_path} !")

if __name__ == "__main__":
    main()