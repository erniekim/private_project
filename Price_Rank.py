import requests as rs
import bs4
import time
import datetime
import logging
import logging.handlers
import psycopg2
import smtplib

from email.mime.text import MIMEText

def getRank(emailtext, today, conn,):
    cursor = conn.cursor()
    #print city_name + state_name + region_name + build_name + build_id
    sql_query = "SELECT * FROM rankrealestate WHERE rankdate = (%s) ORDER BY pricepyeong desc;"
    cursor.execute(sql_query, (today, ))
    i = 1
    
    for apt_item in cursor :
        emailtext = '%s %d | %s | %s | %s\n'%(emailtext, i, apt_item[1], apt_item[2], str(apt_item[4]))
        #print apt_item[1] + apt_item[2] + str(apt_item[4])
        #price_pyeong_1st = apt_item[12].split('/')[0].split('-')[0].rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        #price_pyeong = int(price_pyeong_1st.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) / 3.3
        i = i + 1

    cursor.close()
    return emailtext

def send_email_msg(emailtext):
    senderAddr = "actalent@gmail.com"
    recipientAddr = "actalent@gmail.com"
    
    msg = MIMEText(emailtext,_charset="utf8")
    msg['Subject'] = "Real Estate Price Rank"
    msg['From'] = senderAddr
    msg['to'] = recipientAddr

    s = smtplib.SMTP_SSL('smtp.gmail.com',465)
    s.login("actalent@gmail.com","dkagh1gk05")
    s.sendmail(senderAddr, recipientAddr, msg.as_string())

    s.quit()

daemon_flag = True
reflash_time = 10;

def Daemon():
    emailtext = ""

    highest_price = 0
    highest_name = ""
    highest_region = ""

    highest_pyeong_price = 0.0
    highest_pyeong_name = ""
    highest_pyeong_region = ""

    try:
     conn = psycopg2.connect("dbname='younghokim' user='younghokim'  password='dkagh1gk'")
    except:
     print "not connect"

    now = datetime.datetime.now()
    today = '%s'%(now.strftime("%Y.%m.%d"))
    today = "2017.01.20"
    
    emailtext = getRank(emailtext, today, conn)

    conn.close()

    send_email_msg(emailtext)
    #print "Highest Price Apartment :" + highest_name +"("+ highest_region + ")" + " - " + '%d'%(highest_price) 
    #print "Highest Price Apartment per pyeong :" + highest_pyeong_name +"("+ highest_pyeong_region + ")" + " - " + '%.1f'%(highest_pyeong_price)

    #print emailtext

    #print emailtext

if __name__ == '__main__' :
    Daemon()
