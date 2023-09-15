import os
import hashlib
from random import random
import logging
from datetime import datetime
import uuid
from functools import lru_cache
import time
import random


from utah.core.utilities import ConfigurationException

class AuthenticationUserNotFound(Exception):
    """This exception will be raised when a referenced user id cannot be found"""
    pass

class AuthenticationNotImplemented(Exception):
    """This exception is raised when a method is a base class which needed to be 
    overridden was not in the fina implementation """
    pass

class VerificationIsRequired(Exception):
    """ To be thrown when an attempt is made to authenticate using an unverified account """
    pass

class UserExists(Exception):
    """ Is thrown when an attempt is made to create am account that already exists """
    pass

class VerificationException(Exception):
    """ Exception when an attempt to verify an account fails """
    pass

class AuthenticationSystemError(Exception):
    """ General error in the authentication system """
    pass

class PasswordTooSimple(Exception):
    """ Thrown if a provided password does not meet minimum complexity requirements """
    pass

class TokenIsExpired(Exception):
    """ Thrown if an attempt is made to use an expired token """
    pass

class TokenNotFound(Exception):
    """ Thrown a token key is not found """
    pass


logger = logging.getLogger(__name__)



def generate_password(pwd_min_lower_case=2, pwd_min_upper_case=2, pwd_min_numbers=2, pwd_min_special_chars=2, pwd_min_length=8,
                        lower_case_chars="abcdefghikjlmnopqrstuvwxyz", upper_case_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ", special_chars="~!@#$%^&*()_+{}|:\"<>?`-=[]\;',./"):

    remaining_chars = pwd_min_length
    remaining_chars = remaining_chars - pwd_min_upper_case
    remaining_chars = remaining_chars - pwd_min_lower_case
    remaining_chars = remaining_chars - pwd_min_numbers
    remaining_chars = remaining_chars - pwd_min_special_chars

    if remaining_chars < 0:
        logger.warning("pwd_min_length:[%s] is shorter than the sum of pwd_min_upper_case+pwd_min_lower_case+pwd_min_numbers+pwd_min_special_chars value will be overriden")
        pwd_min_length=pwd_min_upper_case+pwd_min_lower_case+pwd_min_numbers+pwd_min_special_chars

    task_types = ["lower", "upper", "number", "special"]
    tasks = []
    outchars = []

    for i in range(0, pwd_min_lower_case):
        tasks.append("lower")

    for i in range(0, pwd_min_upper_case):
        tasks.append("upper")

    for i in range(0, pwd_min_numbers):
        tasks.append("number")

    for i in range(0, pwd_min_special_chars):
        tasks.append("special")

    while len(tasks) < pwd_min_length:
        tasks.append(random.choice(task_types))

    while tasks != []:
        task = random.choice(tasks)
        if task == "lower":
            char = random.choice(lower_case_chars)
        elif task == "upper":
            char = random.choice(upper_case_chars)
        elif task == "number":
            char = random.choice("0123456789")
        elif task == "special":
            char = random.choice(special_chars)

        del tasks[tasks.index(task)]
        outchars.append(char)

    ret_value = "".join(outchars)

    return ret_value


def encrypt_password(password:str):
    """ Generates a random salt then uses it to hash the password """
    salt = os.urandom(32)
    hashed_password = hash_password(salt, password)
    return (salt, hashed_password)


def hash_password(salt:bytes, password:str):
    """ Hashes a password using a provided salt """
    hashed_password = hashlib.pbkdf2_hmac(
        'sha256', # The hash digest algorithm for HMAC
        password.encode('utf-8'), # Convert the password to bytes
        salt, # Provide the salt
        100000, # It is recommended to use at least 100,000 iterations of SHA-256 
        dklen=128 # Get a 128 byte key
    )

    return hashed_password



class AuthenticationToken():
    def __init__(self, user_id:str, description:str, expire_date:datetime, key:str):
        if not (user_id and description and key):
            raise AuthenticationSystemError("All attributes for the authentication token must be provided: user_id:[%s], description:[%s], expire_date:[%s], key:[%s]" % (user_id, description, expire_date, key))

        self.user_id = user_id
        self.description = description
        self.key = key
        self.expire_date = expire_date

    def is_expired(self):
        if self.expire_date and datetime.utcnow() >= self.expire_date:
            return True

    def __eq__(self, __o: object) -> bool:
        if __o == None or not (
            self.user_id == __o.user_id and
            self.description == __o.description and
            self.key == __o.key and
            self.expire_date == __o.expire_date
        ):
            return False
        else:
            return True


class AuthenticationInfo():
    """ Class used to define the information used to assert identity """
    def __init__(self, user_id:str, salt:bytes, hashed_password:bytes, verification_code:None, authentication_tokens:list=[]):
        self.user_id = user_id
        self.hashed_password = hashed_password
        self.salt = salt
        self.verification_code = verification_code
        self.authentication_tokens = authentication_tokens

    def authenticate(self, password):
        """ Assert identity using the provided password returns True if sucessful and 
        will raise a VerificationIsRequired exception if an attempt is made to authenticat
        against an unverified account """
        ret_value = False

        if self.verification_code:
            raise VerificationIsRequired()

        new_hashed_password = hash_password(self.salt, password)
        if new_hashed_password == self.hashed_password:
            ret_value = True

        return ret_value

    def create_token(self, description:str, expire_date:datetime=None) -> AuthenticationToken:
        """ Create a new authorization token to make API use cases work
        """
        ret_token = AuthenticationToken(self.user_id, description, expire_date, str(uuid.uuid4()))
        self.authentication_tokens.append(ret_token)
        return ret_token


    def __eq__(self, __o: object) -> bool:
        ret_value = True

        if __o == None or not (
            self.user_id == __o.user_id and 
            self.hashed_password == __o.hashed_password and
            self.salt == __o.salt and 
            self.verification_code == __o.verification_code and 
            self.authentication_tokens == __o.authentication_tokens
        ):
            ret_value = False

        return ret_value


class BaseAuthenticationService():
    """ This class provides a base authentication service. It cannot be used
    as is because it does not implement any persistence methods and therefore
    must be extended. """
    def __init__(self, 
        token_cache_timeout_secs:int, 
        account_verification_required:False, 
        pwd_min_upper_case:int=0, 
        pwd_min_lower_case:int=0, 
        pwd_min_numbers:int=0, 
        pwd_min_special_chars:int=0, 
        pwd_min_length:int=6,
        upper_case_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        lower_case_chars="abcdefghikjlmnopqrstuvwxyz",
        special_chars="~!@#$%^&*()_+{}|:\"<>?`-=[]\;',./"):

        self.account_verification_required = account_verification_required
        self.token_cache_timeout_secs = token_cache_timeout_secs
        self.pwd_min_upper_case = pwd_min_upper_case
        self.pwd_min_lower_case = pwd_min_lower_case
        self.pwd_min_numbers = pwd_min_numbers
        self.pwd_min_special_chars = pwd_min_special_chars
        self.pwd_min_length = pwd_min_length
        self.upper_case_chars = upper_case_chars
        self.lower_case_chars = lower_case_chars
        self.numbers = "0123456789"
        self.special_chars = special_chars

        remaining_chars = self.pwd_min_length
        remaining_chars = remaining_chars - self.pwd_min_upper_case
        remaining_chars = remaining_chars - self.pwd_min_lower_case
        remaining_chars = remaining_chars - self.pwd_min_numbers
        remaining_chars = remaining_chars - self.pwd_min_special_chars

        if remaining_chars < 0:
            raise ConfigurationException("Authentication service cannot start. Password rules indicate more non-alpha characters than the password length")

    def is_account_verification_required(self):
        return self.account_verification_required

    def authenticate(self, user_id, password):
        """ Authenticate a user's identity with username and password """
        ret_value = False
        try:
            authentication_info:AuthenticationInfo = self.get_authentication_info(user_id)
            if authentication_info:
                ret_value = authentication_info.authenticate(password)

        except AuthenticationUserNotFound as e:
            pass

        return ret_value


    def add_authentication_info(self, user_id:str, password:str, no_verify=False):
        """ If authentication information is not in directory add it returns a True if sucessful"""

        ret_value = None
        if not self.get_authentication_info(user_id):
            authentication_info = self.build_authentication_info(user_id, password, no_verify=no_verify)
            self.write_authentication_info(authentication_info)
            ret_value = authentication_info

        return ret_value


    def change_password(self, user_id:str, old_password:str, new_password:str):
        """ Verify user identity, generate a new salt and encrypted password then write to directory """

        if not self.is_password_complex_enough(new_password):
            raise PasswordTooSimple()

        ret_value = False
        if self.authenticate(user_id, old_password):
            ai = self.get_authentication_info(user_id)
            salt, hashed_password = encrypt_password(new_password)
            ai.salt = salt
            ai.hashed_password = hashed_password

            self.write_authentication_info(ai)

            ret_value = True

        return ret_value


    def build_authentication_info(self, user_id:str, password:str, no_verify=False):
        """ Used to build an AuthenticationInfo object for new accounts. 
        If the account_verification_required flag is set on the service a verification 
        code will be generated and provided as well. """

        if not self.is_password_complex_enough(password):
            raise PasswordTooSimple()

        salt, hashed_password = encrypt_password(password)
        verification_code = None
        if self.account_verification_required and not no_verify:
            verification_code = self.generate_verification_code()

        authentication_info = AuthenticationInfo(user_id, salt, hashed_password, verification_code)
        return authentication_info


    def generate_verification_code(self):
        """ Used to generate an account verification code. Will be a 6 digit random number. The method can be overriden to generate a different format of value"""
        return str(random())[-6:]


    def new_verification(self, user_id):
        """ Allows a user to request a new verification code when the previous one was lost """
        if not self.account_verification_required:
            raise AuthenticationSystemError("new_verification: Current configuration of the authentication service does not require a verification")

        ai = self.get_authentication_info(user_id)
        ai.verification_code = self.generate_verification_code()
        self.write_authentication_info(ai)
        return ai


    def verify(self, user_id:str, verification_code:str):
        """ Verifies an account with the provided verification code """
        if not self.account_verification_required:
            raise AuthenticationSystemError("verify: Current configuration of the authentication service does not require a verification")

        ai = self.get_authentication_info(user_id)

        ret_value = True
        if ai.verification_code:
            if ai.verification_code == verification_code:
                ai.verification_code = None
                self.write_authentication_info(ai)
            else:
                ret_value = False
        else:
            logger.warn("An attempt was made to verify an account:[%s] that did not need it" % user_id)

        return ret_value


    def get_token_ttl_hash(self):
        """Return the same value withing `seconds` time period"""
        return round(time.time() / self.token_cache_timeout_secs)


    def get_user_id_from_token_key(self, key:str):
        token:AuthenticationToken = self.__get_cached_token_from_key(key, ttl_hash=self.get_token_ttl_hash())

        if token.is_expired():
            raise TokenIsExpired("Authentication token:[%s] is expired" % key)

        return token.user_id


    @lru_cache(1000, False)
    def __get_cached_token_from_key(self, key:str, ttl_hash:int):
        ret_token = self.get_token_from_key(key)

        if not ret_token:
            raise TokenNotFound("Token:[%s] was not found" % key)

        return ret_token


    def get_token_from_key(self, key:str):
        """ IMPLEMENT: Method provides the contract signature to get authentication information 
        This method must be overridden in an implementation """
        raise AuthenticationNotImplemented()


    def get_authentication_info(self, user_id:str):
        """ IMPLEMENT: Method provides the contract sinature to get authentication information 
        This method must be overridden in an implementation """
        raise AuthenticationNotImplemented()


    def write_authentication_info(self, authentication_info:AuthenticationInfo):
        """ IMPLEMENT: Method provides the contract signature to write  authentication information 
        This method must be overridden in an implementation """
        raise AuthenticationNotImplemented()


    def delete_authentication_info(self, user_id:str):
        """ IMPLEMENT: Method provides the contract signature to delete authentication information 
        It will delete the authentication information and return the deleted object
        This method must be overridden in an implementation """
        raise AuthenticationNotImplemented()


    def is_password_complex_enough(self, password):
        """ Check that a password meets min complexity requirements """
        upper_case_count = 0
        lower_case_count = 0
        number_case_count = 0
        special_char_count = 0

        for char in password:
            if char in self.lower_case_chars:
                lower_case_count = lower_case_count + 1
            elif char in self.upper_case_chars:
                upper_case_count = upper_case_count + 1
            elif char in self.numbers:
                number_case_count = number_case_count + 1
            else:
                special_char_count = special_char_count + 1

        if len(password) >= self.pwd_min_length and \
            lower_case_count >= self.pwd_min_lower_case and \
            upper_case_count >= self.pwd_min_upper_case and \
            number_case_count >= self.pwd_min_numbers and \
            special_char_count >= self.pwd_min_special_chars:
            ret_value = True
        else:
            ret_value = False

        return ret_value


    def generate_password(self):
        return generate_password(pwd_min_lower_case=self.pwd_min_lower_case, 
                    pwd_min_upper_case=self.pwd_min_upper_case, 
                    pwd_min_numbers=self.pwd_min_numbers, 
                    pwd_min_special_chars=self.pwd_min_special_chars, 
                    pwd_min_length=self.pwd_min_length,
                    lower_case_chars=self.lower_case_chars, 
                    upper_case_chars=self.upper_case_chars, 
                    special_chars=self.special_chars)
