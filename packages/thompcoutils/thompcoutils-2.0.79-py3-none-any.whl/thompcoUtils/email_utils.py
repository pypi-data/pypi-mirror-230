from thompcoUtils.config_utils import ConfigManager
from thompcoUtils.config_utils import EmailConnectionConfig
from thompcoUtils.log_utils import get_logger
from thompcoUtils.cell_phone import CellPhone
import smtplib
import os
from email import encoders
import mimetypes
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage


if os.name == 'nt' or os.name == "posix":
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
else:
    # noinspection PyUnresolvedReferences
    from email.MIMEMultipart import MIMEMultipart
    # noinspection PyUnresolvedReferences
    from email.MIMEText import MIMEText
    # noinspection PyUnresolvedReferences
    from email.MIMEApplication import MIMEApplication


class EmailSender:
    def __init__(self, email_cfg, smtp_host=None, smtp_port=None, username=None, password=None, from_user=None,
                 use_tls=None, use_authentication=None):
        if email_cfg is None:
            self.smtp_host = smtp_host
            self.smtp_port = smtp_port
            self.username = username
            self.password = password
            self.from_user = from_user
            self.use_tls = use_tls
            self.use_authentication = use_authentication
        else:
            self.smtp_host = email_cfg.smtp_host
            self.smtp_port = email_cfg.smtp_port
            self.username = email_cfg.username
            self.password = email_cfg.password
            self.from_user = email_cfg.from_user
            self.use_tls = email_cfg.use_tls
            self.use_authentication = email_cfg.use_authentication

    def send_text(self, to_cell, message):
        logger = get_logger()
        logger.debug("sending to:{}, message:{}".format(to_cell.as_email(), message))
        server = smtplib.SMTP(self.smtp_host, self.smtp_port)
        if self.use_tls:
            server.starttls()
        if self.use_authentication:
            server.login(self.username, self.password)
        complete_message = ('From:{}\r\nTo:{}\r\nSubject:{}'.format(self.smtp_host,
                                                                    to_cell.as_email(),
                                                                    message))
        server.sendmail(from_addr=self.smtp_host,
                        to_addrs=to_cell.as_email(),
                        msg=complete_message)
        logger.debug('Sent message "{}"'.format(message))

    def send(self, to_email, subject, message, attach_files=None):
        logger = get_logger()
        logger.debug("sending to:{} subject:{}, message:{}, files:{}".format(to_email, subject, message, attach_files))
        if isinstance(attach_files, str):
            attach_files = [attach_files]
        logger = get_logger()
        server = None
        try:
            server = smtplib.SMTP(host=self.smtp_host, port=self.smtp_port)
            server.ehlo()
            server.starttls()
            server.login(self.username, self.password)
            outer_msg = MIMEMultipart('alternative')
            outer_msg['Subject'] = subject
            outer_msg.attach(MIMEText(message, "html"))
            outer_msg['From'] = self.from_user
            if isinstance(to_email, list):
                outer_msg['To'] = ", ".join(to_email)
            else:
                outer_msg['To'] = to_email
            if attach_files is not None:
                for filename in attach_files:
                    file_type, encoding = mimetypes.guess_type(filename)
                    if file_type is None or encoding is not None:
                        file_type = 'application/octet-stream'
                    maintype, subtype = file_type.split('/', 1)
                    if maintype == 'text':
                        with open(filename) as fp:
                            msg = MIMEText(fp.read(), _subtype=subtype)
                    elif maintype == 'image':
                        with open(filename, 'rb') as fp:
                            msg = MIMEImage(fp.read(), _subtype=subtype)
                    elif maintype == 'audio':
                        with open(filename, 'rb') as fp:
                            msg = MIMEAudio(fp.read(), _subtype=subtype)
                    else:
                        with open(filename, 'rb') as fp:
                            msg = MIMEBase(maintype, subtype)
                            msg.set_payload(fp.read())
                        encoders.encode_base64(msg)
                    msg.add_header('Content-Disposition', 'attachment', filename=filename)
                    outer_msg.attach(msg)
            server.sendmail(self.from_user, to_email, outer_msg.as_string())
            logger.debug("Successfully sent mail to " + str(to_email))
        finally:
            if server is not None:
                server.quit()

    def send_embedded_images(self, to_email, subject, html, files):
        msg_root = MIMEMultipart('related')
        msg_root['Subject'] = subject
        msg_root['From'] = self.from_user
        msg_root['To'] = to_email
        msg_root.preamble = 'This is a multi-part message in MIME format.'

        msg_alternative = MIMEMultipart('alternative')
        msg_root.attach(msg_alternative)

        msg_text = MIMEText('Image(s)')
        msg_alternative.attach(msg_text)

        msg_text = MIMEText(html, 'html')
        msg_alternative.attach(msg_text)

        count = 1
        for file in files:
            fp = open(file, 'rb')
            msg_image = MIMEImage(fp.read())
            fp.close()
            msg_image.add_header('Content-ID', '<image{}>'.format(count))
            count += 1
            msg_root.attach(msg_image)

        import smtplib
        smtp = smtplib.SMTP(self.smtp_host, self.smtp_port)
        smtp.ehlo()
        smtp.starttls()
        smtp.login(self.username, self.password)
        smtp.sendmail(self.from_user, to_email, msg_root.as_string())
        smtp.quit()


def main():
    logger = get_logger()
    create_file = False
    temp_filename = "testing EmailCfg only.ini"
    if create_file:
        if os.path.isfile(temp_filename):
            os.remove(temp_filename)
    cfg_mgr = ConfigManager(file_name=temp_filename, create=create_file)
    if create_file:
        EmailConnectionConfig(cfg_mgr=cfg_mgr)
        logger.debug("Writing out configuration file to {} and stopping.".format(temp_filename))
        cfg_mgr.write(out_file=temp_filename, overwrite=True)
        raise Exception("Should never get here!")
    email_cfg = EmailConnectionConfig(cfg_mgr)
    mail_from_cfg = EmailSender(email_cfg)
    mail_from_cfg.send_text(CellPhone(number=3217778377, carrier=CellPhone.Carrier.T_MOBILE),
                            '>testing from thompcoUtils<')
    html_message = '<b>Some <i>HTML</i> text</b> and an image.<br>'\
                   '<img src="cid:image1">'\
                   '<img src="cid:image2">'\
                   '<br>Nifty!'

    mail_from_cfg.send_embedded_images("Jordan@ThompCo.com", "Testing", html_message,
                                       ["../attachments/image_1.png", "../attachments/image_2.png"])

    mail_from_cfg.send_embedded_images(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                                       html=html_message,
                                       files=["../attachments/image_1.png"])

    mail_from_cfg.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                       message="Here is the message using parameters passed in with an attached file",
                       attach_files=[os.path.basename(__file__)])
    mail_from_cfg.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                       message="Here is the message using parameters passed in")
    mail_from_cfg.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                       message="Here is the message using values from a configuration file with an attached file",
                       attach_files=[os.path.basename(__file__)])
    mail_from_cfg.send(to_email="Jordan@ThompCo.com", subject="this is a test from emailSender",
                       message="Here is the message using values from a configuration file")


if __name__ == "__main__":
    main()
