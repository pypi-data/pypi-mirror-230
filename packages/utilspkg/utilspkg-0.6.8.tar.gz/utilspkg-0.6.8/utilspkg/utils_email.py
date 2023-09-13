from email.message import EmailMessage
import os
import smtplib

from utilspkg import utils_init

if __name__ == '__main__':
    utils_init.load_env_variables_from_yaml('/Users/croft/VScode/ptagit/env_vars.yaml')

logger = utils_init.setup_logger(__name__)

class EmailConnect:
    """
    A utility class to send emails using Gmail's SMTP service.
    """

    def __init__(self, user_name=None, pw=None, from_name=None, testing_flag=False, testing_email=None):
        """
        Constructs an instance of the EmailSender class.
        
        Args:
            user_name (str, optional): Gmail username to send emails. Defaults to GMAIL_USER environment variable.
            pw (str, optional): Gmail password. Defaults to GMAIL_PASSWORD environment variable.
            from_name (str, optional): Sender's display name in email. Defaults to GMAIL_FROM environment variable.
            testing_flag (bool, optional): Indicates whether to use a testing email address. Defaults to False.
            testing_email (str, optional): Testing email address. Defaults to TESTING_EMAIL environment variable.
        """
        self.user_name = user_name if user_name else os.environ['GMAIL_USER']
        self.pw = pw if pw else os.environ['GMAIL_PASSWORD']
        self.from_name = from_name if from_name else os.environ['GMAIL_FROM']
        self.testing_flag = testing_flag
        self.testing_email = testing_email if testing_email else os.environ['TESTING_EMAIL']


    def send_email(self, to, subject, body, testing_flag=None):
        """
        Sends an email with the specified details using the Gmail SMTP service.

        Args:
            to (str): The recipient's email address.
            subject (str): The email subject.
            body (str): The email body.
            testing_flag (bool, optional): If set, overrides the `testing_flag` attribute of the class. Defaults to None.
        """
        if testing_flag is None:
            testing_flag = self.testing_flag
        to = to if not testing_flag else self.testing_email
        message = EmailMessage()
        message.set_content(body)
        message["From"] = self.from_name
        message["To"] = to
        message["Subject"] = subject

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(self.user_name, self.pw)
            server.send_message(message)
