class StatusException(Exception):
    def __init__(self, url, code, detail):
        self.url = url
        self.code = code
        self.detail = detail

    def __str__(self):
        return f"{self.url} {self.code}: {self.detail}"

    @staticmethod
    def from_response(response):
        return StatusException(response.url, response.status_code, response.json().get("detail"))