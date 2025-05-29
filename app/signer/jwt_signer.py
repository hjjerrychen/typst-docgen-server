import jwt

class JWTSigner:
    def __init__(self, private_key_path: str, public_key_path: str, algorithm: str = 'HS256'):
        with open(private_key_path, 'rb') as reader:
            self.private_key = reader.read()
        with open(public_key_path, 'rb') as reader:
            self.public_key = reader.read()
        self.algorithm = algorithm

    def sign(self, payload: dict, headers: dict) -> str:
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm, headers=headers)

    def verify(self, encoded: str) -> dict:
        return jwt.decode(encoded, self.public_key, algorithms=[self.algorithm], issuer="urn:invalid", options={"require": ["exp", "iss", "sub"]})
    
    def get_unverified_payload(self, encoded: str) -> dict:
        return jwt.decode(encoded, options={"verify_signature": False})

    def get_unverified_header(self, encoded: str) -> dict:
        return jwt.get_unverified_header(encoded)

    def get_algorithm(self) -> str:
        return self.algorithm