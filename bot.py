import logging
import os
from telegram import ParseMode
from telegram.constants import MAX_MESSAGE_LENGTH
from telegram.ext import (Updater, CommandHandler)
from utils.client import EmailClient


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s:%(lineno)d'
                           ' - %(message)s', filename='/var/log/mailbot.log',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token = os.environ['TELEGRAM_TOKEN']

def handle_large_text(text):
    while text:
        if len(text) < MAX_MESSAGE_LENGTH:
            yield text
            text = None
        else:
            out = text[:MAX_MESSAGE_LENGTH]
            yield out
            text = text.lstrip(out)

def error(bot, update, _error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, _error)

def start_callback(bot, update):
    msg = "Use /help to get help"
    update.message.reply_text(msg)

def _help(bot, update):
    """Send a message when the command /help is issued."""
    help_str = "*Mailbox Setting*: \n" \
               "/setting 123456@example.com yourpassword"
    bot.send_message(update.message.chat_id, 
                    parse_mode=ParseMode.MARKDOWN,
                    text=help_str)

def setting_email(bot, update, args, job_queue):
    global email_addr, email_passwd, inbox_num
    email_addr = args[0]
    email_passwd = args[1]
    logger.info("received setting_email command.")
    update.message.reply_text("Configure email success!")
    with EmailClient(email_addr, email_passwd) as client:
        inbox_num = client.get_mails_count()
    logger.info("periodic task scheduled.")
    job_queue.run_repeating(periodic_task, 600)


def periodic_task(bot, update):
    logger.info("entering periodic task.")
    with EmailClient(email_addr, email_passwd) as client:
        new_inbox_num = client.get_mails_count()
    if new_inbox_num > inbox:
        get_email(bot, update, new_inbox_num)

def inbox(bot, update):
    logger.info("received inbox command.")
    with EmailClient(email_addr, email_passwd) as client:
        inbox_num = client.get_mails_count()
        reply_text = "The index of newest mail is *%d*" % inbox_num
        bot.send_message(update.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        text=reply_text)

def get_email(bot, update, args):
    index = args[0]
    logger.info("received get command.")
    with EmailClient(email_addr, email_passwd) as client:
        mail = client.get_mail_by_index(index)
        content = mail.__repr__()
        for text in handle_large_text(content):
            bot.send_message(update.message.chat_id,
                             text=text)

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token=bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # simple start function
    dp.add_handler(CommandHandler("start", start_callback))

    dp.add_handler(CommandHandler("help", _help))
    #
    #  Add command handler to set email address and account.
    dp.add_handler(CommandHandler("setting", setting_email, pass_args=True,
                                  pass_job_queue=True))

    dp.add_handler(CommandHandler("inbox", inbox))

    dp.add_handler(CommandHandler("get", get_email, pass_args=True))


    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()