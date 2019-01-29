
# coding: utf-8

# In[14]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import datetime 
import pymysql
import re


# In[4]:


def createDB(conn,dbname):
    curs = conn.cursor()
    query = """CREATE DATABASE """+dbname
    try :
        curs.execute(query)
    except :
        print('DB가 이미 존재합니다. DB_NAME : ',dbname)
    
    query = """ALTER DATABASE """+ dbname + """ CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)
    conn.commit()


# In[5]:


def save_DB() : 
    conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
    dbname = 'daum_cafe_'+ keyword
    createDB(conn,dbname)
    curs = conn.cursor()
    curs.execute("""use """+dbname)

    query = """CREATE TABLE IF NOT EXISTS """+ keyword+ """(ID int, URL varchar(200), Title varchar(100), Date varchar(20), Writer varchar(50), cafe_like int, Count int,Text text(62200));"""
    curs.execute(query)

    query = """ALTER TABLE """ + keyword +""" CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)

    conn.commit()
    
    select_query = """SELECT * from """ + keyword 
    index = curs.execute(select_query)

    for value in total_list :
        url = value[0]
        title = value[1]
        date = value[2]
        writer = value[3]
        like = value[4]
        count = value[5]
        content = value[6]

        query = """insert into """ + keyword + """(ID, URL, Title, Date, Writer, cafe_like, Count, Text) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (str(index), url, title, date,writer,like,count,content))

        index = index + 1 

        conn.commit()
        
    conn.close()
    print("FINISH")


# In[21]:


import re

INVISIBLE_ELEMS = ('style', 'script', 'head', 'title')
RE_SPACES = re.compile(r'\s{3,}')

def visible_texts(soup):
    text = ' '.join([
        s for s in soup.strings
        if s.parent.name not in INVISIBLE_ELEMS
    ])

    return RE_SPACES.sub('  ', text)


# In[6]:


keyword = input("Keyword ? ")

start_year = input("Start Year ? ")
start_month = input("Start Month ? ")
start_day = input("Start Day ? ")

end_year = input("End Year ? ")
end_month = input("End Month ? ")
end_day = input("End Day ? ")

start_date = start_year+start_month+start_day
end_date = end_year+end_month+end_day


# In[22]:


dt_start_date = datetime.datetime.strptime(start_date,"%Y%m%d").date()
dt_end_date = datetime.datetime.strptime(end_date,"%Y%m%d").date()
day_1 = datetime.timedelta(days=1)
dt_start_1 = dt_start_date

# 일수를 하루씩 잘라서 반복
while dt_start_1 <= dt_end_date :
    total_list = []
    URL_date_list = []
    page_num = 1
    print(dt_start_1)
    # 페이지 만큼 돌면서 링크 수집
    while True : 
        p_url = 'https://search.daum.net/search?nil_suggest=btn&w=cafe&m=board&lpp=10&DA=STC&q='+keyword+'&sd='+start_date+'000000&ed='+start_date+'235959&period=u&m=board&p='+str(page_num)
        driver = webdriver.Chrome('./chromedriver/chromedriver')
        driver.implicitly_wait(3)
        driver.get(p_url)
        soup = BeautifulSoup(driver.page_source,'html.parser')

        span_tags = soup.findAll("span", {"class" : "f_nb date"})
        a_tags = driver.find_elements_by_xpath("//a[@class='f_link_b']")
        # 한 페이지에 있는 링크들 전부 가져오기
        for a,d in zip(a_tags,span_tags) :
            url = a.get_attribute("href")
            print(url)
            driver = webdriver.Chrome('./chromedriver/chromedriver')
            driver.implicitly_wait(3)
            driver.get(url)
            # 페이지 변환      
            frame = driver.find_element_by_name('down')
            driver.switch_to_frame(frame)

            soup = BeautifulSoup(driver.page_source,'html.parser')
                
            cafe_title = soup.find("div", {"class" : "article_subject"}).find("span", {"class" : "b"}).get_text().strip().encode('cp949','ignore')
            cafe_title = cafe_title.decode('cp949','ignore')
            print(cafe_title)
            cafe_date = d.get_text()
            print(cafe_date)
            try :
                writer = soup.find("a", {"class" : "txt_point p11"}).get_text()
            except :
                writer = 'None'
            print(writer)
            # 공감 버튼이 비어있다면 0으로
            if soup.find("span", {"id" : "recommendCnt"}) is not None :
                cafe_like = soup.find("span", {"id" : "recommendCnt"}).get_text()
            else :
                cafe_like = 0
            print(cafe_like)        
            reply_count = soup.find("span", {"class" : "comment_cnt"}).get_text().strip()[3:]
            print(reply_count) 
            # 이상한 태그 없애기 
            cafe_content = visible_texts(soup.find("table", {"class" : "protectTable"})).strip()
            cafe_content = cafe_content.encode('cp949','ignore')
            cafe_content = cafe_content.decode('cp949','ignore')
            print(cafe_content) 
            total_list.append([url,cafe_title,cafe_date,writer,cafe_like,reply_count,cafe_content])

        driver.get(p_url)

        try :
            driver.find_element_by_xpath("//a[@class='ico_comm1 btn_page btn_next']").click()
            page_num += 1
        except : 
            break;
            
     # 날짜 변환    
    dt_start_1 = dt_start_1 + day_1
    temp = str(dt_start_1)
    start_date = temp[:4]+temp[5:7]+temp[8:]
    
    save_DB()


# In[12]:


#DB삭제시 이용
# query = """DROP DATABASE daum_cafe; """
# curs.execute(query)


# In[1]:


#DB내용 확인시 이용
# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
# curs = conn.cursor()
# curs.execute("use daum_cafe ;")
# query = """select * from ; """
# curs.execute(query)
# all_rows = curs.fetchall()
# for i in all_rows:
#     print(i)

