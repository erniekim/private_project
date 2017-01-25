import requests as rs
import bs4
import time
import datetime
import logging
import logging.handlers
import psycopg2
import smtplib

from email.mime.text import MIMEText

def getLandPrice(emailtext, today, conn, build_id, city_name, state_name, region_name, build_name, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region):
    cursor = conn.cursor()
    #print city_name + state_name + region_name + build_name + build_id
    sql_query = "SELECT * FROM realestateprice WHERE BuildID = (%s) and recorddate = (%s);"
    #INSERT INTO realestateprice (recorddate, date, buildname, buildid, buildnum, floor, price, description, city, state, region, buildsize) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
    cursor.execute(sql_query, (build_id,today, ))
    apt_cnt = 0
    total_price_pyeong = 0
    for apt_item in cursor :
        price_pyeong_1st = ""
        apt_cnt = apt_cnt + 1
        price = int(apt_item[4].replace(',',''))
        #price_pyeong_1st = apt_item[12].split('/')[0].split('-')[0].rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        #price_pyeong = int(price_pyeong_1st.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) / 3.3
        for i, c in enumerate(apt_item[12]):
            if c >='0' and c <= '9':
                price_pyeong_1st = '%s%c'%(price_pyeong_1st,c)
            else :
                break
        price_pyeong = int(price_pyeong_1st) / 3.3
        total_price_pyeong = total_price_pyeong + (price / price_pyeong )

        if price > highest_price :
            highest_price = price
            highest_name = '%s'%(apt_item[1]) + "(" + apt_item[12] + ")"
            highest_region = region_name

    cursor.close()
   
    cursor_rank = conn.cursor()
    if apt_cnt > 0:
        #print apt_item[1] + " " + "%.1f"%(total_price_pyeong/apt_cnt)
        emailtext = '%s\n%s'%(emailtext,apt_item[1] + " " + "%.1f"%(total_price_pyeong/apt_cnt))
        sql_rank_query = "INSERT INTO rankrealestate (region, buildname, pricepyeong, rankdate) VALUES (%s, %s, %s, %s);"

        cursor_rank.execute(sql_rank_query, (state_name, apt_item[1],int(total_price_pyeong/apt_cnt), today, ))

        if (total_price_pyeong/apt_cnt) > highest_pyeong_price :
            highest_pyeong_price = total_price_pyeong/apt_cnt
            highest_pyeong_name = '%s'%(apt_item[1])
            highest_pyeong_region = region_name 
    #print (cursor.fetchall())
    conn.commit()
    cursor_rank.close()
    return emailtext, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region

