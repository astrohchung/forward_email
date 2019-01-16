
# coding: utf-8

# !jupyter nbconvert --no-prompt --to=python cond_email_forward.ipynb


import imaplib
import time
import email
import smtplib
from email.mime.text import MIMEText
from email import policy
from datetime import datetime


class Mail():
    def __init__(self):
        self.user= 'id@gmail.com'
        self.password= 'passwd'
        self.M = imaplib.IMAP4_SSL('imap.gmail.com', '993')
        self.M.login(self.user, self.password)
        
    def checkMail(self):
        self.M.select()
        self.unRead = self.M.search(None, 'UnSeen')
        return len(self.unRead[1][0].split())
    
    def fetchMail(self):
        typ, data=self.M.fetch((self.unRead[1][0].split())[0], '(RFC822)')
        str_cont=data[0][1]
        self.msg = email.message_from_bytes(str_cont, policy=policy.default)    # predefined policy of message_from_bytes 
                                                                                # is compatible with Python3.2, which 
                                                                                # does not have get_body() attribute. 
        
    def checkSender(self, kwd):
        sender=self.msg['From']
        return sender.find(kwd)
    
    def readbody(self):
        mime_body=self.msg.get_body('text/plain')
        text=mime_body.get_payload(decode=True)
        return text.decode()
        
    def sendMail(self, subject, body, address):
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.ehlo()      # say Hello
        smtp.starttls()  # required when using TLS
        smtp.login('id@gmail.com', 'passwd')

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['To'] = address
        smtp.sendmail('id@gmail.com', address, msg.as_string())
        smtp.quit()
        
    def logout(self):
        self.M.logout()

        
if __name__ == "__main__":
    mail=Mail()
    cnt=0
    print('Start Monitering')
    while True:
        if cnt > 30:
            mail.logout()    # to prevent timeout error, active logout/login is required (here 30 minutes interval).
            cnt=0
            print('logout')
        if cnt ==0:
            mail=Mail()
            print('login')
        ctime=str(datetime.now())
        nnew=mail.checkMail()   # check number of new (unseen) email.
        print(ctime+' '+str(nnew))
        if nnew > 0:
            mail.fetchMail()    # fetch an email from one of the unseen emails from the server.
                                # Status of the fetched email is automatically changed to 'Seen', therefore no longer
                                # counted by mail.checkMail()
                    
            kwd='university.edu'       # Keyword to match with the sender's address
            if mail.checkSender(kwd) >0:    # check whether the keyword is in the sender's email address.
                body=mail.readbody()    # Read body of the email in the text format.
                
                subject='Automatically Forwarded Mail'
                addfront='This mail is automatically forwarded to ... \n\n\n'
                
                ofrom='From: '+mail.msg['From']+'\n'
                oto='To: '+mail.msg['To']+'\n'
                odate='Date: '+mail.msg['Date']+'\n'
                osub='Subject: '+mail.msg['Subject']+'\n\n'
                address='recipient@gmail.com'

                body=addfront+ofrom+odate+osub+oto+body
                mail.sendMail(subject, body, address)    # Send the mail to the receipent. 
                print('Sending')
        cnt+=1     # increase count by 1.
        time.sleep(60)     # wait for 60 seconds

