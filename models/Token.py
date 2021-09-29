import os

from helpers import RequestHandler



class Token(RequestHandler):

    def get_new_token(self):
        token_details = {
            "client_id" : os.getenv("CLIENT_ID"),
            "client_secret" : os.getenv("CLIENT_SECRET"),
            "grant_type" : "client_credentials"
        }

        endpoint = "oauth2/token"
        response = self.get_token(endpoint, token_details)
        os.environ['TOKEN_KEY'] = response.json().get('access_token', None)
        return os.environ['TOKEN_KEY']
