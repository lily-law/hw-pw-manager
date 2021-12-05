import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import bcrypt
import json
import re
import urllib.parse
import binascii

base_dir = "./"
app_data_dir = os.path.join(base_dir, "__appdata__/")
if not app_data_dir: # make dir if it doesn't exist
        os.mkdir(app_data_dir)
salt_file_name = ".salt"

hash_cost = 12
valid_hash = re.compile(rf"^\$\d\w\${hash_cost}")

def get_hash_dir(user, set_error):
    b_user = bytes(user, 'utf-8')
    is_new_user = False
    hash_dir = False
    for dirs in [x[1] for x in os.walk(app_data_dir)]:
        for hash_path in dirs:
            hash = urllib.parse.unquote(hash_path, encoding='utf-8')
            if valid_hash.search(hash):
                b_hash = bytes(hash, 'utf-8')
                if bcrypt.checkpw(b_user, b_hash):
                    hash_path = urllib.parse.quote(hash,safe="")
                    hash_dir = os.path.join(app_data_dir, hash_path)
    if not hash_dir:
        b_hash = bcrypt.hashpw(b_user, bcrypt.gensalt(hash_cost))
        hash = b_hash.decode('utf-8')
        is_new_user = True
        # make dir
        hash_path = urllib.parse.quote(hash,safe="")
        hash_dir = os.path.join(app_data_dir, hash_path)
        os.mkdir(hash_dir)
    if not os.path.exists(hash_dir):
        set_error(f"Something went wrong, invalid hash_dir path: {hash_dir}")
    return { 'hash_dir': hash_dir, 'is_new_user': is_new_user }


def get_salt(hash_dir, set_error):
    salt_path = os.path.join(hash_dir, salt_file_name)
    if os.path.exists(salt_path): # read in salt
        try:
            f = open(salt_path, "r")
            data = f.read()
            salt = binascii.unhexlify(data)
        except:
            set_error('Unable to read salt!')
        finally:
            f.close()
    else: # create new salt
        try:
            f = open(salt_path, "w")
            salt = binascii.hexlify(os.urandom(16))
            data = binascii.hexlify(salt).decode()
            f.write(data)
        except:
            if os.path.exists(salt_path):
                os.remove(salt_path)
            set_error('Unable to save salt!')
        finally:
            f.close()
    return salt

class Entries:
    def __init__(self, pin, user, set_error):
        user_data = get_hash_dir(user, set_error)
        self.hash_dir = user_data['hash_dir']
        self.set_error = set_error
        salt = get_salt(self.hash_dir, set_error)
        b_pin = bytes(pin, 'utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(b_pin))
        self.f = Fernet(key)
        self.valid = False

        pin_hash_path = os.path.join(self.hash_dir, ".eph")
        if user_data['is_new_user']: # save encrypted pin hash
            try:
                f = open(pin_hash_path, "w")
                b_hash = bcrypt.hashpw(b_pin, bcrypt.gensalt(14))
                hash = b_hash.decode("utf-8")
                eph = self.encrypt(hash)
                data = eph.decode("utf-8")
                f.write(data)
                self.valid = True
            except:
                if os.path.exists(pin_hash_path):
                    os.remove(pin_hash_path)
                set_error('Unable to save encrypted pin hash!')
            finally:
                f.close()
        elif os.path.exists(pin_hash_path): # check pin is correct
            b_token = False
            b_hash = False
            try:
                hash = False
                f = open(pin_hash_path, "r")
                token = f.read()
                b_token = bytes(token, 'utf-8')
            except:
                set_error('Error opening pin hash')
            finally:
                f.close()
            try:
                data = self.decrypt(b_token)
                b_hash = bytes(data, 'utf-8')
            except:
                self.valid = False # does not decrypt with given pin
            if b_hash and bcrypt.checkpw(b_pin, b_hash):
                self.valid = True
        else: 
            set_error('Unable to locate encrypted pin hash!')

    def encrypt(self, data):
        token = self.f.encrypt(bytes(data, 'utf-8'))
        return token

    def decrypt(self, token):
        b_data = self.f.decrypt(token)
        data = b_data.decode('utf-8')
        return data
    
    def load(self): 
        dat_path = os.path.join(self.hash_dir, '.dat')
        if os.path.exists(dat_path):
            try:
                f = open(dat_path, "r")
                token = f.read()
                try:
                    # decrypt data
                    b_token = bytes(token, 'utf-8')
                    data = self.decrypt(b_token)
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
        dat_path = os.path.join(self.hash_dir, '.dat')
        tmp_path = os.path.join(self.hash_dir, '.tmp')
        try:
            # JSON stringify state['entries']
            data = json.dumps(entries)
            try:
                # encrypt data
                b_token = self.encrypt(data)
                token = b_token.decode('utf-8')
                try:
                    # backup data to tmp file
                    tmp_f = open(tmp_path, "w")
                    tmp_f.write(token) 
                    try: 
                        # write over old file
                        f = open(dat_path, "w")
                        f.write(token)
                        # delete tmp backup file
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                        return True
                    except:
                        try: 
                            # Recover using tmp file and warn user
                            if os.path.exists(dat_path):
                                os.remove(dat_path)
                            os.rename(tmp_path, dat_path)
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

