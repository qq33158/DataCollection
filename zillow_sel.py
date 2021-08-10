import time
import csv
import math
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import pandas as pd
from pymouse import PyMouse

# 爬房價網址
def get_house_links(url, driver, next_page_xpath):
    house_links=[]
    driver.get(url)
    driver.set_window_size(800, 1000)
    time.sleep(3)
    pages = driver.find_element_by_xpath('//*[@id="grid-search-results"]/div[1]/div/span[1]')
    
    if int(pages.text.replace(' results','')) < 40 :
        get_html_text(house_links, next_page_xpath)
           
    elif int(pages.text.replace(' results','')) % 40 == 0:
        pages = math.floor(int(pages.text.replace(' results',''))/40)
        for i in range(pages):
            get_html_text(house_links, next_page_xpath)
             
    else :
        pages = math.floor(int(pages.text.replace(' results',''))/40)
        for i in range(pages+1):
            get_html_text(house_links, next_page_xpath)
    
    return house_links

def get_html_text(house_links, next_page_xpath):
    for j in range(7):
        ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()  
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listings = soup.find_all("a", class_="list-card-link list-card-link-top-margin")
    page_links = [row['href'] for row in listings]
    next_page = driver.find_element_by_xpath(next_page_xpath) 
    driver.execute_script("arguments[0].click();", next_page)
    time.sleep(np.random.lognormal(0,1)*2)
    house_links += page_links
    
    return house_links

# 爬房價資料
def get_house_data(driver,house_links_flat):
    try:
        # 自動登入
        # auto_login(driver,house_links_flat[0])
        
        error_list = []
        house_data = []
        for link in house_links_flat:
            time.sleep(np.random.lognormal(0,1)*1)

            soup = get_html_data(link,driver)

            time.sleep(6)

            houseprice = get_price(soup)

            if type(houseprice) == float:
                error_list += [link]

            sale_date =get_sale_date(soup)
            address = get_address(soup)

            time.sleep(1)
            time.sleep(np.random.lognormal(0,1))

            bd = get_bd(soup)
            ba = get_ba(soup)
            floor_size = get_floor_size(soup)
            housetype = get_type(soup)
            year_built = get_year_built(soup)


            lot_size = get_lot_size(soup)
            hoa = get_hoa(soup)
            walk_score = get_walk_score(soup)
            transit_score = get_transit_score(soup)

            time.sleep(np.random.lognormal(0,1))

            pt = get_pt(soup)
            ta = get_ta(soup)
            school1 = get_school1(soup)
            school2 = get_school2(soup)
            school3 = get_school3(soup)
            mls = get_mls(soup)

            time.sleep(np.random.lognormal(0,1))

            house_data.append([mls, bd, ba, floor_size, address, sale_date, walk_score, transit_score, school1, school2, school3, housetype, year_built, lot_size, pt, ta, hoa, houseprice])        

        if error_list != []:
            save_error_html(error_list)
            
        return house_data
    except:
        print('error')
        if error_list != []:
            save_error_html(error_list)
        return house_data

def get_html_data(url, driver):
    driver.get(url)
    htmlsleep()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

# 抓不到價錢時, 判定發生機器人或者頁面找不到(404), 程式暫停後續抓OR回空值
def get_price(soup):
    try:
        try:
            houseprice = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/p/span[1]/span[2]')
            houseprice = int(houseprice.text.replace(': $','').replace(',',''))
            return houseprice
        except NoSuchElementException:
            try:
                mouseCount = 0
                while driver.find_element_by_xpath('/html/body/main') != None:
                    if mouseCount == 10:
                        print('robot error')
                        htmlsleep()
                        break
                    time.sleep(random.randint(2,4))
                    check_root()
                    mouseCount +=1
            except NoSuchElementException:            
                houseprice = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/p/span[1]/span[2]')
                houseprice = int(houseprice.text.replace(': $','').replace(',',''))
                return houseprice
    except:
        return np.nan
    
def check_root():
    m = PyMouse()
    x= random.randint(500,700)
    y = random.randint(400,450)
    mx = random.randint(0,10)
    my = random.randint(0,10)
    m.press(x,y)
    time.sleep(random.randint(3,5))
    m.release(x+mx, y+my)
    print('check_robot')
    
# 發生機器人時睡一下及開網頁時
def htmlsleep():
    time.sleep(np.random.lognormal(0,1))
    random_time = [4,5,6,7]
    time.sleep(random.choice(random_time))
    
def get_sale_date(soup):
    try:
        sale_date = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/p/span[2]')
        sale_date = sale_date.text.replace('Sold on ','')
        return sale_date
    except:
        return np.nan
    
def get_address(soup):
    try:
        address = driver.find_element_by_xpath('//*[@id="ds-chip-property-address"]')        
        return address.text
    except:
        return np.nan
    
