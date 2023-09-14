import hashlib
import binascii
import os


def passwd(password: str) -> str:
    """Hash a password for storing.
    :param password: The password to hash
    :type password: str
    """
    salt = binascii.hexlify(os.urandom(6))
    hash = hashlib.sha1(salt + password.encode('utf-8')).hexdigest()
    return ('sha1:' + salt.decode() + ':' + hash)
