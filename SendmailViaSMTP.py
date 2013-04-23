#! /bin/env python
##############################################
# SendmailViaSMTP is a kit for sending mail
# under console throught exist SMTP server.
#
# Author: leopku#qq.com
#
# History:
#   2013-04-23:
#       * fixed a bug while adding an attachment(thanks http://weibo.com/u/1738440993).
#   2012-10-29:
#       * fixed problem under python 2.3.x.
#   2012-10-09:
#       * fixed bug under crontab.
#       * adjust priority to --file, --content and piped mode because of the bug above.
#   2012-09-30:
#       + add --log option for debugging errors.
#   2012-09-24:
#       * restruct the codes.
#       * update the version number to 1.2.
#   2012-08-20:
#       * fixed homepage link broken in README.rst(thanks http://weibo.com/royshan ).
#   2012-08-15:
#       + support attachments(-a or --attach option).
#   2012-03-13:
#       * Fixed sending mail under python 2.4x(thanks yong.yang).
#   2011-12-28:
#       + add README.rst.
#       + add pipe mode -- accept data as mail body which transfered through pipe.
#       + implement file mode.
#       * adjust the file mode has higher priority than option mode.
#   2011-12-23:
#       * Fixed auth not supported issue under 2.5.x(thanks doitmy).
#   2010-09-28:
#       * fixed --tls as turn on/off option.
#       * optimize help message.
#   2010-09-27:
#       + add support for Gmail(smtp.gmail.com).
#       * fixed bugs for multi recipients.
#       + first release.
##############################################

import sys
import os
import os.path
import fileinput

import smtplib
import mimetypes
from email import Encoders
from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

__author__ ="leopku#qq.com"
__date__ ="$2012-08-25 14:05:56$"

__usage__ = u'''python %prog [--host=smtp.yourdomain.com] <--port=110> [--user=smtpaccount] [--password=smtppass] <--subject=subject> [--file=filename]|[--content=mailbody] [--from=sender] [--to=reciver].

    example:
    1. echo "blablabla" | python %prog --host="mail.domain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain.com" --user="myname@yourdomain.com" --password="p4word" --subject="mail title"
    2. python %prog --host="mail.domain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain.com" --user="myname@yourdomain.com" --password="p4word" --subject="mail title" --file=/path/of/file
    3. python %prog --host="mail.yourdomain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain2.com;friends3@domain3.com" --user="myname@yourdomain.com" --password="p4word" -s "Hello from MailViaSMTP" -c "This is a mail just for testing."

    The priority of three content inputing method is: piped-data, --file, --content.'''

__version__ = '%prog 1.2'
__desc__ = u'''This is a command line kit for sending mail via smtp server which can use in multiple platforms like linux, BSD, Windows etc.
    This little kit was written by %s using python.
    The minimum version of python required was 2.3.''' % (__author__)

class Mail:
    """docstring for Mail"""
    def __init__(self, subject='', content='', m_from='', m_to='', m_cc=''):
        self.subject = subject
        self.content = MIMEText(content, 'html', 'utf-8')
        self.m_from = m_from
        self.m_to = m_to
        self.m_cc = m_cc

        self.body = MIMEMultipart('related')
        self.body['Subject'] = self.subject
        self.body['From'] = self.m_from
        self.body['To'] = self.m_to
        self.body.preamble = 'This is a multi-part message in MIME format.'

        self.alternative = MIMEMultipart('alternative')
        self.body.attach(self.alternative)
        self.alternative.attach(self.content)

    def attach(self, attachments):
        if attachments:
            for attachment in attachments:
                if not os.path.isfile(attachment):
                    print 'WARNING: Unable to attach %s because it is not a file.' % attachment
                    continue

                ctype, encoding = mimetypes.guess_type(attachment)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)

                fp = open(attachment, 'rb')
                attachment_mime = MIMEBase("application", "octet-stream")
                attachment_mime.set_payload(fp.read())
                fp.close()

                Encoders.encode_base64(attachment_mime)
                attachment_mime.add_header('Content-Disposition', 'attachment', filename=attachment)
                self.body.attach(attachment_mime)

class SMTPServer:
    """docstring for SMTPServer"""
    def __init__(self, host='localhost', user='', password='', port=25, tls=False):
        self.port = port
        self.smtp = smtplib.SMTP()
        self.host = host
        self.user = user
        self.password = password
        self.is_gmail = False
        if self.host == 'smtp.gmail.com':
           self.is_gmail = True
           self.port = 587
        self.tls = tls

    def sendmail(self, mail):
        self.smtp.connect(self.host, self.port)
        if self.tls or self.is_gmail:
            self.smtp.starttls()
            self.smtp.ehlo()
            self.smtp.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
        if self.user:
            self.smtp.login(self.user, self.password)
        self.smtp.sendmail(mail.m_from, mail.m_to.split(';'), mail.body.as_string())
        self.smtp.quit()

