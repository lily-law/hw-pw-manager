import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import json


def get_hash_dir(pin, set_error):
    password = bytes(pin, 'utf-8')
    for hash in [x[0] for x in os.walk(f"./__appdata")]:
        if bcrypt.checkpw(password, hash):
            hash_dir = hash
    if not hash_dir:
        hash = bcrypt.hashpw(password, bcrypt.gensalt(14))
        # TODO make dir
    return hash_dir


app_data_path = "./__appdata__/"
salt_file_name = ".salt"

def get_salt(hash_dir, set_error):
    if os.path.exists(f"{app_data_path}{hash_dir}/{salt_file_name}"):
        try:
            f = open(f"{app_data_path}{hash_dir}/{salt_file_name}", "r")
            data = f.read()
            salt = bytes(data, 'utf-16')
        except:
            set_error('Unable to read salt!')
        finally:
            f.close()
    else:
        try:
            salt = os.urandom(16)
            f = open(f"{app_data_path}{hash_dir}/{salt_file_name}", "w")
            data = salt.decode("utf-16")
            f.write(data)
        except:
            if os.path.exists(f"{app_data_path}{hash_dir}/{salt_file_name}"):
                os.remove(f"{app_data_path}{hash_dir}/{salt_file_name}")
            set_error('Unable to save salt!')
        finally:
            f.close()
    return salt

class Entries:
    def __init__(self, pin, set_error):
        self.hash_dir = get_hash_dir(pin, set_error)
        self.set_error = set_error
        salt = get_salt(self.hash_dir, set_error)
        password = bytes(pin, 'utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.f = Fernet(key)

    def encrypt(self, data):
        token = self.f.encrypt(bytes(data, 'utf-16'))
        return token

    def decrypt(self, token):
        data = self.f.decrypt(token).decode('utf-16')
        return data
    
    def load(self): 
        if os.path.exists(f"{app_data_path}{self.hash_dir}/.dat"):
            try:
                f = open(f"{app_data_path}{self.hash_dir}/.dat", "r")
                data = f.read()
                try:
                    # decrypt data
                    data = self.decrypt(data)
                except:
                    self.set_error('Unable to decrypt data, this should not be happening! :S')
                # JSON parse data
                entries = json.loads(data)
                # set entries into state
                return entries
            except:
                self.set_error('Oh s***! Error opening file! :(')
            finally:
                f.close()
        else:
            return []

    def save(self, entries):
        try:
            # JSON stringify state['entries']
            data = json.dumps(state['entries'])
            try:
                # encrypt data
                data = self.encrypt(data)
                try:
                    # backup data to tmp file
                    tmp_f = open(f".tmp", "w")
                    tmp_f.write(data) 
                    try: 
                        # write over old file
                        f = open(f".dat", "w")
                        f.write(data)
                        # delete tmp backup file
                        if os.path.exists(f".tmp"):
                            os.remove(f".tmp")
                        return True
                    except:
                        try: 
                            # Recover using tmp file and warn user
                            if os.path.exists(f".dat"):
                                os.remove(f".dat")
                            os.rename(f".tmp", f".dat")
                            self.set_error(f"Recovered using a tmp backup file. SD card might be out of space or corrupted. Backing up is highly recommeded.")
                        except:
                            self.set_error(f"File write failed! sd card might be out of space or corrupted")
                    finally:
                        f.close()
                except:
                    self.set_error('Unable to make backup file, sd card might be out of space or corrupted!')
                finally:
                    tmp_f.close()
            except:
                self.set_error('Something went wrong while trying to encrypt data. No changes were saved.')
        except:
            self.set_error('Unable to convert data to JSON string. No changes were saved.')
