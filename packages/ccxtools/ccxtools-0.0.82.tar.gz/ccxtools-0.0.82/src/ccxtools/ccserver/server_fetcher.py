import requests


class ServerFetcher:
    server_url = 'http://ec2-43-200-255-25.ap-northeast-2.compute.amazonaws.com'

    # server_url = 'http://127.0.0.1:8000'

    def __init__(self, token, program):
        self.token = token
        self.program = program

    def request_get(self, url):
        return requests.get(url)

    def request_post(self, url, data):
        res = requests.post(url, json=data, headers={
            'Authorization': f'Token {self.token}',
            'Content-Type': 'application/json',
        })

        if not 200 <= res.status_code < 300:
            raise Exception(res.text)

    def log_error(self, exception, traceback):
        return self.request_post(f'{self.server_url}/logs/errors/', {
            'program': self.program,
            'exception': exception,
            'traceback': traceback,
        })
