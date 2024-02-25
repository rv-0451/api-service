import logging
from core.schemas.users import ExternalUser


log = logging.getLogger()


EXTERNAL_DB = {
    "testuser": {
        "email": "test@email.domain",
        "password": "test"
    }
}


class ExternalDB:
    def __init__(self):
        pass

    def get_user(self, username):
        try:
            user = EXTERNAL_DB[username]
            return ExternalUser(
                login=username,
                mail=user['email']
            )
        except KeyError:
            log.info(f"User '{username}' not found.")
            return None

    def authenticate_user(self, username, password):
        try:
            user = EXTERNAL_DB[username]
            if user['password'] == password:
                return ExternalUser(
                    login=username,
                    mail=user['email']
                )
            else:
                log.info("Wrong password.")
                return None
        except KeyError:
            log.info(f"User '{username}' not found.")
            return None
