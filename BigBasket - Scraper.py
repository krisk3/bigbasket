from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import json
import re
import undetected_chromedriver as uc
import pandas as pd
from time import sleep

driver = webdriver.Chrome(ChromeDriverManager().install())
driver.maximize_window()
driver.get('https://www.bigbasket.com/')
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul#navBarMegaNav>li>a")))
all_cat = driver.find_elements(By.CSS_SELECTOR,'ul#navBarMegaNav>li>a')
cat_links = []
for cat in all_cat[0:5]:
    cat_links.append(cat.get_attribute('href'))
data = []
for cat_link in cat_links:
    driver.get(cat_link)
    sleep(5)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-xs-12.checkbox.subcat.ng-scope >a")))
    except:
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-xs-12.checkbox.subcat.ng-scope >a")))
    subcat = driver.find_element(By.CSS_SELECTOR,'div.col-xs-12.checkbox.subcat.ng-scope >a').get_attribute('href')
    sleep(5)
    driver.get(subcat)
    sleep(5)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-xs-12.checkbox.subcat2.ng-scope>a")))
    except:
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-xs-12.checkbox.subcat2.ng-scope>a")))
    under_sub = driver.find_element(By.CSS_SELECTOR,'div.col-xs-12.checkbox.subcat2.ng-scope>a').get_attribute('href')
    driver.get(under_sub)
    sleep(5)
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.prod-view >a")))
    except:
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.prod-view >a")))
    products_elements = driver.find_elements(By.CSS_SELECTOR,'div.prod-view >a')
    p_links = []
    for product in products_elements[0:10]:
        p_links.append(product.get_attribute('href'))
    for link in p_links:
        driver.get(link)
        data_dict = {}
        sleep(5)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.Ayn30")))
        data_dict['City'] = driver.find_element(By.CSS_SELECTOR,'span.Ayn30').text.split(',')[0]
        bread_ele = driver.find_element(By.CSS_SELECTOR,'div._3moNK')
        bread = driver.execute_script("return arguments[0].innerText;", bread_ele)
        data_dict['Super Category'] = bread.split('>')[1]
        data_dict['Category'] = bread.split('>')[2]
        data_dict['Sub Category'] = bread.split('>')[3]
        link_text = link
        data_dict['SKU ID'] = link_text.split('pd')[1].split('/')[1]
        data_dict['Link'] = "https://www.bigbasket.com/pd/" + data_dict['SKU ID'] + "/"
        data_dict['Image'] = driver.find_element(By.CSS_SELECTOR,'div._2slLX.pdImageSection__Carousel-sc-j55xs-0.hRXXhZ >div>img').get_attribute('src')
        data_dict['Brand'] = driver.find_element(By.XPATH,'//a[@context="brandlabel"]').text
        data_dict['SKU Name'] = driver.find_element(By.CSS_SELECTOR,'div#title>h1').text.replace(data_dict['Brand'], "").rsplit(',', 1)[0].strip()
        size_text = driver.find_element(By.CSS_SELECTOR,'div#title>h1').text
        last_comma_index = size_text.rfind(",")
        sku_size = size_text[last_comma_index+2:]
        second_space_index = size_text.index(" ", size_text.index(" ") + 1)
        data_dict['SKU Size'] = sku_size[:second_space_index].strip()
        data_dict['Special Price']= driver.find_element(By.XPATH,'//td[@data-qa="productPrice"]').text
        try:
            data_dict['MRP']= driver.find_element(By.CSS_SELECTOR,'td._2ifWF').text
        except:
            data_dict['MRP']= data_dict['Special Price' ]
        #Here we are scraping the first 10 products of each category and they are always active.
        data_dict['Active ?'] = "Yes"
        #Here we are scraping the first 10 products of each category and they are always in stock.
        data_dict['Out of Stock ?'] = "No"
        data.append(data_dict)
df = pd.DataFrame(data)
df.to_csv('BigBasket.xls', index=False)