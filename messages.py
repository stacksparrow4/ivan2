import json
import re

def load_message_db():
    with open("data/message-db.json", "r") as f:
        return json.load(f)

def load_users():
    with open("data/users.json", "r") as f:
        return json.load(f)

class UserDB:
    def __init__(self, users):
        self.users = users
        self.uid_to_name_dict = {}

        for uname in self.users:
            self.uid_to_name_dict[self.users[uname]["id"]] = self.users[uname]["name"]
    
    def uname_to_name(self, uname):
        return self.users[uname]["name"]
    
    def uid_to_name(self, uid):
        return self.uid_to_name_dict[uid]

    def names(self):
        return [self.users[uname]["name"] for uname in self.users.keys()]

    def uids(self):
        return [self.users[uname]["id"] for uname in self.users.keys()]

def clean_msg(m, user_db):
    # Emoji
    m = re.sub(r"<a?(:[^:]+:)[0-9]+>", r"\1", m)
    # User mentions
    for uid in user_db.uids():
        m = m.replace(f"<@{uid}>", f"@{user_db.uid_to_name(uid)}")
    return m

def clean_message_db(msg_db, user_db):
    for m in msg_db:
        m["content"] = clean_msg(m["content"], user_db)

    return [
        (user_db.uname_to_name(m["author"]), m["content"])
        for m in msg_db
        if m['content'].strip()
    ]

def load():
    user_db = UserDB(load_users())
    return clean_message_db(load_message_db(), user_db), user_db

def render_messages(msgs):
    return "\n".join([msg if type(msg) == str else ": ".join(msg) for msg in msgs])