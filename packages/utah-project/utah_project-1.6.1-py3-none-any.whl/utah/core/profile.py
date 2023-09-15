class ProfileUserNotFound(Exception):
    pass

class ProfileNotImplemented(Exception):
    pass

class ProfileInfo():
    def __init__(self, user_id:str, email_address:str, first_name:str, last_name:str, timezone:str="UTC"):
        self.user_id = user_id
        self.email_address = email_address
        self.first_name = first_name
        self.last_name = last_name
        self.timezone = timezone


class BaseProfileService():
    def get_profile_info(self, user_id:str):
        raise ProfileNotImplemented()


    def delete_profile_info(self, user_id:str):
        raise ProfileNotImplemented()


    def add_profile_info(self, profile_info:ProfileInfo):
        ret_value = False
        if not self.get_profile_info(profile_info.user_id):
            self.write_profile_info(profile_info)
            ret_value = True

        return ret_value


    def update_profile_info(self, profile_info:ProfileInfo):
        ret_value = False
        if self.get_profile_info(profile_info.user_id):
            self.write_profile_info(profile_info)
            ret_value = True


    def write_profile_info(self, profile_info:ProfileInfo):
        raise ProfileNotImplemented()

    
    def get_all_profiles(self):
        raise ProfileNotImplemented()





