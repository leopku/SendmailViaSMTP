#! /bin/env python

import sys

__author__="leopku@qq.com"
__date__ ="$2010-9-27 14:36:59$"

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

def send_mail(subject, content, address_from, address_to, smtp_host, smtp_user, smtp_password):
    import smtplib
    smtp = smtplib.SMTP()
    smtp.connect(smtp_host)
    # smtp = smtplib.SMTP(smtp_host)
    if smtp_user:
        smtp.login(smtp_user, smtp_password)
    mailbody = build_mail(subject, content, address_from, address_to)
    smtp.sendmail(address_from, address_to.split(';'), mailbody.as_string())
    smtp.quit()
    ## end of http://code.activestate.com/recipes/473810/
if __name__ == "__main__":
    import optparse
    USAGE = 'python %prog [--host=smtp.yourdomain.com] <--port=110> [--user=smtpaccount] [--password=smtppass] <--subject=subject> [--content=mailbody]|[--file=filename] [--from=sender] [--to=reciver].\n\nexample: %prog --host="mail.yourdomain.com" --from="myname@yourdomain.com" --to="friends1@domain1.com;friends2@domain2.com;friends3@domain3.com" --user="my" --password="p4word" -s "Hello from MailViaSMTP" -c "This is a mail just for testing."'
    VERSION = '%prog 1.0'
    DESC = """This is a command line kit for sending mail via
    smtp server which can use in multiple platforms like linux, BSD, Windows etc.
    This little kit was written by leopku@qq.com using python.
    The minimum version of python required was 2.3."""

    parser = optparse.OptionParser(usage=USAGE, version=VERSION, description=DESC)
    parser.add_option('-s', '--subject', help='The subject of the mail.')
    parser.add_option('-c', '--content', help='The mail body of the mail.')
    parser.add_option('-f', '--from', dest='address_from', help='Set envelope from address.')
    parser.add_option('-t', '--to', dest='address_to', help="Set recipient address. Use comma to seperate multi recipient.")
    parser.add_option('-F', '--file', dest='file', help='Read mail body from file. NOTE:  --file will be ignored if work with --content option at same tome.')
    parser.add_option('--host', help='SMTP server host name or ip.')
    parser.add_option('-P', '--port', help='SMTP server port number.')
    parser.add_option('-u', '--user', help='The username for SMTP server authorcation. Left this option empty for non-auth smtp server.')
    parser.add_option('-p', '--password', help='The password for SMTP server authorcation. If --user option is empty, this option will be ignored.')
    opts, args= parser.parse_args()
    #print opts.host
    #print opts.user
    #print opts.password
    #if not opts.subject:
    #    opts.subject = ''
    if opts.host is None or opts.address_from is None or opts.address_to is None:
        sys.exit('ERROR:  All parameters belowed were required: --host, --from and --to.\n\nUse -h to get more help.')
    if opts.content:
        content = opts.content
    else:
        if opts.file:
            fp = open(opts.file, 'r')
            content = fp.read()
            fp.close()
        else:
            #raise Exception,'You must specify one of --content or --file.'
            #print 'Error: You must specify one of --content or --file.'
            #print 'Now exitting.'
            sys.exit('ERROR: One of --content and --file was required.\n\nUse -h to get more help.')

    send_mail(opts.subject, content, opts.address_from, opts.address_to, opts.host, opts.user, opts.password)