def get_bd(soup):
    try:
        housebedroom = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/span/span[1]/span[1]')
        housebedroom = int(housebedroom.text)
        return housebedroom
    except:
        return np.nan
    
def get_ba(soup):
    try:
        try:
            housebathroom = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/span/button/span/span[1]')
            return float(housebathroom.text)
        except NoSuchElementException:
            housebathroom = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/span/span[3]/span[1]')
            housebathroom = float(housebathroom.text)
            return housebathroom
    except:
        return np.nan

def get_floor_size(soup):
    try:
        try:
            floor_size = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/span/span[4]/span[1]')
            floor_size = int(floor_size.text.replace('sqft','').replace(',',''))
            return floor_size
        except NoSuchElementException:
            floor_size = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]/span/span[5]/span[1]')
            floor_size = int(floor_size.text.replace('sqft','').replace(',',''))
            return floor_size
    except:
        return np.nan

def get_type(soup):
    try:
        try:
            housetype = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[6]/div/div[1]/ul/li[1]/span[2]')
            return housetype.text
        except NoSuchElementException:
            housetype = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div/div[1]/ul/li[1]/span[2]')
            return housetype.text
    except:
        return np.nan

def get_year_built(soup):
    try:
        try:
            year_built = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[6]/div/div[1]/ul/li[2]/span[2]')
            return year_built.text
        except NoSuchElementException:
            year_built = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div/div[1]/ul/li[2]/span[2]')
            return year_built.text
    except:
        return np.nan

def get_lot_size(soup):
    try:         
        try:
            try:
                try:
                    lot = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div/div[1]/ul/li[6]/span[2]')
                    if lot.text[-1] == 's' or lot.text[-1] == 't':
                        return lot.text
                    else:
                        raise NoSuchElementException
                except NoSuchElementException:
                    lot = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div/div[1]/ul/li[7]/span[2]')
                    if lot.text[-1] == 's' or lot.text[-1] == 't':
                        return lot.text
                    else:
                        raise NoSuchElementException
            except NoSuchElementException:
                lot = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[6]/div/div[1]/ul/li[7]/span[2]')
                if lot.text[-1] == 's' or lot.text[-1] == 't':
                    return lot.text
                else:
                    raise NoSuchElementException
        except NoSuchElementException:
            lot = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[6]/div/div[1]/ul/li[6]/span[2]')
            if lot.text[-1] == 's' or lot.text[-1] == 't':
                return lot.text
            else:
                raise NoSuchElementException
    except:
        return np.nan

def get_hoa(soup):
    try:
        try:
            try:
                hoa = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div/div[1]/ul/li[6]/span[2]')
                if hoa.text[0] == '$':
                    return hoa.text.replace('$','').replace(' monthly','')
                else:
                    raise NoSuchElementException
            except NoSuchElementException:
                hoa = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[6]/div/div[1]/ul/li[6]/span[2]')            
                if hoa.text[0] == '$':
                    return hoa.text.replace('$','').replace(' monthly','')
                else:
                    raise NoSuchElementException
        except NoSuchElementException:
            hoa = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div/div[1]/ul/li[6]/span[2]')        
            if hoa.text[0] == '$':
                return hoa.text.replace('$','').replace(' monthly','')
            else:
                raise NoSuchElementException
    except:
        return np.nan

def get_walk_score(soup):
    try:
        walk_score = driver.find_element_by_xpath('//*[@id="walk-score-text"]')
        try:
            walk_score = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[8]/div[1]/div[1]/ul/li[1]/a/span')
            return int(walk_score.text)
        except NoSuchElementException:
            walk_score = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[9]/div[1]/div[1]/ul/li[1]/a/span')
            return int(walk_score.text)
    except:
        return np.nan

def get_transit_score(soup):
    try:
        transit_score = driver.find_element_by_xpath('//*[@id="transit-score-text"]')
        try:
            try:
                try:            
                    transit_score = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[9]/div[1]/div[1]/ul/li[2]/a/span')
                    return int(transit_score.text)
                except NoSuchElementException:
                    transit_score = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[8]/div[1]/div[1]/ul/li[2]/a/span')
                    return int(transit_score.text) 
            except NoSuchElementException:
                transit_score = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[9]/div[1]/div[1]/ul/li[1]/a/span')
                return int(transit_score.text)                
        except NoSuchElementException:
            transit_score = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[8]/div[1]/div[1]/ul/li[1]/a/span')
            return int(transit_score.text)
    except:
        return np.nan
    
def get_pt(soup):
    try:
        try: 
            pt = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/span[1]')
            pt = int(pt.text.replace('$','').replace(',',''))
            return pt
        except NoSuchElementException:          
            pt = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[8]/div[1]/div[2]/div/table/tbody/tr[1]/td[2]/span[1]')
            pt = int(pt.text.replace('$','').replace(',',''))
            return pt
    except:
        return np.nan

