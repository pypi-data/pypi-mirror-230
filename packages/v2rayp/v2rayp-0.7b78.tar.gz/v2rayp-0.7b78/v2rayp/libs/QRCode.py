import os

# Generate the QR code
import pyperclip
import PySimpleGUI as sg
import qrcode,platform
from libs.in_win import config_path, inside_windows


class QRCode:
    def __init__(self, data) -> None:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image = qr_image.resize((400, 400))

        # Save the QR code as an image file
        if inside_windows():
            image_file = f"{os.getenv('TEMP')}\\qrcode.png"  # Provide the desired filename and extension
        else:
            if platform.system()=="Darwin":
                temp_dir=f'{os.popen("echo $TMPDIR").read().strip()}'
            elif platform.system()=="Linux":
                temp_dir=f"{os.popen('MYTMPDIR=$(mktemp -d);echo $MYTMPDIR').read().strip()}"
            image_file = f"{temp_dir}/qrcode.png"  # Provide the desired filename and extension

        qr_image.save(image_file)

        # Create the PySimpleGUI window
        layout = [
            [sg.Image(image_file, key="-IMAGE-", size=(400, 400))],
            [sg.Multiline(data, size=(400, 5))],
            [sg.Button("Copy to Clipboard", key="copy"), sg.Button("Close")],
        ]

        window = sg.Window("QR Code", layout, size=(450, 550), keep_on_top=True)

        # Event loop to handle window events
        while True:
            event, _ = window.read()
            if event == sg.WINDOW_CLOSED or event == "Close":
                break
            elif "copy" in event:
                pyperclip.copy(data)

        window.close()


if __name__ == "__main__":
    data = "trojan://jJxdKznjbv@hels.ddns.net:2096?security=reality&sni=yahoo.com&fp=firefox&pbk=8LIuGGsdhR59qjyRALAmGKNuKVlyH3t8OqJmRRdyKl4&sid=92cd56b1&spx=%2F&type=grpc#reality-trojan-2096"  # Replace with your desired data
    QRCode(data)
