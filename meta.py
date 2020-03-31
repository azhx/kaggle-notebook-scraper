import os
import numpy as np
import pandas as pd
import time
import re
import ast
import cssselect
from bs4 import BeautifulSoup as bsoup
from lxml import html
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
chrome_options = Options()
chrome_options.add_argument('log-level=3')
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

def parsevis(tooltip):
    vis = 0
    if ('visualizations' in tooltip) or ('visualization' in tooltip):
        for i, v in enumerate(tooltip):
            if ((v == 'visualizations' or v == 'visualization') and (tooltip[i-1].isdigit())):
                vis = int(tooltip[i-1])
            elif ((v == 'visualizations' or v == 'visualization') and (not tooltip[i-1].isdigit())):
                vis = 0
    else:
        vis = 0
    return vis

def parsedata(tooltip):
    data = 0
    if ('data' in tooltip):
        for i, v in enumerate(tooltip):            
            if ((v == 'data') and (tooltip[i-1].isdigit())):
                data = int(tooltip[i-1])
            elif ((v == 'data') and (not tooltip[i-1].isdigit())):
                data = 0
    else:
        data = 0
    return data

webdriver = 'chromedriver_win32/chromedriver.exe'

driver = Chrome(webdriver)#, options=chrome_options)
url = "https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/kernels"
driver.get(url)
print ('started webdriver, loading elements')

actions = ActionChains(driver)
driver.find_element_by_class_name("dataset-header-v2__title").click()
while (driver.find_element_by_class_name("smart-list__message").text != 'No more notebooks to show'):
    actions.key_down(Keys.PAGE_DOWN).perform()
print('loaded elements, scraping')
    
tree = html.fromstring(driver.page_source)
metadata = {'votes': [], 'user_link': [], 'tier': [], 'notebook_name': [], 
            'num_visualizations': [], 'num_datafiles': [], 'time_published': [], 
            'relative_time_published': [], 'tags': [], 'language': [], 
            'num_comments': [], 'notebook_link': []}


metadata['votes']                   = [each.text for each in tree.xpath("//*[@class='block-link block-link--bordered']/*/*/*/*/*/*/*/*[@class='vote-button__vote-count']")]
metadata['user_link']               = ['https://kaggle.com'+ each.attrib['href'] for each in tree.xpath("//*[@class='block-link block-link--bordered']/*/*/*/*/*/*[@class='avatar']")]
metadata['tier']                    = [each.attrib['alt'].split(' ')[0] for each in tree.xpath("//*[@class='block-link block-link--bordered']/*/*/*/*/*/*/*[@class='avatar__tier']")]
metadata['notebook_name']           = [each.text for each in tree.xpath("//*[@class='block-link block-link--bordered']/*/*/*/*/*/*[@class ='kernel-list-item__name false']")]              
metadata['time_published']          = [each.attrib['title'] for each in tree.xpath("//*[@class='block-link block-link--bordered']/*/*/*/*/*/*[@title and self::span]")]
metadata['relative_time_published'] = [each.text for each in tree.xpath("//*[@class='block-link block-link--bordered']/*/*/*/*/*/*[@title and self::span]")]
metadata['tags']                    = [[each.text for each in block.xpath(".//span/div/div[2]/div/div/span[2]/*/*[self::a]")] for block in tree.xpath("//*[@class='block-link block-link--bordered']")]
metadata['language']                = [each.attrib['data-tooltip'].split(' ')[-1:][0] for each in tree.xpath("//*[@class='block-link block-link--bordered']/span/div/div[2]/div[2]/span[2]")]
metadata['num_comments']            = [re.sub('\D','',each.attrib['data-tooltip']) for each in tree.xpath("//*[@class='block-link block-link--bordered']/span/div/div[2]/div[2]/span[3]")]
metadata['notebook_link']           = ['https://kaggle.com' + each.attrib['href'] for each in tree.xpath("//*[@class='block-link block-link--bordered']/*[self::a]")]
metadata['num_visualizations']      = np.array([parsevis(each.attrib['data-tooltip'][:-1].split(' ')) for each in tree.xpath("//*[@class='block-link block-link--bordered']/span/div/div[2]/div[2]/span[1]")])
metadata['num_datafiles']           = np.array([parsedata(each.attrib['data-tooltip'][:-1].split(' ')) for each in tree.xpath("//*[@class='block-link block-link--bordered']/span/div/div[2]/div[2]/span[1]")])
print('done scraping, writing csv')

driver.quit()

meta_df = pd.DataFrame.from_dict(metadata)
meta_df.to_csv("covid-kernels.csv", index = False)
print('done writing csv')