def get_ta(soup):
    try:
        try:
            ta = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[7]/div[1]/div[2]/div/table/tbody/tr[1]/td[3]/span[1]')
            ta = int(ta.text.replace('$','').replace(',',''))
            return ta
        except NoSuchElementException:
            ta = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[8]/div[1]/div[2]/div/table/tbody/tr[1]/td[3]/span[1]')
            ta = int(ta.text.replace('$','').replace(',',''))
            return ta
    except:
        return np.nan

def get_school1(soup):
    try:
        school1 = driver.find_element_by_xpath('//*[@id="ds-nearby-schools-list"]/li[1]/div[1]/div/span[1]')        
        return school1.text
    except:
        return np.nan

def get_school2(soup):
    try:
        school2 = driver.find_element_by_xpath('//*[@id="ds-nearby-schools-list"]/li[2]/div[1]/div/span[1]')        
        return school2.text
    except:
        return np.nan
    
def get_school3(soup):
    try:
        school3 = driver.find_element_by_xpath('//*[@id="ds-nearby-schools-list"]/li[3]/div[1]/div/span[1]')        
        return school3.text
    except:
        return np.nan

def get_mls(soup):
    try:
        try:
            mls = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[5]/div[1]/div[3]/div[2]')
            mls = mls.text.replace('MLS#:','')
            return mls
        except NoSuchElementException:         
            mls = driver.find_element_by_xpath('//*[@id="home-details-content"]/div/div/div[1]/div[2]/div[2]/div[3]/div/div/div/ul/li/div[6]/div[1]/div[3]/div[2]')
            mls = mls.text.replace('MLS#:','')
            return mls
    except:
        return 0

def save_html(house_links_pages):
    file_name = "house_html%s_%s.csv" % (str(time.strftime("%Y-%m-%d")), str(time.strftime("%H%M%S")))
    columns = ['html']
    pd.DataFrame(house_links_pages, columns = columns).to_csv(file_name, index = False, encoding = "UTF-8")

def save_error_html(error_list):
    file_name = "error_html%s_%s.csv" % (str(time.strftime("%Y-%m-%d")), str(time.strftime("%H%M%S")))
    columns = ['html']
    pd.DataFrame(error_list, columns = columns).to_csv(file_name, index = False, encoding = "UTF-8")

# 自動登錄功能
def auto_login(driver, url):

    driver.get(url)
    time.sleep(2)

    sign_in1 = driver.find_element_by_xpath('//*[@id="page-header-container"]/header/nav/div[1]/ul/li[1]/a/span') 
    driver.execute_script("arguments[0].click();", sign_in1)
    time.sleep(2)

    email = driver.find_element_by_xpath('//*[@id="reg-login-email"]')
    email.send_keys('帳號')
    time.sleep(2)

    password = driver.find_element_by_xpath('//*[@id="inputs-password"]')
    password.send_keys('密碼')
    time.sleep(2)

    button = driver.find_element_by_xpath('//*[@id="login-tab_panel"]/form/div[3]/div/input')
    button.click()
    time.sleep(2)

# 讀取csv檔
file = '***.csv'
with open(file) as csvFile:
    csvReader = csv.reader(csvFile)
    datas = list(csvReader)
house_links_pages = []    
for data in datas[1:]:
    house_links_pages += data
    
# 取得房價資
driver = webdriver.Chrome("./chromedriver")
house_links_flat = get_house_data(driver, house_links_pages)
driver.close()
print('Finish')

file_name = "%s_%s.csv" % (str(time.strftime("%Y-%m-%d")), str(time.strftime("%H%M%S")))
columns = ['mls','housebedroom','housebathroom','sqft','address','soldout','walkscore','transitscore','school1','school2','school3','housetype','houseyear','lot','pt','ta','hoa','houseprice']
pd.DataFrame(house_links_flat, columns = columns).to_csv(file_name, index = False, encoding = "UTF-8")
print('已存檔')

# 取得房價網址
#driver = webdriver.Chrome("./chromedriver")
# 因頁數不一樣需要改下一頁的xpath
#next_page_xpath = '//*[@id="grid-search-results"]/div[2]/nav/ul/li[10]/a'
# 改網頁
#htmls = 'https://www.zillow.com/federal-way-wa-98003/sold/house_type/1-_beds/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%2298003%22%2C%22mapBounds%22%3A%7B%22west%22%3A-122.42200673095704%2C%22east%22%3A-122.20983326904297%2C%22south%22%3A47.26186910664669%2C%22north%22%3A47.35568303676819%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A99491%2C%22regionType%22%3A7%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22ah%22%3A%7B%22value%22%3Atrue%7D%2C%22rs%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%2C%22tow%22%3A%7B%22value%22%3Afalse%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22price%22%3A%7B%22min%22%3A550000%7D%2C%22mp%22%3A%7B%22min%22%3A1772%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D'
#house_links_pages = get_house_links(htmls, driver, next_page_xpath)
#driver.close()
#print('Finish')