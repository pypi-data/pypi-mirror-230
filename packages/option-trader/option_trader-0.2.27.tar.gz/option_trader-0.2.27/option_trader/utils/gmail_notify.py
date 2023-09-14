
import sys

sys.path.append(r'/Users/jimhu/option_trader/src')

import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

from option_trader.settings import app_settings

def send_mail(send_from, send_to, subject, text, html, files=None,
              server='smtp.gmail.com', port=587):
    assert isinstance(send_to, list)

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.add_header('Content-Type','text/html')

    msg.attach(MIMEText(text, 'plain' ))
    msg.attach(MIMEText(html, 'html'))


    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)


    smtp = smtplib.SMTP(server, port)
    smtp.starttls()
    #smtp.login(send_from, "sdhbjsuhudmvuugp")    
    smtp.login(send_from, app_settings.MY_GMAIL_PASSWORD)    
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

if __name__ == '__main__':

    import logging

    logger = logging.getLogger(__name__)
    #files = ["C:\\Users\\jimhu\\option_trader\\sites\mysite\\users\\chrishua\\dataset\\fidelity\\Option_Summary_for_Account_185173665.csv", 
    #         "C:/Users/jimhu/option_trader/data/charts/AAPL_BB.png"]
    from option_trader.admin.site import site
    
    files = []
    mysite = site('mysite')
    mdf = mysite.get_monitor_df()
    user_name_list = mysite.get_user_list()

    for user_name in user_name_list:
        user_obj = mysite.get_user(user_name)
        to_addr = user_obj.get_user_email()
        watchlist = user_obj.get_default_watchlist()

        detail_df = mdf[mdf.symbol.isin(watchlist)]
        detail_df = detail_df[['symbol', 'last_price', '5 days change %', '10d change%', '30 days change %', 'support', 'resistence', 'trend', 'HV', 'IV1', 'earning', 'forward_PE', 'rating', 'bb_pos', 'rsi', 'macd', 'mfi']]
        detail_df.sort_values('5 days change %', inplace=True)

        summary_df = detail_df[['symbol', 'last_price', '5 days change %', '10d change%', '30 days change %']]

        from datetime import datetime
        import os

        today = str(datetime.now().date())

        report_path = os.path.join(user_obj.report_dir, 'watchlist_report_'+today+'.csv')
        #report_path = user_obj.report_dir+'/'+'watchlist_report_'+today+'.csv'

        detail_df.to_csv(report_path)

        files.append(report_path)

        for symbol in watchlist:
            bng_path = os.path.join(app_settings.CHART_ROOT_DIR,symbol+'_BB.png')
            if os.path.exists(bng_path):
                files.append(bng_path)
            else:
                logger.error('BNG file %s not found' % bng_path)


        send_mail("jim.huang.bellevue@gmail.com", 
                    [to_addr], 
                    'Watchlist Update!! (' + today + ')', 
                "watchlist for %s" %user_obj.user_name,
                summary_df.to_html(),             
                files)

