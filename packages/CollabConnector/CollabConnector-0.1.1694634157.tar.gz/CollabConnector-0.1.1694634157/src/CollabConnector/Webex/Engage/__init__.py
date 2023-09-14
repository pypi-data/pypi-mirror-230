from .REST import REST
from .User import User
from .Team import Team
from .Chat import Chat


class Connect:
    def __init__(self, key=None, domain=None):
        self.rest = REST(key, domain)
        self.user = User(self)
        self.team = Team(self)
        self.chat = Chat(self)
