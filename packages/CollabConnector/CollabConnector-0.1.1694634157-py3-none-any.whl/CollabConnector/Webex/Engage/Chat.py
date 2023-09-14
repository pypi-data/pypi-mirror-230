import sys


class Chat:
    def __init__(self, parent):
        self.parent = parent

    def list(self):
        if chats := self.parent.rest.get(f"/v3.0/chats"):
            return chats['chats']
        return chats

    def get(self, chat_id: int) -> dict:
        if chat := self.parent.rest.get(f"/v3.0/chat/{chat_id}"):
            return chat

        print(f"Error getting chat: {chat_id}", file=sys.stderr)
        return {}
