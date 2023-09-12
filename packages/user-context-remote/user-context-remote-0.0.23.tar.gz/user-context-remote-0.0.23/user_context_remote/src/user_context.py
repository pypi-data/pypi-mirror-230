import os
from our_url.src.index import UrlCirclez
import json
from typing import Any
import sys
from our_url.src.action_name_enum import ActionName
from our_url.src.entity_name_enum import EntityName
from our_url.src.component_name_enum import ComponentName
from language_local_python_package.src.language_enum_class import LanguageCode
from dotenv import load_dotenv
import requests
from httpstatus import HTTPStatus
load_dotenv()
BRAND_NAME = os.getenv('BRAND_NAME')
ENVIORNMENT_NAME = os.getenv('ENVIRONMENT_NAME')
AUTHENTICATION_API_VERSION = 1
# TODO: As we don't want to using the logger, add a mini logger function/method from sdk package

class UserContext:
    _instance = None

    def __new__(cls, email: str = None, password: str = None, jwt_token: str = None):
        if cls._instance is None:
            cls._instance = super(UserContext, cls).__new__(cls)
            if email is not None and password is not None:
                cls._instance._initialize(email=email, password=password)
            else:
                cls._instance._initialize(jwt_token=jwt_token)
        return cls._instance

    # TODO: change email to username, change jwt_token to user_jwt_token everywhere
    def _initialize(self, email: str = None, password: str = None, jwt_token: str = None):
        self.user_id = None
        self.profile_id = None
        self.lang_code = None
        self.real_first_name = None
        self.real_last_name = None
        self.real_display_name = None
        if (email is not None and password is not None):
            self.jwt_token = None
            data = self._authenticate_by_email_and_password(email, password)
        else:
            self.jwt_token = jwt_token
            data = self._authenticate_by_jwt_token(jwt_token=jwt_token)
        self.get_user_data_login_response(data=data)

    @staticmethod
    # TODO: Change the method name to login_using_username_and_password()
    # TODO: Change the 1st parameter from email to username, change jwt_token to user_jwt_token
    def login(email: str = None, password: str = None, jwt_token: str = None):
        # logger.start(object={"email": email, "passowrd": password})
        if UserContext._instance is None:
            if jwt_token is not None:
                UserContext._instance = UserContext(jwt_token=jwt_token)
            else:
                if email is None:
                    email = os.getenv("PRODUCT_USERNAME")
                if password is None:
                    password = os.getenv("PRODUCT_PASSWORD")
                if email is None or password is None or email == "" or password == "":
                    raise Exception(
                        "please insert in your .env PRODUCT_USERNAME and PRODUCT_PASSWORD")
                UserContext._instance = UserContext(
                    email=email, password=password)
        user = UserContext._instance
        # logger.end(object={"user": str(user)})
        return user

    def _set_real_user_id(self, user_id: int) -> None:
        # logger.start(object={"user_id": user_id})
        self.user_id = user_id
        # logger.end()

    def _set_real_profile_id(self, profile_id: int) -> None:
        # logger.start(object={"profile_id": profile_id})
        self.profile_id = profile_id
        # logger.end()

    def get_real_user_id(self) -> int:
        # logger.start()
        # logger.end(object={"user_id": self.user_id})
        return self.user_id

    def get_real_profile_id(self) -> int:
        # logger.start()
        # logger.end(object={"user_id": self.profile_id})
        return self.profile_id

    def get_curent_lang_code(self) -> str:
        # logger.start()
        # logger.end(object={"language": self.language})
        return self.lang_code

    def _set_current_lang_code(self, language: LanguageCode) -> None:
        # logger.start(object={"language": language.value})
        self.lang_code = language.value
        # logger.end()

    def _set_real_first_name(self, first_name: str) -> None:
        # logger.start(object={"first_name": first_name})
        self.real_first_name = first_name
        # logger.end()

    def _set_real_last_name(self, last_name: str) -> None:
        # logger.start(object={"first_name": last_name})
        self.real_last_name = last_name
        # logger.end()

    def get_real_first_name(self) -> str:
        # logger.start()
        # logger.end(object={"first_name": self.first_name})
        return self.real_first_name

    def get_real_last_name(self) -> str:
        # logger.start()
        # logger.end(object={"last_name": self.last_name})
        return self.real_last_name

    def _set_real_name(self, name: str) -> None:
        # logger.start(object={"first_name": last_name})
        self.real_display_name = name
        # logger.end()

    def get_real_name(self) -> str:
        # logger.start()
        # logger.end(object={"first_name": self.first_name})
        return self.real_display_name

    def get_jwt_token(self) -> str:
        return self.jwt_token

    # TODO: Do we have public method for login_using_user_jwt_token()?
    def _authenticate_by_email_and_password(self, email: str, password: str) -> str:
        # logger.start(object={"email": email, "password": password})
        try:
            url_circlez = UrlCirclez()
            url_jwt = url_circlez.endpoint_url(
                brand_name=BRAND_NAME,
                environment_name=ENVIORNMENT_NAME,
                component=ComponentName.AUTHENTICATION.value,
                entity=EntityName.AUTH_LOGIN.value,
                version=AUTHENTICATION_API_VERSION,
                action=ActionName.LOGIN.value
            )
            data = {"email": email, "password": password}
            headers = {"Content-Type": "application/json"}
            output = requests.post(
                url=url_jwt, data=json.dumps(data, separators=(",", ":")), headers=headers
            )
            if output.status_code != HTTPStatus.OK:
                print(output.text, file=sys.stderr)
                raise Exception(output.text)
            self.jwt_token = output.json()["data"]["token"]
            # logger.end(object={"user_jwt_token": user_jwt_token })
            return output
        except Exception as e:
            print(
                "Error(Exception): user-context-remote-python _authenticate() " + str(e), file=sys.stderr)
            # TODO: logger.exception(object=e)
            # TODO: logger.end()
            raise

    def _authenticate_by_jwt_token(self, jwt_token: str) -> str:
        # TODO: Change UrlCirclez to OurUrl() as we are not only Circlez
        url_circlez = UrlCirclez()
        # TODO: Renamr url_jwt to authentication_login_validate_jwt_url
        url_jwt = url_circlez.endpoint_url(
            brand_name=BRAND_NAME,
            environment_name=ENVIORNMENT_NAME,
            component=ComponentName.AUTHENTICATION.value,
            entity=EntityName.AUTH_LOGIN.value,
            version=AUTHENTICATION_API_VERSION,
            action=ActionName.VALIDATE_JWT.value
        )
        data = {"jwtToken": jwt_token}
        headers = {"Content-Type": "application/json"}
        output = requests.post(
            url=url_jwt, data=json.dumps(data, separators=(",", ":")), headers=headers
        )
        if output.status_code != HTTPStatus.OK:
            print(output.text, file=sys.stderr)
            raise Exception(output.text)
        return output

    # TODO: We should also get the email from user_jwt_token
    # TODO: More meanigful name than data
    def get_user_data_login_response(self, data: str) -> None:
        if "userDetails" in data.json()["data"]:
            if "profileId" in data.json()["data"]["userDetails"]:
                profile_id = data.json(
                )["data"]["userDetails"]["profileId"]
                self._set_real_profile_id(int(profile_id))
            if "userId" in data.json()["data"]["userDetails"]:
                user_id = data.json()["data"]["userDetails"]["userId"]
                self._set_real_user_id(int(user_id))
            if "lang_code" in data.json()["data"]["userDetails"]:
                lang_code = data.json(
                )["data"]["userDetails"]["lang_code"]
                self._set_current_lang_code(lang_code)
            if "firstName" in data.json()["data"]["userDetails"]:
                first_name = data.json(
                )["data"]["userDetails"]["firstName"]
                self._set_real_first_name(first_name)
            if "lastName" in data.json()["data"]["userDetails"]:
                last_name = data.json(
                )["data"]["userDetails"]["lastName"]
                self._set_real_last_name(last_name)
            # TODO: split the if, add each one separately to name. If none of the exist name = email
            if self.real_first_name is not None and self.real_last_name is not None:
                name = first_name+" "+last_name
                self._set_real_name(name)


