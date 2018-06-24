from pyzmail import PyzMessage, decode_text

class Email(object):
    def __init__(self, raw_mail_lines):
        msg_content = b'\r\n'.join(raw_mail_lines)
        msg =  PyzMessage.factory(msg_content)

        self.subject = msg.get_subject()
        self.sender = msg.get_address('from')
        self.date = msg.get_decoded_header('date', '')
        self.id = msg.get_decoded_header('message-id', '')

        for mailpart in msg.mailparts:
            if mailpart.is_body=='text/plain':
                payload, used_charset=decode_text(mailpart.get_payload(), mailpart.charset, None)
                self.charset = used_charset
                self.text = payload
                return
            else:
                self.text = None

    def __repr__(self):
        mail_str = "Subject: %s\n" % self.subject
        mail_str += "From: %s %s\n" % self.sender
        mail_str += "Date: %s\n" % self.date
        mail_str += "ID: %s\n" % self.id
        if self.text:
            mail_str += "Text: %s\n" % self.text
        return mail_str
