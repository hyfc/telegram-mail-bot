import base64
from datetime import datetime
from email.parser import Parser
import logging
import poplib
import pytz
import re


logger = logging.getLogger(__name__)

class MailDetails(object):
    def __init__(self):
        self.from_nickname = ""
        self.from_account  = ""
        self.to_nickname = ""
        self.to_account = ""
        self.subject = ""
        self.receivedtime = ""
        self.text_content = ""
        self.html_content = ""


def decode_byte(bstr, charset='utf8'):
    return bstr.decode(charset)

def get_rawcontent_charset(rawcontent):
    for item in rawcontent:
        if decode_byte(item).find('charset='):
            charset = re.findall(re.compile('charset="(.*)"'), decode_byte(item))
            for member in charset:
                if member is not None:
                    return member


def parse_raw_mail_data(raw_lines, charset='utf8'):
    msg_content = b'\r\n'.join(raw_lines).decode(encoding=charset)
    return Parser().parsestr(text=msg_content)

def decode_base64(s, charset='utf8'):
    return str(base64.decodebytes(s.encode(encoding=charset)), encoding=charset)


def get_mail_info(s):
    try:
        nickname, account = s.split(" ")
    except ValueError:
        nickname = ''
        account = s

    account = account.lstrip('<')
    account = account.rstrip('>')
    return nickname, account

def get_mail_details(msg):
    maildetails = MailDetails()

    fromstr = msg.get('From')
    from_nickname, from_account = get_mail_info(fromstr)
    maildetails.from_nickname = from_nickname
    maildetails.from_account = from_account
    tostr = msg.get('To')
    to_nickname, to_account = get_mail_info(tostr)
    maildetails.to_nickname = to_nickname
    maildetails.to_account = to_account

    subject = msg.get('Subject')
    try:
        maildetails.subject = decode_base64(subject.split("?")[3], charset=subject.split("?")[1])
    except IndexError:
        maildetails.subject = subject
    received_time = msg.get("Date")
    if received_time.endswith('(CST)'):
        maildetails.receivedtime = received_time
    else:
        time_str_fmt = "%a, %d %b %Y %H:%M:%S %z"
        time_obj = datetime.strptime(received_time, time_str_fmt)
        time_obj = time_obj.astimezone(pytz.timezone('Asia/Hong_Kong'))
        maildetails.receivedtime = time_obj.strftime(time_str_fmt)

    parts = msg.get_payload()
    content_charset = parts[0].get_content_charset()
    content = parts[0].as_string().split('base64')[-1]
    try:
        maildetails.text_content = decode_base64(content, content_charset)
    except Exception as e:
        logger.error('Exception caught: "%s"', e)
        maildetails.text_content = content
    content = parts[1].as_string().split('base64')[-1]
    maildetails.html_content = content

    return maildetails

class EmailClient(object):
    def __init__(self, email_account, passwd):
        self.email_account = email_account
        self.password = passwd
        self.server = self.connect(self)

    @staticmethod
    def connect(self):
        # parse the server's hostname from email account
        pop3_server = 'pop.'+self.email_account.split('@')[-1]

        server = poplib.POP3_SSL(pop3_server)

        # display the welcome info received from server,
        # indicating the connection is set up properly
        print(server.getwelcome().decode('utf8'))

        # authenticating
        server.user(self.email_account)
        server.pass_(self.password)

        return server

    def get_mails_list(self):
        _, mails, _ = self.server.list()
        return mails

    def get_mails_count(self):
        mails = self.get_mails_list()
        return len(mails)



    def get_mail_by_index(self, index):
        resp_status, mail_lines, mail_octets = self.server.retr(index)
        content_charset = get_rawcontent_charset(mail_lines)
        data = parse_raw_mail_data(mail_lines, charset=content_charset or 'utf-8')
        maildetails = get_mail_details(data)
        return maildetails



    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            print('exited normally\n')
            self.server.quit()
        else:
            print('raise an exception! ' + str(exc_type))
            self.server.close()
            return False # Propagate



if __name__ == '__main__':
    useraccount = "XXXXX"
    password = "XXXXXX"

    client = EmailClient(useraccount, password)
    client.get_mails_count()