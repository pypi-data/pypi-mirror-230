import json
import subprocess
import random
import string
import base64
import datetime
import socket
import os


class Key(object):
    private_key = None
    public_key = None
    public_key_file = None
    private_key_file = None
    keypair_id = None
    type = None
    bits = None

    def __init__(self,
                 key_type=None,
                 key_bits=None,
                 public_key_file=None,
                 private_key_file=None
                 ):
        self.type = key_type
        self.bits = key_bits
        self.public_key_file = public_key_file
        self.private_key_file = private_key_file

    def create_keypair(self):
        # check bits
        if self.bits and self.bits not in [2048, 4096]:
            self.bits = 2048
        # Most cases we need save private key
        cmmd_en = 'openssl genrsa ' + str(self.bits)
        cmmd_de = 'openssl rsa -pubout'
        # phase 1
        p1 = subprocess.Popen([cmmd_en], shell=True, stdout=subprocess.PIPE)
        private_key = b''.join(p1.stdout.readlines()).decode()
        self.private_key = private_key
        # phase 2
        cmmd_echo = 'echo ' + '"' + private_key + '"'
        p2 = subprocess.Popen([cmmd_echo], shell=True, stdout=subprocess.PIPE)
        # phase 3
        p3 = subprocess.Popen([cmmd_de], shell=True, stdin=p2.stdout, stdout=subprocess.PIPE)
        public_key = p3.communicate()[0].decode()
        self.public_key = public_key

    def write_public_key(self):
        pubkey_id = ''.join([random.choice(string.hexdigits.lower()) for _ in range(12)])
        filename = '/tmp/' + pubkey_id + '.pubkey'
        with open(filename,'w') as f:
            print("writing pubkey to file: ", filename)
            f.write(self.public_key)
        self.public_key_file = filename

    def write_keypair(self):
        keypair_id = ''.join([random.choice(string.hexdigits.lower()) for _ in range(12)])
        filename_pubkey = '/tmp/' + keypair_id + '.pubkey'
        filename_prikey = '/tmp/' + keypair_id + '.prikey'
        with open(filename_pubkey,'w') as f:
            print("writing pubkey to file: ", filename_pubkey)
            f.write(self.public_key)
        self.public_key_file = filename_pubkey
        with open(filename_prikey,'w') as f:
            print("writing pubkey to file: ", filename_prikey)
            f.write(self.private_key)
        self.private_key_file = filename_prikey
        self.keypair_id = keypair_id

    def encrypt(self, plain_text:str):
        plain_text_base64 = base64.b64encode(plain_text.encode("utf-8")).decode()
        en_p1_cmd = 'echo -n ' + str(plain_text_base64.strip())
        # print("en_p1_cmd: ", en_p1_cmd)
        en_p1 = subprocess.Popen([en_p1_cmd], shell=True, stdout=subprocess.PIPE)
        # en_p2_cmd = 'openssl pkeyutl -encrypt -pubin -inkey ' + self.public_key_file + ' -in - '
        en_p2_cmd = 'openssl pkeyutl -encrypt -pubin -inkey ' + self.public_key_file
        # print("en_p2_cmd: ", en_p2_cmd)
        en_p2 = subprocess.Popen([en_p2_cmd], shell=True, stdin=en_p1.stdout, stdout=subprocess.PIPE)
        raw_byte = en_p2.communicate()[0]
        ascii_byte = base64.b64encode(raw_byte)
        ascii_text = ascii_byte.decode()
        return ascii_text

    def decrypt_deprecated(self, encrypted_text):
        encrypted_b64_string = encrypted_text
        encrypted_bytes = base64.b64decode(encrypted_b64_string)
        encrypted_bytes_file = '/tmp/' + self.keypair_id + '.encrypted_bytes'
        self.encrypted_bytes_file = encrypted_bytes_file
        with open(encrypted_bytes_file, 'wb') as f:
            f.write(encrypted_bytes)
        de_p1_cmd = 'openssl pkeyutl -decrypt -inkey' + ' ' + self.private_key_file + ' -in ' + encrypted_bytes_file
        de_p1 = subprocess.Popen([de_p1_cmd], shell=True, stdout=subprocess.PIPE)
        plain_text_base64_decrypted_byte = de_p1.communicate()[0]
        return base64.b64decode(plain_text_base64_decrypted_byte).decode()

    def decrypt(self, encrypted_text):
        encrypted_b64_string = encrypted_text
        encrypted_bytes = base64.b64decode(encrypted_b64_string)
        decryption_id = ''.join([random.choice(string.hexdigits.lower()) for _ in range(12)])
        decryption_temp_file = '/tmp/' + decryption_id + '.encrypted_bytes'
        with open(decryption_temp_file, 'wb') as f:
            f.write(encrypted_bytes)
        de_p1_cmd = 'openssl pkeyutl -decrypt -inkey' + ' ' + self.private_key_file + ' -in ' + decryption_temp_file
        de_p1 = subprocess.Popen([de_p1_cmd], shell=True, stdout=subprocess.PIPE)
        plain_text_base64_decrypted_byte = de_p1.communicate()[0]
        return base64.b64decode(plain_text_base64_decrypted_byte).decode()

    def load_pubkey(self):
        user_home = os.environ.get('HOME')
        if not self.public_key_file:
            public_key_file = user_home + '/.easyssl/pubkey'
            self.public_key_file = public_key_file
        else:
            public_key_file = self.public_key_file
        with open(public_key_file, 'r') as f:
            public_key = f.read()
        self.public_key = public_key

    def load_prikey(self):
        user_home = os.environ.get('HOME')
        if not self.private_key_file:
            private_key_file = user_home + '/.easyssl/prikey'
            self.private_key_file = private_key_file
        else:
            private_key_file = self.private_key_file
        with open(private_key_file, 'r') as f:
            private_key = f.read()
        self.private_key = private_key

