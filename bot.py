import logging
import os

from utils.mail import EmailClient
from telegram import ParseMode
from telegram.constants import MAX_MESSAGE_LENGTH
from telegram.ext import (Updater, CommandHandler)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

bot_token = os.environ['TELEGRAM_TOKEN']


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

def setting_email(bot, update, args):
    global email_addr, email_passwd
    email_addr = args[0]
    email_passwd = args[1]

    update.message.reply_text("Configure email success!")

def inbox(bot, update):
    with EmailClient(email_addr, email_passwd) as client:
        num_of_mails = client.get_mails_count()
        reply_text = "The index of newest mail is *%d*" % num_of_mails
        bot.send_message(update.message.chat_id,
                        parse_mode=ParseMode.MARKDOWN,
                        text=reply_text)

def get_email(bot, update, args):
    index = args[0]
    with EmailClient(email_addr, email_passwd) as client:
        mail = client.get_mail_by_index(index)
        subject = "*Subject*: %s\n" % mail.subject
        sender = "*From*: %s - %s\n" % (mail.from_nickname, mail.from_account)
        date = "*Date*: %s\n" % mail.receivedtime
        bot.send_message(update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=subject+sender+date)
        if len(mail.text_content) > MAX_MESSAGE_LENGTH:
            text = mail.text_content[0:4096]
            bot.send_message(update.message.chat_id,
                             text=text)
            mail.text_content = mail.text_content.lstrip(text)
        if mail.text_content:
            bot.send_message(update.message.chat_id,
                             text=mail.text_content)
        


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
    dp.add_handler(CommandHandler("setting", setting_email, pass_args=True))

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