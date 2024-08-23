# TG Voice GPT

TG Voice GPT is a Telegram Bot that allows you to interact with ChatGPT through both vocal and typed messages in multiple languages.

## Features

- Interact with ChatGPT via text or voice messages.
- Supports multiple languages.
- Simple to set up and run.

## Prerequisites

1. **Python 3.7+**: Ensure you have Python installed on your system.
2. **Virtual Environment**: It's recommended to use a virtual environment for managing dependencies.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/betweenlife/tg-voice-gpt.git
cd tg-voice-gpt
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a file named ".env" in the project root directory and add the following variables:

- TG_BOT_TOKEN: your Telegram bot token. Follow Telegram [documentation](https://core.telegram.org/bots/tutorial) to create one.
- OPENAI_API_KEY: your OpenAI API key. Obtain it from OpenAI's API [documentation](https://openai.com/index/openai-api/).
- GPT_MODEL: the model to use with OpenAI's GPT. Default is "gpt-3.5-turbo", but it can be changed to another model if you have a suitable OpenAI plan.

Check ".env.example" to do it.

### 5. Run the Bot

Start the bot with the following command:

```bash
python voice_gpt.py
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## Contact

For any questions or issues, please contact francesco.vita1993@gmail.com.