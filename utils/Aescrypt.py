from Crypto.Cipher import AES
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash


def add_16(par):
    if type(par) == str:
        par = par.encode()
    while len(par) % 16 != 0:
        par += b'\x00'
    return par


class Aescrypt:
    def __init__(self):
        self.result = None
        self.md5_pwd = None
        self.decrypt_text = None
        self.encrypt_text = None
        self.aes = None
        self.key = add_16('15sFA..SF12FA1SFz.*97WRr#)($#')
        self.MD5Key = 'VSD-GAG65fas*eaGzSDFaffs02*(^$()^R'
        # CBB模式
        self.model = AES.MODE_CBC
        # ECB模式
        # self.model = AES.MODE_ECB
        self.iv = '85412/*UJ^$#(.FW'.encode()

    def AesEnCrypt(self, EC):
        EC = add_16(EC)
        if self.model == AES.MODE_CBC:
            self.aes = AES.new(self.key, self.model, self.iv)
        elif self.model == AES.MODE_ECB:
            self.aes = AES.new(self.key, self.model)
        self.encrypt_text = self.aes.encrypt(EC)
        return self.encrypt_text

    def AesDeCrypt(self, EC):
        if self.model == AES.MODE_CBC:
            self.aes = AES.new(self.key, self.model, self.iv)
        elif self.model == AES.MODE_ECB:
            self.aes = AES.new(self.key, self.model)
        self.decrypt_text = self.aes.decrypt(EC)
        self.decrypt_text = self.decrypt_text.strip(b"\x00")
        return self.decrypt_text.decode('utf8')

    def AesEnCryptMD5(self, AE):
        pwd = AE + self.MD5Key
        encode_pwd = pwd.encode()  # 把字符串转为字节类型
        # 使用md5进行加密
        self.md5_pwd = hashlib.md5(encode_pwd)
        return self.md5_pwd

    def encryption(self, pwd):
        pwd_1 = self.AesEnCrypt(pwd)
        self.result = self.AesEnCryptMD5(str(pwd_1)).hexdigest()
        return self.result

    def encryption1(self, pwd):
        pwd_1 = self.AesEnCrypt(pwd)
        self.result = self.AesEnCryptMD5(str(pwd_1)).hexdigest()
        return self.result


if __name__ == '__main__':
    aesCryptor = Aescrypt()
    text = "Ll001123.."
    en_text = aesCryptor.encryption(text)
    print("密文:", str(en_text))
    print(check_password_hash('pbkdf2:sha256:260000$m3qeYG0yKBLvFeRl$5d583d55d903005240b883e88330cc2cf5af1fba74622d6439e57bcd8340a4fe',en_text))

