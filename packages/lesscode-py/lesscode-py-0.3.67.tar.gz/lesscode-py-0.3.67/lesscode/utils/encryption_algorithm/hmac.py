import hmac
import warnings


class HMAC:
    @staticmethod
    def encrypt(string: str, key: str, digestmod="MD5", encoding='utf-8', flag=True):
        warnings.warn("此方法已弃用，不推荐使用，切换到lesscode-utils包里", DeprecationWarning)
        h = hmac.new(key.encode(encoding), string.encode(encoding), digestmod=digestmod)
        if flag:
            encrypt_string = h.hexdigest()
        else:
            encrypt_string = h.digest()
        return encrypt_string
