#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import traceback
import click
from PIL import Image
import json
import io
import os
import sys
import smtplib
from email.mime.text import MIMEText
import time

THUMBNAIL_SIZE = (320,320)

def email(addr):
    msg = MIMEText(f'{sys.argv}\n\n{traceback.format_exc(10)}')
    msg['Subject'] = 'ProjectM Error'
    msg['From'] = addr
    msg['To'] = addr
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def take_image(host, out_file, thumbnail=False):
    r = requests.get(host, stream=True)
    try:
        data = next(r.iter_content(200000))
    finally:
        r.close()
    header, ctype, clength, _, data = data.split(b'\r\n', 4)
    length = int(clength.split(b':')[1])
    fname, ext = os.path.splitext(out_file)
    with io.BytesIO(data[:length]) as bdat:
        with Image.open(bdat) as out_fh:
            out_fh.save(fname + ext)
            if thumbnail:
                out_fh.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
                out_fh.save(fname+'t'+ext)


@click.command(name='imager')
@click.argument('camera')
@click.argument('target')
@click.option('--email', 'addr', help='If provided, errors will be emailed to the given address')
@click.option('--delay', 'delay', type=float, default=0.0, help='Wait before taking the image')
@click.option('-t', '--thumbnail', is_flag=True)
def cli(camera, target, addr=None, delay=0, thumbnail=False):
    """Save frame of CAMERA stream to TARGET

    \b
    CAMERA - Address of the webcam stream
    TARGET - Full file path for where to write the file
    """
    try:
        time.sleep(delay)
        take_image(camera, target, thumbnail=thumbnail)
    except Exception as e:
        if addr:
            email(addr)
        else:
            traceback.print_exc()
        sys.exit(1)
    else:
        click.echo(f'Written to {target}')

if __name__ == '__main__':
    cli()
