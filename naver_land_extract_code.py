import requests as rs
import bs4
import time
import datetime
import logging
import logging.handlers
import psycopg2


def getTopRank(logger):
    text = ""
    text_2nd = ""
    #daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&rletNo=111414&hscpTypeCd=B01%3AB02%3AB03&page='+str(page)
    #daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=4157010300'
    main_url = 'http://land.naver.com/article/cityInfo.nhn?cortarNo=1100000000&rletNo=&rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cpId=&location=&siteOrderCode='   

        
    logger.info('=========================================')
    now = datetime.datetime.now()
    logger.info(now.strftime("%Y/%m/%d %H:%M:%S"))
    logger.info('=========================================')

    response_main = rs.get(main_url)
    html_content_main = response_main.text.encode(response_main.encoding)
    navigator_main = bs4.BeautifulSoup(html_content_main, "html.parser")
    main_link = navigator_main.find("div", attrs={"id": "loc_view1"})
    resultList_main = main_link.find_all("option")      

    for index_main, keword_main in enumerate(resultList_main) :
        #print '%s\n %s(%s)'%(text,keword_main.get_text().replace('\n', '').replace('\r', ''),keword_main.get("value").replace('\n', '').replace('\r', ''))
        detail_state_url = 'http://land.naver.com/article/cityInfo.nhn?cortarNo=' + str(keword_main.get("value").replace('\n', '').replace('\r', '')) + '&rletNo=&rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cpId=&location=&siteOrderCode='
        response = rs.get(detail_state_url)
        #print detail_state_url
        html_content = response.text.encode(response.encoding)

        navigator = bs4.BeautifulSoup(html_content, "html.parser")

        first_link = navigator.find("div", attrs={"id": "loc_view2"})
        
        resultList = first_link.find_all("option")        
        for index, keword in enumerate(resultList) :
            #text =
            if keword.get("value") != None :
                #print '%s\n %s(%s)'%(text,keword.get_text().replace('\n', '').replace('\r', ''),keword.get("value").replace('\n', '').replace('\r', ''))
                detail_city_url = 'http://land.naver.com/article/divisionInfo.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=' + str(keword.get("value").replace('\n', '').replace('\r', '')) + '&articleOrderCode=&siteOrderCode=&cpId=&mapX=&mapY=&mapLevel=&minPrc=&maxPrc=&minWrrnt=&maxWrrnt=&minLease=&maxLease=&minSpc=&maxSpc=&subDist=&mviDate=&hsehCnt=&rltrId=&mnex=&mHscpNo=&mPtpRange=&mnexOrder=&location=&ptpNo=&bssYm=&schlCd=&cmplYn='

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
    logger.info('')

    #print text
    #print text_2nd
    #print name_text
    #print name_build_text
    return text

daemon_flag = True
reflash_time = 10;

def Daemon():
    emailtext = ""
    senderAddr = "actalent@gmail.com"
    recipientAddr = "actalent@gmail.com"

    try:
     conn = psycopg2.connect("dbname='younghokim' user='younghokim'  password='dkagh1gk'")
    except:
     print "not connect"
  
    logger = logging.getLogger('mylogger')
    fomatter = logging.Formatter('')

    filedate = datetime.datetime.now()
    fileHandler = logging.FileHandler('./myLog_%s.log'%(filedate.strftime("%Y%m%d")))
    streamHandler = logging.StreamHandler()

    fileHandler.setFormatter(fomatter)
    streamHandler.setFormatter(fomatter)

    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)

    logger.setLevel(logging.DEBUG)

    #while(daemon_flag):
    emailtext = '%s\n %s'%(emailtext,getTopRank(logger))
    #    time.sleep(reflash_time)

    #conn.commit()
    #cur.close()
    conn.close()

    #print emailtext

if __name__ == '__main__' :
    Daemon()