if __name__ == "__main__":
    import optparse
    import logging

    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    LOG_FILENAME = os.path.join(PROJECT_ROOT, 'sendmail.log')

    parser = optparse.OptionParser(usage=__usage__, version=__version__, description=__desc__)
    parser.add_option('-a', '--attach', dest='attach', default=[], action='append', help='Specifies a file as attachment to be attached. Can be specified more than once.')
    parser.add_option('-s', '--subject', dest='subject', help='The subject of the mail.')
    parser.add_option('-c', '--content', dest='content', help='option mode. Mail body should be passed through this option. Note: this option should be ignored while working with piped-data or --file option.')
    parser.add_option('-f', '--from', dest='address_from', metavar='my@domain.com', help='Set envelope from address. If --user option is not empty, commonly this option should be equaled with --user options. Otherwize, the authoration of the smtp server should be failed.')
    parser.add_option('-t', '--to', dest='address_to', metavar='friend@domain2.com', help='Set recipient address. Use semicolon to seperate multi recipient, for example: "a@a.com;b@b.com."')
    parser.add_option('-F', '--file', dest='file', help='File mode. Read mail body from file. NOTE: this option should be ignored while working with piped-data.')
    parser.add_option('--host', dest='host', metavar='smtp.domain.com', help='SMTP server host name or ip. Like "smtp.gmail.com" through GMail(tm) or "192.168.0.99" through your own smtp server.')
    parser.add_option('-P', '--port', dest='port', type='int', default=25, help='SMTP server port number. Default is %default.')
    parser.add_option('-u', '--user', dest='user', metavar='my@domain.com', help='The username for SMTP server authorcation. Left this option empty for non-auth smtp server.')
    parser.add_option('-p', '--password', dest='password', help='The password for SMTP server authorcation. NOTE: if --user option is empty, this option will be ignored.')
    parser.add_option('--tls', dest='tls', action='store_true', help='Using tls to communicate with SMTP server. Default is false. NOTE: if --host option equals "smtp.gmail.com", this option becomes defaults true.')
    parser.add_option('--log', dest='log', default='critical', help='specify --log=DEBUG or --log=debug, more info see document for logging module.')
    opts, args= parser.parse_args()

    numeric_level = getattr(logging, opts.log.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % opts.log)
    if sys.version_info < (2, 3, 0):
        raise 'Python runtime MUST greater than 2.3.0'
    elif sys.version_info > (3, 0, 0):
        raise 'Python 3.0 was NOT recommented!'
    elif sys.version_info >= (2, 3, 0) and sys.version_info < (2, 4, 0):
        logging.basicConfig()
    else:
        logging.basicConfig(filename=LOG_FILENAME, level=numeric_level, format='%(asctime)s %(message)s')

    if opts.host is None or opts.address_from is None or opts.address_to is None:
        msg = '''ERROR:  All parameters followed were required: --host, --from and --to.
            Use -h to get more help.'''
        logging.critical(msg)
        sys.exit(msg)

    content = None
    filename = None
    if opts.content:
        logging.debug('[param mode] %s' % opts.content)
        content = opts.content # content mode, mail content should read from --content option.

    if opts.file:
        logging.debug('[file mode] %s' % opts.file)
        filename = opts.file # file mode, mail content should read from file.
    if content is None and filename is None and not isatty(0):
        logging.debug('[pip mode]')
        filename = '-' # pipe mode - mail content should read from stdin.
    if filename:
        try:
            fi = fileinput.FileInput(filename)
            logging.debug('[filename] %s' % filename)
            content = '<br />'.join(fi)
        except:
            logging.critical('can not open %s.' % filename)
    logging.debug('[content]%s' % content)
    if content:
        try:
            logging.info('preparing mail...')
            mail = Mail(opts.subject, content, opts.address_from, opts.address_to)
            logging.info('preparing attachments...')
            mail.attach(opts.attach)
            logging.info('preparing SMTP server...')
            smtp = SMTPServer(opts.host, opts.user, opts.password, opts.port, opts.tls)
            logging.info('sending mail...')
            smtp.sendmail(mail)
            logging.info('all done.')
        except Exception, e:
            logging.critical('[Exception]%s' % e)
    else:
        msg = '''ERROR: Mail content is EMPTY! Please specify one option of listed: piped-data, --file or --content.
            Use -h to get more help.'''
        logging.critical(msg)
        sys.exit(msg)
