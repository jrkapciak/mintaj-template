from ninja import Schema


class TokenOut(Schema):
    access: str
    refresh: str


class RegisterIn(Schema):
    email: str
    password: str
