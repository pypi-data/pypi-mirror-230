import hashlib
import base64
from Crypto.Cipher import AES
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

UTF_8_ENCODING = "UTF-8"
GBK_ENCODING = "GBK"


def sha256_encrypt(text: str, salt: str = None, encoding: str = UTF_8_ENCODING):
    """
    Encrypts an API token using SHA-256 hashing algorithm.

    about salt:
    如果需要与业务方确认sha256的值是否一致，双方保证sha256前，格式为：salt.text
    """
    if salt:
        text = f"{salt}.{text}"

    hash_object = hashlib.sha256(text.encode(encoding))
    return hash_object.hexdigest()


def md5_encrypt(text: str, salt: str = None, encoding: str = UTF_8_ENCODING):
    """
    Encrypts an API token using MD5 hashing algorithm.

    about salt:
    如果需要与业务方确认md5的值是否一致，双方保证md5前，格式为：salt.text
    """
    if salt:
        text = f"{salt}.{text}"

    hash_object = hashlib.md5(text.encode(encoding))
    return hash_object.hexdigest()


def base64_encode(text: str, encoding: str = UTF_8_ENCODING) -> str:
    """
    Encodes a string to base64 string.
    """
    return base64.b64encode(text.encode(encoding)).decode()


def base64_decode(text: str, encoding: str = "utf-8") -> str:
    """
    Decodes a base64 string to string.
    """
    return base64.b64decode(text).decode(encoding)


class AESCryptor(object):

    key: str
    nonce: str
    encoding: str

    def __init__(self, key: str, nonce: str, encoding: str = UTF_8_ENCODING):
        self.key = key
        self.nonce = nonce
        self.encoding = encoding

    def encrypt(self, plaintext: str) -> str:
        cipher = AES.new(self.key.encode(), AES.MODE_GCM, nonce=self.nonce.encode())
        ciphertext = base64.b64encode(cipher.encrypt(plaintext.encode(self.encoding))).decode()

        return ciphertext

    def decrypt(self, ciphertext: str) -> str:
        cipher = AES.new(self.key.encode(), AES.MODE_GCM, nonce=self.nonce.encode())
        s = base64.b64decode(ciphertext)
        plaintext = cipher.decrypt(s)

        return plaintext.decode(self.encoding)


class RSA2Cryptor:

    def __init__(self, private_key: str = None, public_key: str = None) -> None:
        self.private_key = private_key
        self.public_key = public_key

    @classmethod
    def generate_key_pair(cls) -> tuple[str, str]:
        # 生成RSA密钥对
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        # 将私钥序列化为PEM格式
        pem_private_key = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # 将公钥序列化为PEM格式
        public_key = private_key.public_key()
        pem_public_key = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return base64.b64encode(pem_private_key).decode(), base64.b64encode(pem_public_key).decode()

    def encode_by_public_key(self, content: str | bytes) -> str:
        pem_public_key = base64.b64decode(self.public_key)
        public_key = serialization.load_pem_public_key(pem_public_key)
        encrypted_data = public_key.encrypt(
            content if isinstance(content, bytes) else content.decode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return base64.b64encode(encrypted_data).decode()

    def decode_by_private_key(self):
        ...