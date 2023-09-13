import warnings
from base64 import b64encode, b64decode


class BASE64:
    @staticmethod
    def encrypt(string: str, encoding='utf-8'):
        warnings.warn("此方法已弃用，不推荐使用，切换到lesscode-utils包里", DeprecationWarning)
        encrypt_string = b64encode(string.encode(encoding)).decode(encoding)
        return encrypt_string

    @staticmethod
    def decrypt(string: str, encoding='utf-8'):
        warnings.warn("此方法已弃用，不推荐使用，切换到lesscode-utils包里", DeprecationWarning)
        decrypt_string = b64decode(string.encode(encoding)).decode(encoding)
        return decrypt_string
