import warnings


class SHA1:
    @staticmethod
    def encrypt(string: str):
        warnings.warn("此方法已弃用，不推荐使用，切换到lesscode-utils包里", DeprecationWarning)
        import hashlib
        sha = hashlib.sha1(string.encode('utf-8'))
        encrypt_string = sha.hexdigest()
        return encrypt_string
