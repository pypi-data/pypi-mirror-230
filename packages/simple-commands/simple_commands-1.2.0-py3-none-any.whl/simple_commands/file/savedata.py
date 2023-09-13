import os
import shutil
import sqlite3
from datetime import datetime, timedelta
def loal(name,type):
    # หาพาธของไดเรกทอรี 'savedata' ภายในไลบรารี
    library_dir = os.path.dirname(os.path.abspath(__file__))
    savedata_dir = os.path.join(library_dir, 'savedata')
    file_path = os.path.join(savedata_dir, f"{name}.{type}")
    return file_path

def delete_loal(name,type):
    library_dir = os.path.dirname(os.path.abspath(__file__))
    savedata_dir = os.path.join(library_dir, 'deletedata')
    file_path = os.path.join(savedata_dir, f"{name}.{type}")
    return file_path

def delete_loal_db():
    library_dir = os.path.dirname(os.path.abspath(__file__))
    savedata_dir = os.path.join(library_dir, 'deletedata/deleted_files.db')
    return savedata_dir

def Retrieve_log(name, path, type="txt"):
    shutil.copy(loal(name,type), path)

def create_log(name, type="txt"):
    try:
        with open(loal(name,type), 'x'):
            pass
    except Exception:
        return

def adddata_to_log(name, text, type="txt"):
    with open(loal(name,type), 'a', encoding='utf-8') as file:
        # เขียนข้อมูลลงในไฟล์
        file.write(text)

def delete_log(name, type="txt"): 
    shutil.move(loal(name,type), delete_loal(name,type))
    # เชื่อมต่อกับฐานข้อมูล SQLite
    db_connection = sqlite3.connect(delete_loal_db())
    db_cursor = db_connection.cursor()
    deletion_time_seconds = int(datetime.now().timestamp())
    db_cursor.execute("INSERT INTO deleted_files (file_name, deletion_time) VALUES (?, ?)", (name, deletion_time_seconds))
    db_connection.commit()
    db_connection.close()

def recover_log(name, type="txt"):
    db_connection = sqlite3.connect(delete_loal_db())
    db_cursor = db_connection.cursor()
    # ค้นหาไฟล์ที่ผู้ใช้ต้องการเรียกคืน
    db_cursor.execute("SELECT deletion_time FROM deleted_files WHERE file_name = ?", (name,))
    file_info = db_cursor.fetchone()
    if file_info is not None:
        deletion_time = datetime.fromtimestamp(file_info[0])
        current_time = datetime.now()     
        # ตรวจสอบเวลาลบของไฟล์
        if current_time - deletion_time > timedelta(days=30):
            # ถ้าเวลาการลบเกิน 30 วัน ลบไฟล์ทิ้งทันที
            os.remove(delete_loal(name,type))
        else:
            # ถ้าไม่เกิน 30 วัน ย้ายไฟล์ไปยังโฟลเดอร์ savedata
            shutil.move(delete_loal(name,type), loal(name,type))
    # ปิดการเชื่อมต่อกับฐานข้อมูลเมื่อไม่ใช้งาน
    db_connection.close()

def list_log(name=None,type="txt"):
    if name == None:
        library_dir = os.path.dirname(os.path.abspath(__file__))
        savedata_dir = os.path.join(library_dir, 'savedata')
        return os.listdir(savedata_dir)
    else:
        return os.listdir(loal(name, type))

def list_log_delete(name,type="txt"):
    if name == None:
        library_dir = os.path.dirname(os.path.abspath(__file__))
        savedata_dir = os.path.join(library_dir, 'savedata')
        return os.listdir(savedata_dir)
    else:
        return os.listdir(loal(name, type))

def return_data_log(name, type="txt"):
    with open(loal(name, type), 'r', encoding='utf-8') as file:
        return file.read()

def delete_text_in_log(name, text_to_delete, type="txt"):
    # อ่านข้อมูลทั้งหมดในไฟล์ log
    with open(loal(name, type), 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # ค้นหาและลบข้อความที่ผู้ใช้ต้องการออก
    modified_lines = [line for line in lines if text_to_delete not in line]

    # เขียนข้อมูลใหม่ลงในไฟล์ log
    with open(loal(name, type), 'w', encoding='utf-8') as file:
        file.writelines(modified_lines)

def delete_alltext_log(name, type="txt"):

    with open(loal(name, type), 'w', encoding='utf-8') as file:
        file.write('')