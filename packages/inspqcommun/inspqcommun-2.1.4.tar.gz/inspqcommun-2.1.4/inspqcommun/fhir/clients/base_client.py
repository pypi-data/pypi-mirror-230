class BaseClient:

    base_headers = {
        "Content-type": "application/json+fhir"
    }

    def __init__(self, base_url=None, base_uri=None, token_header=None) -> None:
        self.base_url = base_url if base_url is not None else "http://localhost:14001"
        self.base_uri = base_uri if base_uri is not None else ""
        self.set_headers(token_header=token_header)

    def set_headers(self, headers={}, token_header=None):
        new_headers = {**headers, **self.base_headers}
        if token_header is not None:
            if 'Content-Type' in token_header:
                del token_header['Content-Type']
            headers_with_auth = {**new_headers, **token_header}
            self.headers = headers_with_auth
        else:
            self.headers = new_headers
        return self.headers
    
    def get_fhir_url(self):
        return "{0}{1}".format(self.base_url, self.base_uri)