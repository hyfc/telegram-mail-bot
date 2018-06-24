import logging
import poplib
from utils.mail import Email


logger = logging.getLogger(__name__)



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
        logger.info(server.getwelcome().decode('utf8'))
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
        return Email(mail_lines)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            logger.info('exited normally\n')
            self.server.quit()
        else:
            logger.error('raise an exception! ' + str(exc_type))
            self.server.close()
            return False # Propagate



if __name__ == '__main__':
    useraccount = "XXXXX"
    password = "XXXXXX"

    client = EmailClient(useraccount, password)
    num = client.get_mails_count()
    print(num)
    for i in range(1, num):
        print(client.get_mail_by_index(i))