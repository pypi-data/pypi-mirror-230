import os
import traceback

class sc_commad:
    def __init__(self):
        pass

    @classmethod
    def log_error(cls, func):
        def decorator(*args, **kwargs):
            folder_name = "error"
            file_name = "python.error"
            # ตรวจสอบว่าโฟลเดอร์ my_folder มีอยู่หรือไม่
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)  # สร้างโฟลเดอร์ my_folder ถ้ายังไม่มี

            # ตรวจสอบว่าไฟล์ python.error อยู่ในโฟลเดอร์ my_folder หรือไม่
            file_path = os.path.join(folder_name, file_name)
            if not os.path.exists(file_path):
                # สร้างไฟล์ python.error ถ้ายังไม่มี
                with open(file_path, 'w') as file:
                    pass
            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                # รับข้อมูล traceback
                traceback_info = traceback.format_exc()

                # เขียนข้อมูล traceback ลงในไฟล์ python.error
                with open(file_path, 'a', encoding='utf-8') as file:
                    file.write("==== Traceback Information ====\n\n")
                    file.write(traceback_info)
                    file.write("\n\n")
                print(f"\033[31m{traceback_info}\033[0m")
        return decorator