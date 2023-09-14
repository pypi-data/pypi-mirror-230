import requests


class User:
    config = None

    def __init__(self, client=None):
        self.config = client.get_config()

    def login(self):
        new_headers = {'X-Amz-Target': 'AWSCognitoIdentityProviderService.InitiateAuth',
                       'Content-Type': 'application/x-amz-json-1.1'}
        login_url = "https://cognito-idp.ap-south-1.amazonaws.com/"
        data = {
            "AuthParameters": {
                "USERNAME": self.config.get("username"),
                "PASSWORD": self.config.get("password")
            },
            "AuthFlow": "USER_PASSWORD_AUTH",
            "ClientId": self.config.get("client_id")
        }

        resp = requests.post(login_url, json=data, headers=new_headers)
        api_access_token = resp.json()['AuthenticationResult']['IdToken']
        return api_access_token

    def logout(self):
        pass
