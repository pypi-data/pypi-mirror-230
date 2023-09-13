import warnings


class MD5:
    @staticmethod
    def encrypt(string: str):
        warnings.warn("此方法已弃用，不推荐使用，切换到lesscode-utils包里", DeprecationWarning)
        import hashlib
        md5 = hashlib.md5(string.encode('utf-8'))
        encrypt_string = md5.hexdigest()
        return encrypt_string
