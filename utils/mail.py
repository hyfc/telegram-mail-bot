import poplib


class MailInfo(object):
    """
    Class for storing mail's metadata
    """
    def __init__(self):
        self.index = 0
        self.size = 0
        self.status = ""
        self.data = ""

class EmailClient(object):
    def __init__(self, email_account, password):
        self.email_account = email_account
        self.password = password
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

    def get_mail_count(self):
        _, mails, _ = self.server.list()
        return len(mails)



if __name__ == '__main__':
    useraccount = "XXXXX"
    password = "XXXXXX"

    client = EmailClient(useraccount, password)
    client.get_mail_count()