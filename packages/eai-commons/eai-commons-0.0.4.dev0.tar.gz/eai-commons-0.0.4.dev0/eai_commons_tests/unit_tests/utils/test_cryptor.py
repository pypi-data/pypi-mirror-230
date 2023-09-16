import time

from eai_commons.utils import cryptor
from eai_commons_tests.unit_tests.utils import SALT, AES_KEY, AES_NONCE


need_encrypt_content = "无关风月，我题序等你回，悬笔一绝，那岸边浪千迭"


def test_sha256_encrypt():
    default_encrypt = cryptor.sha256_encrypt(need_encrypt_content)
    print(default_encrypt)

    salt_encrypt = cryptor.sha256_encrypt(need_encrypt_content, SALT)
    print(salt_encrypt)

    assert default_encrypt != salt_encrypt


def test_md5_encrypt():
    default_encrypt = cryptor.md5_encrypt(need_encrypt_content)
    print(default_encrypt)

    salt_encrypt = cryptor.md5_encrypt(need_encrypt_content, SALT)
    print(salt_encrypt)

    assert default_encrypt != salt_encrypt


def test_base64_encode_decode():
    encode = cryptor.base64_encode(need_encrypt_content)
    print(encode)

    decode = cryptor.base64_decode(encode)
    print(decode)
    assert need_encrypt_content == decode


def test_aes_encode_decode():
    aes_cryptor = cryptor.AESCryptor(AES_KEY, AES_NONCE)
    encrypt = aes_cryptor.encrypt(need_encrypt_content)
    print(encrypt)

    decrypt = aes_cryptor.decrypt(encrypt)
    print(decrypt)
    assert need_encrypt_content == decrypt


def test_generate_rsa2_key_pair():
    priv_key, pub_key = cryptor.RSA2Cryptor.generate_key_pair()
    print(priv_key)
    print(pub_key)
    ...