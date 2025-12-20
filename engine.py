from PIL import Image


def text_to_bin(text):
    binary = ''.join(format(ord(i), '08b') for i in text)
    return binary


def bin_to_text(binary):
    text = ""
    for i in range(0, len(binary), 8):
        byte = binary[i:i + 8]
        try:
            text += chr(int(byte, 2))
        except:
            pass
    return text


def save_encrypted_image(img_path, text, output_path):
    img = Image.open(img_path)
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
                r, g, b = pixels[x, y]

                bit = int(binary_text[index])
                r = (r & ~1) | bit

                pixels[x, y] = (r, g, b)
                index += 1
            else:
                img.save(output_path)
                return str(data_len)

    img.save(output_path)
    return str(data_len)


def get_decrypted_text(img_path, key):
    img = Image.open(img_path)
    pixels = img.load()
    width, height = img.size

    try:
        bits_to_read = int(key)
    except:
        return "Ошибка ключа"

    binary_data = ""
    index = 0

    for y in range(height):
        for x in range(width):
            if index < bits_to_read:
                r, g, b = pixels[x, y]
                binary_data += str(r & 1)
                index += 1
            else:
                break

    return bin_to_text(binary_data)