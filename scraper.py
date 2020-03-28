import os
import numpy as np
import pandas as pd
import time
import re
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

webdriver = 'chromedriver_win32/chromedriver.exe' # Change path
driver = Chrome(webdriver)

driver = Chrome(webdriver)#, options=chrome_options)
url = "https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/kernels"
driver.get(url)

actions = ActionChains(driver)
driver.find_element_by_class_name("dataset-header-v2__title").click()
while (driver.find_element_by_class_name("smart-list__message").text != 'No more notebooks to show'):
    actions.key_down(Keys.PAGE_DOWN).perform()

items = driver.find_elements_by_xpath('//*[@id="site-content"]/div[2]/div[2]/div/div/div/div[1]/div[2]/div[2]/div/div/div/div')

metadata = {'votes': [], 'user_link': [], 'tier': [], 'notebook_name': [], 
            'num_visualizations': [], 'num_datafiles': [], 'time_published': [], 
            'relative_time_published': [], 'tags': [], 'language': [], 
            'num_comments': [], 'notebook_link': []}

for i, each in enumerate(items):
    if (i%50==0):
        print(i)
    metadata['votes'].append(int(each.find_element_by_class_name("vote-button__vote-count").text))
    metadata['user_link'].append(each.find_element_by_class_name('avatar').get_attribute("href"))
    metadata['tier'].append(each.find_element_by_class_name('avatar__tier').get_attribute('alt').split(' ')[0])
    metadata['notebook_name'].append(each.find_element_by_class_name('kernel-list-item__name').text)
    tooltip = each.find_element_by_class_name('kernel-list-item__info-blocks')\
              .find_element_by_xpath('.//span[1]').get_attribute('data-tooltip')[:-1].split(' ')
    if ('visualizations' in tooltip) or ('visualization' in tooltip):
        for i, v in enumerate(tooltip):
            if ((v == 'visualizations' or v == 'visualization') and (tooltip[i-1].isdigit())):
                metadata['num_visualizations'].append(int(tooltip[i-1]))
            elif ((v == 'visualizations' or v == 'visualization') and (not tooltip[i-1].isdigit())):
                metadata['num_visualizations'].append(0)
    else:
        metadata['num_visualizations'].append(0)
    if ('data' in tooltip):
        for i, v in enumerate(tooltip):            
            if ((v == 'data') and (tooltip[i-1].isdigit())):
                metadata['num_datafiles'].append(int(tooltip[i-1]))
            elif ((v == 'data') and (not tooltip[i-1].isdigit())):
                metadata['num_datafiles'].append(0)
    else:
        metadata['num_datafiles'].append(0)
    metadata['time_published'].append(each.find_element_by_class_name('kernel-list-item__details').\
                                          find_element_by_xpath('.//*[@title]').get_attribute('title'))
    metadata['relative_time_published'].append(each.find_element_by_class_name('kernel-list-item__details').\
                                              find_element_by_xpath('.//*[@title]').text)
    metadata['tags'].append([each.text for each in\
                             each.find_elements_by_class_name('Tag_TextAnchor-sc-hezo17')\
                             if each.text != ''])
    metadata['language'].append(each.find_element_by_class_name('kernel-list-item__info-blocks')\
                  .find_element_by_xpath('.//span[2]').get_attribute("data-tooltip").split(' ')[-1:][0])
    metadata['num_comments'].append(re.sub('\D', '', each.find_element_by_class_name('kernel-list-item__info-blocks')\
                  .find_element_by_xpath('.//span[3]').get_attribute("data-tooltip")))
    metadata['notebook_link'].append(each.find_element_by_xpath('.//a').get_attribute('href'))

meta_df = pd.DataFrame.from_dict(metadata)
meta_df.to_csv("covid-kernels.csv", index = False)