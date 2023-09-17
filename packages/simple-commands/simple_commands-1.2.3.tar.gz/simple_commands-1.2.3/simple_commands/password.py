import random
import string

def generate_random_password(length=12, use_uppercase=True, use_digits=True, use_symbols=True):
    # ตัวแปรที่ใช้เก็บตัวอักษรที่ใช้สร้างรหัสผ่าน
    characters = string.ascii_lowercase  # ใช้ตัวอักษรตัวเล็กเป็นค่าเริ่มต้น

    # เพิ่มตัวอักษรตัวใหญ่ (ถ้าต้องการ)
    if use_uppercase:
        characters += string.ascii_uppercase

    # เพิ่มตัวเลข (ถ้าต้องการ)
    if use_digits:
        characters += string.digits

    # เพิ่มสัญลักษณ์ (ถ้าต้องการ)
    if use_symbols:
        characters += string.punctuation

    # สุ่มเลือกตัวอักษรตามความยาวที่กำหนด
    password = ''.join(random.choice(characters) for _ in range(length))

    return password

def generate_random_password_with_uppercase(length=12):
    return ''.join(random.choice(string.ascii_uppercase) for _ in range(length))

def generate_random_password_with_digits(length=12):
    return ''.join(random.choice(string.digits) for _ in range(length))

def generate_random_password_with_symbols(length=12):
    return ''.join(random.choice(string.punctuation) for _ in range(length))
