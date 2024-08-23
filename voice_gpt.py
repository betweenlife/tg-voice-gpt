import os
from dotenv import load_dotenv
import logging
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, CallbackContext, \
    MessageHandler, filters
import openai
import speech_recognition as sr
import subprocess

load_dotenv()

TG_BOT_TOKEN=os.getenv("TG_BOT_TOKEN")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
GPT_MODEL=os.getenv("GPT_MODEL")

openai.api_key = OPENAI_API_KEY
logging.basicConfig(level=logging.INFO)

language_codes = json.load(open('language_codes.json'))
language_keyboard_buttons = [[InlineKeyboardButton(text=lang, callback_data=language_codes[lang])] for lang in language_codes]

r = sr.Recognizer()


def obtain_language_name(language_code) -> str:
    if language_code != 'en-EN':
        for lang in language_codes:
            if language_codes[lang] == language_code:
                return lang
    else:
        return 'English'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        f"Here you are! \n\n/ask_me_question")


async def ask_me_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(text="Sure, select language and type or record your question using microphone.",
                                    reply_markup=InlineKeyboardMarkup(language_keyboard_buttons))
    context.user_data['selected_language'] = None


async def pre_request_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['selected_language'] = update.callback_query.data
    message = 'Well, type or record your question using microphone.'
    language = obtain_language_name(context.user_data['selected_language'])
    if language != 'English':
        completion = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[
                {'role': 'user', 'content': f"Can you translate this sentence '{message}' in {language}, "
                                            f"without writing anything else, only translation?"}
            ]
        )
        if 'choices' in completion:
            if 'message' in completion['choices'][0]:
                message = completion['choices'][0]['message'].get("content")
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(message)


def generate_gpt_answer(user_message, language) -> str:
    answer = "Seems something went wrong... try again later!"
    completion = openai.ChatCompletion.create(
        model=os.getenv("TG_BOT_TOKEN"),
        messages=[
            {'role': 'user', 'content': f"Chat, please answer this question {user_message} in {language}"
                                        f"and don't ask me if I need help in anything else."}
        ]
    )
    if 'choices' in completion:
        if 'message' in completion['choices'][0]:
            answer = completion['choices'][0]['message'].get("content")
    return answer


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    language = obtain_language_name(context.user_data['selected_language'])
    gpt_answer = generate_gpt_answer(user_message, language)
    await update.message.reply_text(gpt_answer)
    await update.message.reply_html(f"/ask_me_question")


def convert_audio_in_text(audio_file, selected_language) -> tuple:
    text, error = '', None
    with open('audio.ogg', 'wb') as file:
        file.write(audio_file)
    ffmpeg_command = ['ffmpeg', '-i', 'audio.ogg', 'audio.wav', '-y']
    subprocess.run(ffmpeg_command, check=True)
    file = sr.AudioFile('audio.wav')
    try:
        with file as source:
            audio = r.record(source)
            text = r.recognize_google(audio, language=selected_language)
    except Exception as e:
        error = "Sorry, I didn't catch your phrase"
    return text, error


async def get_voice(update: Update, context: CallbackContext):
    selected_language = context.user_data['selected_language']
    language = obtain_language_name(selected_language)
    file = await context.bot.get_file(update.message.voice)
    audio = file.download_as_bytearray()
    audio_file = await audio
    text, error = convert_audio_in_text(audio_file, selected_language)
    if not error:
        gpt_answer = generate_gpt_answer(text, language)
        await update.message.reply_html(
            f"You asked: \n{text}. \n\nHere the answer: \n{gpt_answer}"
        )
    else:
        await update.message.reply_html(error)
    await update.message.reply_html(text="/ask_me_question")


def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ask_me_question", ask_me_question))
    application.add_handler(
        CallbackQueryHandler(pre_request_text, pattern="^" + "|".join(language_codes.values()) + "$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, get_text))
    application.add_handler(MessageHandler(filters.VOICE, get_voice))
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
