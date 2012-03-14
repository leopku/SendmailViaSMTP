#! /bin/env python
##############################################
# SendmailViaSMTP is a kit for sending mail
# under console throught exist SMTP server.
#
# Author: leopku#qq.com
#
# History:
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
import fileinput

__author__="leopku@qq.com"
__date__ ="$2011-12-28 12:34:56$"

def build_mail(subject, text, address_from, address_to, address_cc=None, images=None):
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.MIMEImage import MIMEImage

    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = address_from
    msgRoot['To'] = address_to
    #text_msg = MIMEText(text)
    #msgRoot.attach(text_msg)
    msgRoot.preamble = 'This is a multi-part message in MIME format.'
    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)
    msgContent = MIMEText(text, 'html', 'utf-8')
    msgAlternative.attach(msgContent)

    return msgRoot

def send_mail(subject, content, address_from, address_to, smtp_host, smtp_user, smtp_password, smtp_port=25,using_tls=False):
    import smtplib
    smtp = smtplib.SMTP()
    # smtp = smtplib.SMTP(smtp_host)
    is_gmail = False
    if smtp_host == "smtp.gmail.com":
        is_gmail = True
    if is_gmail:
        smtp_port = 587
    smtp.connect(smtp_host, smtp_port)
    if using_tls or is_gmail:
        smtp.starttls()
        smtp.ehlo() # must do while python is 2.5.x or lower.
        smtp.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
    if smtp_user:
        smtp.login(smtp_user, smtp_password)
    mailbody = build_mail(subject, content, address_from, address_to)
    smtp.sendmail(address_from, address_to.split(';'), mailbody.as_string())
    smtp.quit()
    ## end of http://code.activestate.com/recipes/473810/
    
if __name__ == "__main__":
    import optparse
    USAGE = 'python %prog [--host=smtp.yourdomain.com] <--port=110> [--user=smtpaccount] [--password=smtppass] <--subject=subject> [--file=filename]|[--content=mailbody] [--from=sender] [--to=reciver].\n\nexample: \n\n1.echo "blablabla" | python %prog --host="mail.domain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain.com" --user="myname@yourdomain.com" --password="p4word" --subject="mail title"\n\n2. python %prog --host="mail.domain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain.com" --user="myname@yourdomain.com" --password="p4word" --subject="mail title" --file=/path/of/file\n\n3.%prog --host="mail.yourdomain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain2.com;friends3@domain3.com" --user="myname@yourdomain.com" --password="p4word" -s "Hello from MailViaSMTP" -c "This is a mail just for testing."\n\nThe priority of three content inputing method is: piped-data, --file, --content.'
    VERSION = '%prog 1.1'
    DESC = u"""This is a command line kit for sending mail via smtp server which can use in multiple platforms like linux, BSD, Windows etc. This little kit was written by leopku#qq.com using python. The minimum version of python required was 2.3."""

    parser = optparse.OptionParser(usage=USAGE, version=VERSION, description=DESC)
    parser.add_option('-s', '--subject', help='The subject of the mail.')
    parser.add_option('-c', '--content', help='option mode. Mail body should be passed through this option. Note: this option should be ignored while working with piped-data or --file option.')
    parser.add_option('-f', '--from', dest='address_from', metavar='my@domain.com', help='Set envelope from address. If --user option is not empty, commonly this option should be equaled with --user options. Otherwize, the authoration of the smtp server should be failed.')
    parser.add_option('-t', '--to', dest='address_to', metavar='friend@domain2.com', help='Set recipient address. Use semicolon to seperate multi recipient, for example: "a@a.com;b@b.com."')
    parser.add_option('-F', '--file', dest='file', help='File mode. Read mail body from file. NOTE: this option should be ignored while working with piped-data.')
    parser.add_option('--host', metavar='smtp.domain.com', help='SMTP server host name or ip. Like "smtp.gmail.com" through GMail(tm) or "192.168.0.99" through your own smtp server.')
    parser.add_option('-P', '--port', type='int', default=25, help='SMTP server port number. Default is %default.')
    parser.add_option('-u', '--user', metavar='my@domain.com', help='The username for SMTP server authorcation. Left this option empty for non-auth smtp server.')
    parser.add_option('-p', '--password', help='The password for SMTP server authorcation. NOTE: if --user option is empty, this option will be ignored.')
    parser.add_option('--tls', action='store_true', help='Using tls to communicate with SMTP server. Default is false. NOTE: if --host option equals "smtp.gmail.com", this option becomes defaults true.')
    opts, args= parser.parse_args()

    if opts.host is None or opts.address_from is None or opts.address_to is None:
        sys.exit('ERROR:  All parameters followed were required: --host, --from and --to.\n\nUse -h to get more help.')

    content = None
    filename = None
    if opts.content:
        content = opts.content # content mode, mail content should read from --content option.

    if opts.file:
        filename = opts.file # file mode, mail content should read from file.
    if not os.isatty(0):
        filename = '-' # pipe mode - mail content should read from stdin.
    if filename:
        
        try:
            fi = fileinput.FileInput(filename)
            content = '<br />'.join(fi)
        except:
            pass
    if content:
        send_mail(opts.subject, content, opts.address_from, opts.address_to, opts.host,opts.user, opts.password,  opts.port, opts.tls)
    else:
        sys.exit('ERROR: Mail content is EMPTY! Please specify one option of piped-data or --file or --content.\n\nUse -h to get more help.')
