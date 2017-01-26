# -*- coding:utf-8 -*-

import requests as rs
import bs4
import time
import datetime
import logging
import logging.handlers
import psycopg2
import smtplib
import urllib2

from konlpy.tag import Kkma

from email.mime.text import MIMEText


def getTopRank(today, logger, conn):
    text = ""
    Region = ""
    City = ""
    State = ""
    BuildID = ""
    BuildName = ""
    cursor = conn.cursor()
    page = 1
    page_size = 99
    while page_size > 1:
        # daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&rletNo=111414&hscpTypeCd=B01%3AB02%3AB03&page='+str(page)
        daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&tradeTypeCd=A1&rletNo=105159&hscpTypeCd=A01&page=' + str(
            page)
        response = rs.get(daum_url)

        html_content = response.text.encode(response.encoding)

        navigator = bs4.BeautifulSoup(html_content, "html.parser")

        # resultList_region_Name = navigator.find_all("input", attrs={"name": "cortarNo"})
        resultList_building_Name = navigator.find("input", attrs={"name": "rletNo"})
        resultList = navigator.find_all("div", class_="inner")
        page_size = len(resultList)

        first_link = navigator.find("div", attrs={"id": "loc_view4"})
        resultList_building_realname = first_link.find("div", class_="selectbox-label")

        second_link = navigator.find("div", attrs={"id": "loc_view2"})
        # resultList_state_name = second_link.find_all("div", class_="selectbox-label")
        resultList_state_name = second_link.find("option", selected=True)

        third_link = navigator.find("div", attrs={"id": "loc_view1"})
        # resultList_city_name = third_link.find_all("div", class_="selectbox-label")
        resultList_city_name = third_link.find("option", selected=True)

        forth_link = navigator.find("div", attrs={"id": "loc_view3"})
        # resultList_city_name = third_link.find_all("div", class_="selectbox-label")
        resultList_region_Name = forth_link.find("option", selected=True)

        # for index, keword in enumerate(resultList_region_Name) :
        #    Region = '%s\n %s'%(Region,keword.get("value").replace('\n', '').replace('\r', ''))
        Region = resultList_region_Name.get("value")

        # for index, keword in enumerate(resultList_building_Name) :
        #    BuildID = '%s\n %s'%(BuildID,keword.get("value").replace('\n', '').replace('\r', ''))
        BuildID = resultList_building_Name.get("value")

        # for index, keword in enumerate(resultList_state_name) :
        #    State = '%s\n %s'%(State,keword.get_text().replace('\n', '').replace('\r', ''))
        State = resultList_state_name.get("value")

        # for index, keword in enumerate(resultList_city_name) :
        #    City = '%s\n %s'%(City,keword.get_text().replace('\n', '').replace('\r', ''))
        City = resultList_city_name.get("value")

        BuildName = resultList_building_realname.get_text()

        logger.info('=========================================')
        now = datetime.datetime.now()
        logger.info(now.strftime("%Y/%m/%d %H:%M:%S"))
        logger.info('=========================================')

        i = 0

        for index, keword in enumerate(resultList):
            del keword['tabindex']
            # del keword['<span>']
            # del keword['</span>']
            # resultText = '[%2d] %s'%(index+1,keword.get_text().replace('\n', '').replace('\r', '').encode('utf-8'))
            # logger.info(resultText)
            if (i != 0):
                if (i == 2):
                    Date = '%s%s' % (text, keword.get_text().replace('\n', '').replace('\r', ''))
                if (i == 5):
                    BuildNum = '%s%s' % (text, keword.get_text().replace('\n', '').replace('\r', ''))
                if (i == 6):
                    Floor = '%s%s' % (text, keword.get_text().replace('\n', '').replace('\r', ''))
                if (i == 7):
                    Price = '%s%s' % (text, keword.get_text().replace('\n', '').replace('\r', ''))
                if (i == 9):
                    Description = '%s%s' % (text, keword.get_text().replace('\n', '').replace('\r', ''))
            # print emailtext
            # logger.info(keword)
            i = i + 1
            if i > 9:
                i = 1
                sql_query = 'INSERT INTO realestateprice (recorddate, date, buildname, buildid, buildnum, floor, price, description, city, state, region) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
                cursor.execute(sql_query, (
                today, Date, BuildName, BuildID, BuildNum, Floor, Price, Description, City, State, Region,))
                conn.commit()
        logger.info('')

        # print text
        print City
        print State
        print Region
        print BuildName
        print BuildID
        page = page + 1
    cursor.close()
    # return text


def Create_DB_Tabel(conn):
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE realestateprice(id varchar(20) primary key,date varchar(20), buildname varchar(100), buildnum varchar(20), floor varchar(20), price varchar(20), description varchar(200), city varchar(20), state varchar(20), region varchar(20));")
    conn.commit()
    cursor.close()


daemon_flag = True
reflash_time = 10;


def Daemon():
    emailtext = ""
    senderAddr = "actalent@gmail.com"
    recipientAddr = "actalent@gmail.com"

    now = datetime.datetime.now()
    today = '%s' % (now.strftime("%Y.%m.%d"))
    # print today

    try:
        conn = psycopg2.connect("dbname='younghokim' user='younghokim'  password='dkagh1gk'")
    except:
        print "not connect"

    logger = logging.getLogger('mylogger')
    fomatter = logging.Formatter('')

    filedate = datetime.datetime.now()
    fileHandler = logging.FileHandler('./myLog_%s.log' % (filedate.strftime("%Y%m%d")))
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(fomatter)
    streamHandler.setFormatter(fomatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    logger.setLevel(logging.DEBUG)

    main_page = 1

    kkma = Kkma()

    for i in range(0,5):
        #daum_url = 'https://www.google.co.kr/webhp?sourceid=chrome-instant&ion=1&espv=2&ie=UTF-8#q=%EB%B6%80%EB%8F%99%EC%82%B0&tbm=nws'
        daum_url = 'http://search.naver.com/search.naver?where=news&sm=tab_jum&ie=utf8&query=부동산&start=' + str(main_page)
        response = rs.get(daum_url)

        html_content = response.text.encode(response.encoding)

        navigator = bs4.BeautifulSoup(html_content, "html.parser")
        #resultList = navigator.find_all('div')
        resultList = navigator.find_all('dt')

        for index, keyword in enumerate(resultList):
            #print '%s\n' % (kkma.pos(keyword.get_text()).encode('utf-8'))
            splited_text = kkma.pos(keyword.get_text())
            for word_pos in enumerate(splited_text):
                num, word_tup = word_pos
                word, pos = word_tup
                print '%s (%s)\n' %(word.encode('utf-8'),pos.encode('utf-8'))

        main_page = main_page + 10


        # while(daemon_flag):
        # for page in range(5,6) :
        # getTopRank(today, logger, conn)
        #    time.sleep(reflash_time)

        # conn.commit()
        # cur.close()
        # Create_DB_Tabel(conn)

    #    conn.close()

    # print emailtext

    #    msg = MIMEText(emailtext,_charset="utf8")
    #    msg['Subject'] = "Real Estate Price"
    #    msg['From'] = senderAddr
    #    msg['to'] = recipientAddr

    #    s = smtplib.SMTP_SSL('smtp.gmail.com',465)
    #    s.login("actalent@gmail.com","dkagh1gk05")
    # s.sendmail(senderAddr, recipientAddr, msg.as_string())


#    s.quit()

if __name__ == '__main__':
    Daemon()
