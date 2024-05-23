#!/usr/bin/env python3

import smtplib,ssl,email,argparse,configparser,os,sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

ssl_context = ssl.create_default_context()

# smtp_server = os.getenv("SCRIPT_SMTP_SERVER")
smtp_port = os.getenv("SCRIPT_SMTP_PORT","587")
smtp_user = os.getenv("SCRIPT_SMTP_USERNAME")
smtp_pw = os.getenv("SCRIPT_SMTP_PASSWORD")

argParser = argparse.ArgumentParser()
cfgParser = configparser.ConfigParser()
argParser.add_argument('--config-file','-c',help='Location for the config file to be used for email settings',default='config.ini')
argParser.add_argument('--cfg-section','-s',help='Section of the config ini to use for sending email',default='default')

args = argParser.parse_args()
cfg_file = args.config_file
cfg_section = args.cfg_section
mail_config = {}

def set_config():
    global mail_config
    try:
        cfg_read = configparser.read(cfg_file)
        mail_config = cfg_read[cfg_section]
        
    except Exception:
        print(f'Could not read config file at {cfg_file}: Exiting...')
        sys.exit(1)

def email_content() -> MIMEMultipart:
    global mail_config
    email_content = ''
    email_content_type = 'html'
    email_content_file = mail_config['email_content_file']
    try:
        with open(email_content_file) as f:
            email_content = f.read()
            if 'txt' in email_content_file:
                email_content_type = 'plain'
    except Exception:
        print(f'Could not find email content file {email_content_file}: falling back to default message.')
        email_content = 'TEST MESSAGE HERE'
        email_content_type = 'plain'
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = mail_config['email_subject']
    msg['From'] = mail_config['from_addr']
    msg['To'] = mail_config['to_addr']
    msg_content = MIMEText(email_content,email_content_type)
    msg.attach(msg_content)
    return msg
    
def sendmail():
    global mail_config
    smtp_server=mail_config['mail_server']
    mail_from = mail_config['from_addr']
    mail_to = mail_config['to_addr']
    email_msg = email_content()
    with smtplib.SMTP(smtp_server,smtp_port) as server:
        server.starttls(ssl_context)
        if smtp_user and smtp_pw:
            try:
                server.login(user=smtp_user,password=smtp_pw)
            except Exception as e:
                print(f"Could not log in to {smtp_server}: {e}")
                server.quit()
        
        server.sendmail(mail_from,mail_to,email_msg.as_string())

if __name__ == '__main__':
    set_config()
    sendmail()
