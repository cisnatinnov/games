import jwt
import bcrypt
import re
import os
import json
import random
import string
import time

# -----------------------
# Password hashing
# -----------------------
def gen_bcrypt(password: str) -> str:
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(8))
        return hashed.decode('utf-8')
    except Exception as e:
        print(e)
        return None # type: ignore

def compare(pass_hash: str, password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), pass_hash.encode('utf-8'))
    except Exception as e:
        print(e)
        return False

# -----------------------
# JWT
# -----------------------
def gen_jwt(payload: dict) -> str:
    try:
        secret = os.getenv("JWT_SECRET", "default_secret")
        token = jwt.encode(payload, secret, algorithm="HS256") # type: ignore
        return token
    except Exception as e:
        print(e)
        return None # type: ignore

def verify_jwt(token: str):
    try:
        secret = os.getenv("JWT_SECRET", "default_secret")
        decoded = jwt.decode(token, secret, algorithms=["HS256"]) # type: ignore
        return decoded
    except Exception as e:
        print(e)
        return None

# -----------------------
# Validation
# -----------------------
def validate_email(email: str) -> bool:
    return bool(re.match(r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', email))

def valid_password(password: str) -> bool:
    return bool(re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password))

# -----------------------
# OTP
# -----------------------
def otp(length: int) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# -----------------------
# Binary/Hex conversion
# -----------------------
def bin2hex(s: str) -> str:
    return ''.join(format(ord(c), '02x') for c in s)

def hex2bin(s: str):
    try:
        return ''.join(chr(int(s[i:i+2], 16)) for i in range(0, len(s), 2))
    except:
        return False

# -----------------------
# Morse Code
# -----------------------
def decode_morse(morse_code: str) -> str:
    ref = {
        '.-': 'a', '-...': 'b', '-.-.': 'c', '-..': 'd',
        '.': 'e', '..-.': 'f', '--.': 'g', '....': 'h',
        '..': 'i', '.---': 'j', '-.-': 'k', '.-..': 'l',
        '--': 'm', '-.': 'n', '---': 'o', '.--.': 'p',
        '--.-': 'q', '.-.': 'r', '...': 's', '-': 't',
        '..-': 'u', '...-': 'v', '.--': 'w', '-..-': 'x',
        '-.--': 'y', '--..': 'z', '.----': '1', '..---': '2',
        '...--': '3', '....-': '4', '.....': '5', '-....': '6',
        '--...': '7', '---..': '8', '----.': '9', '-----': '0'
    }
    return ' '.join(
        ''.join(ref.get(symbol, '') for symbol in word.split(' '))
        for word in morse_code.strip().split('   ')
    )

def encode_morse(text: str) -> str:
    alphabet = {
        'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..',
        'e': '.', 'f': '..-.', 'g': '--.', 'h': '....',
        'i': '..', 'j': '.---', 'k': '-.-', 'l': '.-..',
        'm': '--', 'n': '-.', 'o': '---', 'p': '.--.',
        'q': '--.-', 'r': '.-.', 's': '...', 't': '-',
        'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-',
        'y': '-.--', 'z': '--..', ' ': '/',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..',
        '9': '----.', '0': '-----'
    }
    return ' '.join(alphabet.get(ch.lower(), '') for ch in text)

# -----------------------
# Local storage simulation
# -----------------------
local_storage_file = "localstorage.json"

def _load_storage():
    if os.path.exists(local_storage_file):
        with open(local_storage_file, "r") as f:
            return json.load(f)
    return {}

def _save_storage(data):
    with open(local_storage_file, "w") as f:
        json.dump(data, f)

def set_with_expiry(key, value):
    item = {
        "value": value,
        "expiry": int(time.time() * 1000)  # milliseconds
    }
    data = _load_storage()
    data[key] = item
    _save_storage(data)

def more_than_8_hours(now, date):
    eight_hours_ms = 1000 * 60 * 60 * 8
    return date < (now - eight_hours_ms)

def get_with_expiry(key):
    try:
        data = _load_storage()
        item = data.get(key)
        if not item:
            return None
        now = int(time.time() * 1000)
        if more_than_8_hours(now, item["expiry"]):
            data.pop(key, None)
            _save_storage(data)
            return None
        return item["value"]
    except Exception as e:
        print(e)
        return None
