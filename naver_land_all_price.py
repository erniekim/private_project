import requests as rs
import bs4
import time
import datetime
import logging
import logging.handlers
import psycopg2

def getLandPrice(today, conn, build_id, build_type):
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
        text = ""
        Region = ""
        City = ""
        State = ""
        BuildID = ""
        BuildName = ""
        Date = ""
        BuildSize = ""
        BuildNum = ""
        Floor = ""
        Price = ""
        Description = ""
        #daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&rletNo=111414&hscpTypeCd=B01%3AB02%3AB03&page='+str(page)
        daum_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&tradeTypeCd=A1&rletNo=' + build_id + '&hscpTypeCd=A01&page='+ str(page)
        daum2_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&hscpTypeCd=B01%3AB02%3AB03&rletNo=' + build_id + '&page='+ str(page)

        if build_type == 1:
            response = rs.get(daum_url)
        else:
            response = rs.get(daum2_url)

        html_content = response.text.encode(response.encoding)

        navigator = bs4.BeautifulSoup(html_content, "html.parser")

        #resultList_region_Name = navigator.find_all("input", attrs={"name": "cortarNo"})
        resultList_building_Name = navigator.find("input", attrs={"name": "rletNo"})
        resultList = navigator.find_all("div",class_="inner")
        page_size = len(resultList)
        
        first_link = navigator.find("div", attrs={"id": "loc_view4"})
        resultList_building_realname = None
        if first_link:
            resultList_building_realname = first_link.find("div", class_="selectbox-label")

        second_link = navigator.find("div", attrs={"id": "loc_view2"})
        #resultList_state_name = second_link.find_all("div", class_="selectbox-label")
        resultList_state_name = None
        if second_link:
            resultList_state_name = second_link.find("option", selected = True) 

        third_link = navigator.find("div", attrs={"id": "loc_view1"})
        #resultList_city_name = third_link.find_all("div", class_="selectbox-label")
        resultList_city_name = None
        if third_link:
            resultList_city_name = third_link.find("option", selected = True)    

        forth_link = navigator.find("div", attrs={"id": "loc_view3"})
        #resultList_city_name = third_link.find_all("div", class_="selectbox-label")
        resultList_region_Name = None
        if forth_link:
            resultList_region_Name = forth_link.find("option", selected = True)    
        
        #for index, keword in enumerate(resultList_region_Name) :
        #    Region = '%s\n %s'%(Region,keword.get("value").replace('\n', '').replace('\r', ''))
        if resultList_region_Name:
            Region = resultList_region_Name.get("value")
        
        #for index, keword in enumerate(resultList_building_Name) :
        #    BuildID = '%s\n %s'%(BuildID,keword.get("value").replace('\n', '').replace('\r', ''))
        if resultList_building_Name:
            BuildID = resultList_building_Name.get("value")

        #for index, keword in enumerate(resultList_state_name) :
        #    State = '%s\n %s'%(State,keword.get_text().replace('\n', '').replace('\r', ''))
        if resultList_state_name:
            State = resultList_state_name.get("value")

        #for index, keword in enumerate(resultList_city_name) :
        #    City = '%s\n %s'%(City,keword.get_text().replace('\n', '').replace('\r', ''))
        if resultList_city_name:
            City = resultList_city_name.get("value")

        if resultList_building_realname:
            BuildName = resultList_building_realname.get_text()

        i = 0

        for index, keword in enumerate(resultList) :
            del keword['tabindex']
            #del keword['<span>']
            #del keword['</span>']
            #resultText = '[%2d] %s'%(index+1,keword.get_text().replace('\n', '').replace('\r', '').encode('utf-8'))
            #logger.info(resultText)
            if (i != 0):
                if (i == 2):
                    Date = '%s'%(keword.get_text().replace('\n', '').replace('\r', ''))
                    if Date[0]>='0' and Date[0]<='9':
                        #print Date
                        Date
                    else :
                        #print Date + '\n' + Date[0]
                        Date = ""
                        break
                if (i == 4):
                    BuildSize = '%s'%(keword.get_text().replace('\n', '').replace('\r', ''))
                    if BuildSize[0] ==' ' or BuildSize[0] =='\t':
                        BuildSize = '%s'%(keword.get_text(':', strip=True).replace('\n', '').replace('\r', ''))
                        BuildSizes = BuildSize.split(':')
                        BuildSize = BuildSizes[0]
                    else :
                        i = i - 1
                        BuildSize = ""
                if (i == 5):
                    BuildNum = '%s'%(keword.get_text().replace('\n', '').replace('\r', ''))
                    if BuildNum[0] ==' ' or BuildNum[0] =='\t':
                        i = i - 1
                        BuildNum = ""
                if (i == 6):
                    Floor = '%s'%(keword.get_text().replace('\n', '').replace('\r', ''))
                if (i == 7):
                    Price = '%s'%(keword.get_text(':', strip=True).replace('\n', '').replace('\r', ''))
                    Prices = Price.split(':')
                    Price = Prices[0]
                if (i == 9):
                    Description = '%s'%(keword.get_text().replace('\n', '').replace('\r', ''))
            #print emailtext
            #logger.info(keword)
            i = i + 1
            if i > 9 :
                i = 1
                sql_query = 'INSERT INTO realestateprice (recorddate, date, buildname, buildid, buildnum, floor, price, description, city, state, region, buildsize) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
                cursor.execute(sql_query, (today, Date, BuildName, BuildID, BuildNum, Floor, Price, Description, City, State, Region, BuildSize))
                conn.commit()

        #print text
        #print City
        #print State
        #print Region
        #print BuildName
        #print BuildID
        page = page + 1
    cursor.close()
    #return text

def getTopRank(today, conn):
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
                        detail_apt_id = str(keword_detail.get("value").replace('\n', '').replace('\r', ''))
                        detail_apt_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=A01&tradeTypeCd=A1&hscpTypeCd=A01%3AA03%3AA04&cortarNo=' + detail_apt_id
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
                                getLandPrice(today, conn, keword_apt.get("value"), 1)

                        #text_2nd =
                        #print '%s(%s)'%(keword_detail.get_text().replace('\n', '').replace('\r', ''),keword_detail.get("value").replace('\n', '').replace('\r', ''))
                        detail_apt2_url = 'http://land.naver.com/article/articleList.nhn?rletTypeCd=B01&tradeTypeCd=A1&rletNo=&cortarNo=' + detail_apt_id + '&hscpTypeCd=B01'
                        #print detail_apt_url
                        response_apt = rs.get(detail_apt2_url)
                        html_content_apt = response_apt.text.encode(response_apt.encoding)
                        navigator_apt = bs4.BeautifulSoup(html_content_apt, "html.parser")
                        
                        third_link = navigator_apt.find("div", attrs={"id": "loc_view4"})
                        #print third_link
                        resultList_3rd = third_link.find_all("option")
                        for index_apt, keword_apt in enumerate(resultList_3rd) :
                            if keword_apt.get("value") != "_" :
                                #text_2nd =
                                if keword_apt.get("value").replace('\n', '').replace('\r', '') != "none" :
                                    #print '%s(%s)'%(keword_apt.get_text().replace('\n', '').replace('\r', ''),keword_apt.get("value").replace('\n', '').replace('\r', ''))
                                    getLandPrice(today, conn, keword_apt.get("value"), 2)
            time.sleep(1)

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

    now = datetime.datetime.now()
    today = '%s'%(now.strftime("%Y.%m.%d"))

    getTopRank(today, conn)

    conn.close()

    #print emailtext

if __name__ == '__main__' :
    Daemon()
