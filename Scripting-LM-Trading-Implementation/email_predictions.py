import time, ssl, smtplib, os
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

DATA_PATH = "../models_DB.h5"

def send_email():
    with pd.HDFStore(DATA_PATH) as store:
        max_date = store['predictions/news/daily'].index.get_level_values(0).max().strftime('%Y-%m-%d')
        labels = store['predictions/news/daily'].loc[max_date]
        labels = labels[labels.BUY_V1 != labels.BUY_V2]
        labels.to_csv('%s_Predicitions.csv'% max_date)

    user = "firobeid92@gmail.com"
    key = "hlietvfbjugbforx"
    to = ['feras.obeid@lau.edu', 'nrancharan92@gmail.com', ' omar.itani@mavs.uta.edu',
          'amir.zemoodeh@utdallas.edu', 'Hussein.Safaoui.4@gmail.com']


    subject = 'Predictions for %s' % max_date
    email_body = """\
    Hello, 

    Choose BUY_V2 from those Predictions.

    Yours Sincerely,
    Firas's Computer"""

    attachment = '%s_Predicitions.csv'% max_date
    ### Define email ###
    message = MIMEMultipart()
    message['From'] = Header(user.split("@")[0])
    # message['To'] = Header(to)     
    message['Subject'] = Header(subject)
    message.attach(MIMEText(email_body, 'plain', 'utf-8'))
    att_name = os.path.basename(attachment)
    att1 = MIMEText(open(attachment, 'rb').read(), 'base64', 'utf-8')
    att1['Content-Type'] = 'application/octet-stream'
    att1['Content-Disposition'] = 'attachment; filename=' + att_name
    message.attach(att1)

    context = ssl.create_default_context()
    email_port = 465
    with smtplib.SMTP_SSL(host = "smtp.gmail.com", port = email_port, context = context) as server:
        server.login(user, key)
        print(server.ehlo())
        if server.ehlo()[0] == 250:
            server.sendmail(key,to, message.as_string())
            print('Email sent successfully!')
            os.remove('%s_Predicitions.csv'% max_date)
            server.quit()
        else:
            print(f'Unable to establish connection with server! Error code: {server.ehlo()[0]}')
            server.quit()

if __name__ == '__main__':
    send_email()
