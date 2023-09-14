#
import hashlib


#
import bcrypt


#


#
class ResponseStatus:
    @staticmethod
    def send_ok(data=None, message=None):
        result = {'status': 'OK'}
        if data is not None:
            result['data'] = data
        if message is not None:
            result['message'] = message
        return result

    @staticmethod
    def send_nok(message, e=None):
        if not e:
            return {'status': 'NOK', 'message': message}
        else:
            return {'status': 'NOK', 'message': message, 'e': e}


class SafePw:
    @staticmethod
    def get_hashed_pw(plain_text_pw):
        return bcrypt.hashpw(plain_text_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def check_pw(plain_text_password, hashed_password):
        return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password.encode('utf-8'))


class FastPw:
    @staticmethod
    def get_hashed_pw(plain_text_pw):
        return hashlib.sha256(plain_text_pw.encode('utf-8')).hexdigest()

    @staticmethod
    def check_pw(plain_text_password, hashed_password):
        return FastPw.get_hashed_pw(plain_text_pw=plain_text_password) == hashed_password
