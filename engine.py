from PIL import Image
import base64


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


def _generate_smart_key(method_code, length):
    raw_key = f"{method_code}:{length}"
    key_bytes = raw_key.encode("ascii")
    base64_bytes = base64.b64encode(key_bytes)
    return base64_bytes.decode("ascii")


def _parse_smart_key(key):
    try:
        base64_bytes = key.encode("ascii")
        raw_bytes = base64.b64decode(base64_bytes)
        raw_key = raw_bytes.decode("ascii")
        method_code, length = raw_key.split(":")
        return method_code, int(length)
    except:
        return None, None


def encrypt(img_path, text, output_path, method):
    method_code = 'r'
    if "Green" in method:
        method_code = 'g'
    elif "Blue" in method:
        method_code = 'b'
    elif "EOF" in method:
        method_code = 'e'

    length_str = ""

    if method_code == 'e':
        length_str = _encrypt_eof(img_path, text, output_path)
    else:
        channel = 0
        if method_code == 'g':
            channel = 1
        elif method_code == 'b':
            channel = 2
        length_str = _encrypt_lsb(img_path, text, output_path, channel)

    if length_str:
        return _generate_smart_key(method_code, length_str)
    return None


def decrypt(img_path, key):
    method_code, length = _parse_smart_key(key)

    if method_code is None or length is None:
        return "Ошибка: Неверный формат ключа"

    if method_code == 'e':
        return _decrypt_eof(img_path, length)

    channel = 0
    if method_code == 'g':
        channel = 1
    elif method_code == 'b':
        channel = 2

    return _decrypt_lsb(img_path, length, channel)


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


def _decrypt_lsb(img_path, length, channel_idx):
    img = Image.open(img_path)
    img = img.convert("RGB")
    pixels = img.load()
    width, height = img.size

    bits_to_read = length
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


def _decrypt_eof(img_path, length):
    with open(img_path, "rb") as f:
        content = f.read()

    hidden_bytes = content[-length:]
    try:
        return hidden_bytes.decode('utf-8')
    except:
        return "Ошибка декодирования"