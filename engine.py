import random
import hashlib
import base64
from PIL import Image
from cryptography.fernet import Fernet


def _get_fernet_key(password):
    key = hashlib.sha256(password.encode()).digest()
    return base64.urlsafe_b64encode(key)


def _get_shuffled_pixels(width, height, password):
    pixels_coords = [(x, y) for y in range(height) for x in range(width)]
    random.seed(password)
    random.shuffle(pixels_coords)
    return pixels_coords


def get_image_capacity(img_path):
    try:
        img = Image.open(img_path)
        return img.width * img.height
    except:
        return 0


def calculate_encrypted_size(text):
    if not text: return 0
    try:
        dummy_key = base64.urlsafe_b64encode(b'0' * 32)
        f = Fernet(dummy_key)
        encrypted = f.encrypt(text.encode('utf-8'))
        return len(encrypted) * 8
    except:
        return len(text.encode('utf-8')) * 8 * 2


def encrypt(img_path, text, password, output_path, method):
    try:
        f = Fernet(_get_fernet_key(password))
        encrypted_data = f.encrypt(text.encode('utf-8'))
        binary_list = list(''.join(format(byte, '08b') for byte in encrypted_data))
    except Exception:
        return None

    img = Image.open(img_path).convert("RGB")
    pixels = img.load()
    width, height = img.size

    if len(binary_list) > width * height:
        return "TooLarge"

    bit_indices = list(range(len(binary_list)))
    random.seed(password)
    random.shuffle(bit_indices)

    shuffled_bits = [None] * len(binary_list)
    for i, original_idx in enumerate(bit_indices):
        shuffled_bits[i] = binary_list[original_idx]

    coords = _get_shuffled_pixels(width, height, password)
    random.seed(password)

    for i, bit in enumerate(shuffled_bits):
        x, y = coords[i]
        p = list(pixels[x, y])

        if method == "LSB (Multi)":
            channel_idx = random.randint(0, 2)
            code = 'm'
        else:
            channel_idx = 0
            if "Green" in method:
                channel_idx = 1
            elif "Blue" in method:
                channel_idx = 2
            code = method[5].lower() if "LSB" in method else 'r'

        p[channel_idx] = (p[channel_idx] & ~1) | int(bit)
        pixels[x, y] = tuple(p)

    img.save(output_path)
    final_code = 'm' if method == "LSB (Multi)" else code
    return _generate_smart_key(final_code, len(binary_list))


def decrypt(img_path, key, password):
    method_code, length = _parse_smart_key(key)
    if not method_code or not length: return "Неверный ключ"

    img = Image.open(img_path).convert("RGB")
    pixels = img.load()
    width, height = img.size

    coords = _get_shuffled_pixels(width, height, password)
    random.seed(password)

    extracted_shuffled_bits = []
    for i in range(length):
        x, y = coords[i]
        p = pixels[x, y]

        if method_code == 'm':
            channel_idx = random.randint(0, 2)
        else:
            channel_idx = {'r': 0, 'g': 1, 'b': 2}.get(method_code, 0)

        extracted_shuffled_bits.append(str(p[channel_idx] & 1))

    bit_indices = list(range(length))
    random.seed(password)
    random.shuffle(bit_indices)

    original_bits = [None] * length
    for i, original_idx in enumerate(bit_indices):
        original_bits[original_idx] = extracted_shuffled_bits[i]

    binary_data = "".join(original_bits)

    try:
        byte_list = [int(binary_data[i:i + 8], 2) for i in range(0, len(binary_data), 8)]
        encrypted_bytes = bytes(byte_list)
        f = Fernet(_get_fernet_key(password))
        return f.decrypt(encrypted_bytes).decode('utf-8')
    except:
        return "Ошибка: Неверный пароль или данные повреждены"


def _encrypt_eof(img_path, text, output_path, password):
    try:
        f = Fernet(_get_fernet_key(password))
        encrypted_data = f.encrypt(text.encode('utf-8'))

        img = Image.open(img_path)
        img.save(output_path)

        with open(output_path, "ab") as f_file:
            f_file.write(encrypted_data)
        return len(encrypted_data)
    except:
        return None


def _decrypt_eof(img_path, length, password):
    try:
        with open(img_path, "rb") as f_file:
            content = f_file.read()

        encrypted_data = content[-length:]
        f = Fernet(_get_fernet_key(password))
        return f.decrypt(encrypted_data).decode('utf-8')
    except:
        return "Ошибка: Неверный пароль или файл поврежден"


def _generate_smart_key(method_code, length):
    raw_key = f"{method_code}:{length}"
    return base64.b64encode(raw_key.encode()).decode()


def _parse_smart_key(key):
    try:
        raw = base64.b64decode(key).decode().split(':')
        return raw[0], int(raw[1])
    except:
        return None, None