def getTopRank(emailtext, today, conn, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region):
    text = ""
    text_2nd = ""
    #daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&rletNo=111414&hscpTypeCd=B01%3AB02%3AB03&page='+str(page)
    #daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=4157010300'
    main_url = 'http://land.naver.com/article/cityInfo.nhn?cortarNo=1100000000&rletNo=&rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cpId=&location=&siteOrderCode='   

    response_main = rs.get(main_url)
    html_content_main = response_main.text.encode(response_main.encoding)
    navigator_main = bs4.BeautifulSoup(html_content_main, "html.parser")
    main_link = navigator_main.find("div", attrs={"id": "loc_view1"})
    resultList_main = main_link.find_all("option")      

    for index_main, keword_main in enumerate(resultList_main) :
    #for k in range(0,1) :
        #print '%s(%s)'%(keword_main.get_text().replace('\n', '').replace('\r', ''),keword_main.get("value").replace('\n', '').replace('\r', ''))
        detail_state_url = 'http://land.naver.com/article/cityInfo.nhn?cortarNo=' + str(keword_main.get("value").replace('\n', '').replace('\r', '')) + '&rletNo=&rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cpId=&location=&siteOrderCode='
        #detail_state_url = 'http://land.naver.com/article/cityInfo.nhn?cortarNo=4100000000&rletNo=&rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cpId=&location=&siteOrderCode='

        response = rs.get(detail_state_url)
        html_content = response.text.encode(response.encoding)

        navigator = bs4.BeautifulSoup(html_content, "html.parser")

        first_link = navigator.find("div", attrs={"id": "loc_view2"})
        
        resultList = first_link.find_all("option")        
        for index, keword in enumerate(resultList) :
        #for j in range(0,1) :
            #text =
            #if resultList:
            if keword.get("value") != None :
                #print '%s\n %s(%s)'%(text,keword.get_text().replace('\n', '').replace('\r', ''),keword.get("value").replace('\n', '').replace('\r', ''))
                detail_city_url = 'http://land.naver.com/article/divisionInfo.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=' + str(keword.get("value").replace('\n', '').replace('\r', '')) + '&articleOrderCode=&siteOrderCode=&cpId=&mapX=&mapY=&mapLevel=&minPrc=&maxPrc=&minWrrnt=&maxWrrnt=&minLease=&maxLease=&minSpc=&maxSpc=&subDist=&mviDate=&hsehCnt=&rltrId=&mnex=&mHscpNo=&mPtpRange=&mnexOrder=&location=&ptpNo=&bssYm=&schlCd=&cmplYn='
                #detail_city_url = 'http://land.naver.com/article/divisionInfo.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=4157000000&articleOrderCode=&siteOrderCode=&cpId=&mapX=&mapY=&mapLevel=&minPrc=&maxPrc=&minWrrnt=&maxWrrnt=&minLease=&maxLease=&minSpc=&maxSpc=&subDist=&mviDate=&hsehCnt=&rltrId=&mnex=&mHscpNo=&mPtpRange=&mnexOrder=&location=&ptpNo=&bssYm=&schlCd=&cmplYn='

                emailtext = '%s<%s>'%(emailtext,keword.get_text().replace('\n', '').replace('\r', ''))

                response_detail = rs.get(detail_city_url)
                html_content_detail = response_detail.text.encode(response_detail.encoding)
                navigator_detail = bs4.BeautifulSoup(html_content_detail, "html.parser")

                second_link = navigator_detail.find("div", attrs={"id": "loc_view3"})
                #print second_link
                resultList_2nd = second_link.find_all("option")

                for index_detail, keword_detail in enumerate(resultList_2nd) :
                    if keword_detail.get("value") != "_" :
                        #text_2nd =
                        #print '%s(%s)'%(keword_detail.get_text().replace('\n', '').replace('\r', ''),keword_detail.get("value").replace('\n', '').replace('\r', ''))
                        detail_apt_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=' + str(keword_detail.get("value").replace('\n', '').replace('\r', ''))
                        #print detail_apt_url
                        response_apt = rs.get(detail_apt_url)
                        html_content_apt = response_apt.text.encode(response_apt.encoding)
                        navigator_apt = bs4.BeautifulSoup(html_content_apt, "html.parser")
                        
                        third_link = navigator_apt.find("div", attrs={"id": "loc_view4"})
                        #print third_link
                        resultList_3rd = third_link.find_all("option")
                        for index_apt, keword_apt in enumerate(resultList_3rd) :
                            if keword_apt.get("value") != "_" :
                                #text_2nd =
                                #print '%s(%s)'%(keword_apt.get_text().replace('\n', '').replace('\r', ''),keword_apt.get("value").replace('\n', '').replace('\r', ''))
                                emailtext, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region = getLandPrice(emailtext, today, conn, keword_apt.get("value"),"Gyeonggi-do", keword.get_text().replace('\n', '').replace('\r', ''), keword_detail.get_text(),keword_apt.get_text(), highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region)
                for index_detail, keword_detail in enumerate(resultList_2nd) :
                    if keword_detail.get("value") != "_" :
                        #text_2nd =
                        #print '%s(%s)'%(keword_detail.get_text().replace('\n', '').replace('\r', ''),keword_detail.get("value").replace('\n', '').replace('\r', ''))
                        detail_apt_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&rletNo=&cortarNo=' + str(keword_detail.get("value").replace('\n', '').replace('\r', '')) + '&hscpTypeCd=B01'
                        #print detail_apt_url
                        response_apt = rs.get(detail_apt_url)
                        html_content_apt = response_apt.text.encode(response_apt.encoding)
                        navigator_apt = bs4.BeautifulSoup(html_content_apt, "html.parser")
                        
                        third_link = navigator_apt.find("div", attrs={"id": "loc_view4"})
                        #print third_link
                        resultList_3rd = third_link.find_all("option")
                        for index_apt, keword_apt in enumerate(resultList_3rd) :
                            if keword_apt.get("value") != "_" :
                                #text_2nd =
                                #print '%s(%s)'%(keword_apt.get_text().replace('\n', '').replace('\r', ''),keword_apt.get("value").replace('\n', '').replace('\r', ''))
                                emailtext, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region = getLandPrice(emailtext, today, conn, keword_apt.get("value"),"Gyeonggi-do", keword.get_text().replace('\n', '').replace('\r', ''), keword_detail.get_text(),keword_apt.get_text(), highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region)
                emailtext = '%s\nHighest Price Apartment : %s'%(emailtext,highest_name +"("+ highest_region + ")" + " - " + '%d'%(highest_price))
                emailtext = '%s\nHighest Price Apartment per pyeong : %s'%(emailtext,highest_pyeong_name +"("+ highest_pyeong_region + ")" + " - " + '%.1f'%(highest_pyeong_price))
                #send_email_msg(emailtext)
                emailtext = ""
                highest_price = 0
                highest_pyeong_price = 0
    return emailtext, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region

def send_email_msg(emailtext):
    senderAddr = "actalent@gmail.com"
    recipientAddr = "actalent@gmail.com"
    
    msg = MIMEText(emailtext,_charset="utf8")
    msg['Subject'] = "Real Estate Price"
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
    
    emailtext, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region = getTopRank(emailtext, today, conn, highest_price, highest_name, highest_region, highest_pyeong_price, highest_pyeong_name, highest_pyeong_region)

    conn.close()

    #print "Highest Price Apartment :" + highest_name +"("+ highest_region + ")" + " - " + '%d'%(highest_price) 
    #print "Highest Price Apartment per pyeong :" + highest_pyeong_name +"("+ highest_pyeong_region + ")" + " - " + '%.1f'%(highest_pyeong_price)

    emailtext = '%s\nHighest Price Apartment : %s'%(emailtext,highest_name +"("+ highest_region + ")" + " - " + '%d'%(highest_price))
    emailtext = '%s\nHighest Price Apartment per pyeong : %s'%(emailtext,highest_pyeong_name +"("+ highest_pyeong_region + ")" + " - " + '%.1f'%(highest_pyeong_price))

    #print emailtext

    #print emailtext

if __name__ == '__main__' :
    Daemon()