# from #logger_local.#loggerComponentEnum import #loggerComponentEnum
# from #logger_local.#logger import #logger

# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID = 197
# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME = "User Context python package"
# DEVELOPER_EMAIL = "idan.a@circ.zone"
# obj = {
#     'component_id': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID,
#     'component_name': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME,
#     'component_category': #loggerComponentEnum.ComponentCategory.Code.value,
#     'developer_email': DEVELOPER_EMAIL
# }
# #logger = #logger.create_#logger(object=obj)

    # Commented as we get the decoded user_jwt_token from the authentication service and the user-context do not have access to th JWT_SECRET_KEY
    # def get_user_json_by_user_jwt_token(self, jwt_token: str) -> None:
    #     if jwt_token is None or jwt_token == "":
    #         raise Exception(
    #             "Your .env PRODUCT_NAME or PRODUCT_PASSWORD is wrong")
    #     #logger.start(object={"jwt_token": jwt_token})
    #     try:
    #         secret_key = os.getenv("JWT_SECRET_KEY")
    #         if secret_key is not None:
    #             decoded_payload = jwt.decode(jwt_token, secret_key, algorithms=[
    #                                          "HS256"], options={"verify_signature": False})
    #             self.profile_id = int(decoded_payload.get('profileId'))
    #             self.user_id = int(decoded_payload.get('userId'))
    #             self.language = decoded_payload.get('language')
    #             #logger.end()
    #     except jwt.ExpiredSignatureError as e:
    #         # Handle token expiration
    #         #logger.exception(object=e)
    #         print("Error:JWT token has expired.", sys.stderr)
    #         #logger.end()
    #         raise
    #     except jwt.InvalidTokenError as e:
    #         # Handle invalid token
    #         #logger.exception(object=e)
    #         print("Error:Invalid JWT token.", sys.stderr)
    #         #logger.end()
    #         raise
