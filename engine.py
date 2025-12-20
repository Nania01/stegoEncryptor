from PIL import Image
import os


def text_to_bin(text):
    bytes_data = text.encode('utf-8')
    return ''.join(format(byte, '08b') for byte in bytes_data)


def bin_to_text(binary):
    bytes_list = []
    for i in range(0, len(binary), 8):
        byte_str = binary[i:i + 8]
        if len(byte_str) == 8:
            bytes_list.append(int(byte_str, 2))

    bytes_data = bytes(bytes_list)
    try:
        return bytes_data.decode('utf-8')
    except:
        return "Ошибка кодировки (неверный ключ или метод)"


def encrypt(img_path, text, output_path, method):
    if method == "EOF (End of File)":
        return _encrypt_eof(img_path, text, output_path)

    channel = 0
    if "Green" in method:
        channel = 1
    elif "Blue" in method:
        channel = 2

    return _encrypt_lsb(img_path, text, output_path, channel)


def decrypt(img_path, key, method):
    if method == "EOF (End of File)":
        return _decrypt_eof(img_path, key)

    channel = 0
    if "Green" in method:
        channel = 1
    elif "Blue" in method:
        channel = 2

    return _decrypt_lsb(img_path, key, channel)


def _encrypt_lsb(img_path, text, output_path, channel_idx):
    img = Image.open(img_path)
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    binary_text = text_to_bin(text)
    data_len = len(binary_text)

    if data_len > width * height:
        return None

    index = 0
    for y in range(height):
        for x in range(width):
            if index < data_len:
                p = list(pixels[x, y])

                bit = int(binary_text[index])
                p[channel_idx] = (p[channel_idx] & ~1) | bit

                pixels[x, y] = tuple(p)
                index += 1
            else:
                img.save(output_path)
                return str(data_len)

    img.save(output_path)
    return str(data_len)


def _decrypt_lsb(img_path, key, channel_idx):
    img = Image.open(img_path)
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    try:
        bits_to_read = int(key)
    except:
        return "Ошибка: Неверный ключ"

    binary_data = ""
    index = 0

    for y in range(height):
        for x in range(width):
            if index < bits_to_read:
                p = pixels[x, y]
                binary_data += str(p[channel_idx] & 1)
                index += 1
            else:
                break
    return bin_to_text(binary_data)


def _encrypt_eof(img_path, text, output_path):
    img = Image.open(img_path)
    img.save(output_path)

    text_bytes = text.encode('utf-8')
    with open(output_path, "ab") as f:
        f.write(text_bytes)

    return str(len(text_bytes))


def _decrypt_eof(img_path, key):
    try:
        byte_len = int(key)
    except:
        return "Ошибка: Неверный ключ"

    with open(img_path, "rb") as f:
        content = f.read()

    hidden_bytes = content[-byte_len:]
    try:
        return hidden_bytes.decode('utf-8')
    except:
        return "Ошибка декодирования"