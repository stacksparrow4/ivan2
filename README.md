# Setup guide

1. Set up a Discord bot for the project and enable message intent and guild intent. Add it to your server giving it read and send message permissions for relevant channels.
1. `cp .env.example .env`.
    Fill in the details:
    | Env var | Details |
    | ------- | ------- |
    | `SCRAPE_CHANNELS` | Comma seperated list of discord channels to scrape chat history from. Bot must have read permission for these channels. |
    | `LLAMA_HOSTS` | Hostnames of worker machines running ollama. If you are going to run it on the local machine, leave it as `http://localhost:11434`. |
    | `WHITELISTED_CHANNELS` | Comma seperated list of channels in which the bot can be interacted with. |
    | `COMMAND_PREFIX` | The command prefix for the bot. |
    | `BOT_TOKEN` | The discord bot token. |
1. Set up your virtual environment:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```
1. Run `scrape_messages.py` to scrape the messages from your desired channel(s). This may take a while.
1. While the scrape is running, install and setup ollama locally [https://ollama.com/](https://ollama.com/). Once this is done, run `ollama run llama3` to download the `llama3` model locally.
1. Once the message scrape has finished, run `extract_facts.py`. This will take a while.
1. Once `extract_facts` has finished, run `collate_facts.py`.
1. Finally, run `bot.py` and use the bot in your whitelisted channel.