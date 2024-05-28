import json
import re

from constants import USERS, MESSAGE_DB_PATH

username_to_name = {}
user_id_to_name = {}
for username, name, user_id, _ in USERS:
    username_to_name[username] = name
    user_id_to_name[user_id] = name

def load_message_db():
    with open(MESSAGE_DB_PATH, "r") as f:
        return json.load(f)

def clean_message_db(msg_db):
    for m in msg_db:
        m["content"] = re.sub(r"<a?(:[^:]+:)[0-9]+>", r"\1", m["content"])
        for uid in user_id_to_name:
            m["content"] = m["content"].replace(f"<@{uid}>", f"@{user_id_to_name[uid]}")

    return [
        (username_to_name[m["author"]], m["content"])
        for m in msg_db
        if m['content'] and m['author'] in username_to_name.keys()
    ]

def load():
    return clean_message_db(load_message_db())

def render_messages(msgs):
    return "\n".join([": ".join(msg) for msg in msgs])