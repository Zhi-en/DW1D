import hashlib
def Hash(password):
    return hashlib.sha1(str(password)).hexdigest()