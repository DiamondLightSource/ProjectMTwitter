#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import traceback
import click
from PIL import Image
import json
import io
import sys
import smtplib
from email.mime.text import MIMEText


def email(addr):
    msg = MIMEText(f'{sys.argv}\n\n{traceback.format_exc(10)}')
    msg['Subject'] = 'ProjectM Error'
    msg['From'] = addr
    msg['To'] = addr
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()


def take_image(host, out_file):
    r = requests.get(host, stream=True)
    try:
        data = next(r.iter_content(100000))
    finally:
        r.close()
    header, ctype, clength, _, data = data.split(b'\r\n', 4)
    length = int(clength.split(b':')[1])
    with io.BytesIO(data[:length]) as bdat:
        with Image.open(bdat) as out_fh:
            out_fh.save(out_file)


@click.command(name='imager')
@click.argument('camera')
@click.argument('target')
@click.option('--email', 'addr', help='If provided, errors will be emailed to the given address')
def cli(camera, target, addr=None):
    """Save frame of CAMERA stream to TARGET

    \b
    CAMERA - Address of the webcam stream
    TARGET - Full file path for where to write the file
    """
    try:
        take_image(camera, target)
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
