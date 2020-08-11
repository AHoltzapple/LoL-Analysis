# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 10:50:39 2020

@author: arshl
"""
#Imports
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

#Make functions###############################################
def click_update():
    update = driver.find_element_by_class_name('update-button')
    update.click()
    time.sleep(3)

def scroller():
    while True:
        body = driver.find_element_by_tag_name('body')
        start = driver.execute_script("return window.pageYOffset;")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(3)
        end = driver.execute_script("return window.pageYOffset;")
        if start == end:
            break
        
def match_processor():
    matches = driver.find_elements_by_class_name('large-match-card-pin-container')
    match_list = []
    columns = ['queue','result','duration','champion','spell1','spell2','keystone','rune','kills','deaths','assists','level','csscore','killpct']
    for i, m in enumerate(matches):
        match_html = BeautifulSoup(m.get_attribute('outerHTML'))
        queue = match_html.find('div',attrs={'class':'queue-type'}).text
        result = match_html.find('div',attrs={'class':'victory-status'}).text
        duration = match_html.find('div',attrs={'class':'game-duration'}).text
        champ = re.search('.*\/(.*).png$', match_html.find('div',attrs={'class':'champion-face'}).find('img').get('src')).group(1)
        spell1 = match_html.find('div',attrs={'class':'col-2'}).findChildren()[0].get('alt')
        spell2 = match_html.find('div',attrs={'class':'col-2'}).findChildren()[1].get('alt')
        keystone = match_html.find('div',attrs={'class':'runes'}).findChildren()[1].get('alt')
        rune = match_html.find('div',attrs={'class':'runes'}).findChildren()[3].get('alt')
        kills = match_html.find('div',attrs={'class':'KDA-totals'}).text.split()[0]
        deaths = match_html.find('div',attrs={'class':'KDA-totals'}).text.split()[2]
        assists = match_html.find('div',attrs={'class':'KDA-totals'}).text.split()[4]
        level = match_html.find('div',attrs={'class':'col-5'}).findChildren()[0].text.split()[-1]
        csscore = match_html.find('div',attrs={'class':'col-5'}).findChildren()[1].text.split()[0]
        killpct = match_html.find('div',attrs={'class':'col-5'}).findChildren()[3].text.split()[-1]
        match_list.append([queue,result,duration,champ,spell1,spell2,keystone,rune,kills,deaths,assists,level,csscore,killpct])
    matches_df = pd.DataFrame(match_list, columns = columns)
    return matches_df       

def class_fix(element):
    element = element[0]
    return element

#############################################################

#Set path and activate driver
PATH = "C:\Program Files (x86)\geckodriver.exe"
driver = webdriver.Firefox(executable_path = PATH)

### CHAMPION DATA ###
#
##Get champion level data
#driver.get('https://u.gg/lol/profile/na1/erythro25/champion-stats?queueType=normal_aram')
#time.sleep(5)
###Click the privacy button
#button = driver.find_element_by_css_selector('button')
#button.send_keys(Keys.RETURN)
#time.sleep(1)
#
#click_update()
#
##Find and grab data
#soup = BeautifulSoup(driver.find_element_by_class_name('rt-tbody').get_attribute('outerHTML'))
#rows = soup.find_all('div',attrs={'class':'rt-tr-group','role':'rowgroup'})
#
##Collect data
#data = []
#for game in rows:
#    game = game.find_all('div',attrs={'role':'gridcell'})
#    champ = []
#    for i, s in enumerate(game):
#        if i != 4:
#            champ.append(s.get_text())
#        elif i == 4:
#            kdas = s.find_all('strong')
#            for n in kdas:
#                champ.append(n.get_text())
#    data.append(champ)
#    
#columns = ['rank','champion','games','winrate','kda','kills','deaths','assists','gold','cs','maxkill','maxdeath','avgdmgdealt','avgdmgtaken','doubles','triples','quadras','pentas']
#
###Create DF
#champ_data_df = pd.DataFrame(data, columns = columns)
#
###Clean DF
#champ_data_df = champ_data_df.replace('—', 0)
#replace = {'%':'',',':''}
#champ_data_df[['gold','avgdmgdealt','avgdmgtaken','winrate']] = champ_data_df[['gold','avgdmgdealt','avgdmgtaken','winrate']].replace(replace, regex=True)
#champ_data_df[['rank','games','winrate','kda','kills','deaths','assists','gold','cs','maxkill','maxdeath','avgdmgdealt','avgdmgtaken','doubles','triples','quadras','pentas']] = champ_data_df[['rank','games','winrate','kda','kills','deaths','assists','gold','cs','maxkill','maxdeath','avgdmgdealt','avgdmgtaken','doubles','triples','quadras','pentas']].apply(pd.to_numeric)


### CHAMPION ROLE DATA ###

driver.get('https://lol.gamepedia.com/Portal:Champions/List')
soup = BeautifulSoup(driver.find_element_by_css_selector('table').get_attribute('innerHTML')).html
soup_string = str(soup)
classes_df = pd.read_html(soup_string)[0]

classes_df = classes_df[['Champion','Attributes']]

classes_df['Attributes'] = classes_df['Attributes'].str.split()
classes_df['Attributes'] = classes_df['Attributes'].apply(class_fix)

symbols = {" ":'',"'":''}

classes_df['Champion'] = classes_df['Champion'].replace(symbols, regex=True).str.upper()

classes_df = classes_df.rename(columns = {'Champion':'champion','Attributes':'class'})

### MATCH DATA ###

#First page (season 10)
driver.get('https://u.gg/lol/profile/na1/erythro25/overview')
time.sleep(5)
##Privacy and boost sign up windows
try:
    button = driver.find_element_by_css_selector('button')
    button.send_keys(Keys.RETURN)
    time.sleep(3)
except: pass
try:
    button2 = driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div[3]/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[3]/div[2]')
    button2.click()
    time.sleep(3)
except: pass

##Update
click_update()

#Find matches
scroller()

#Grab matches
matches_df1 = match_processor()


#####################################

driver.get('https://u.gg/lol/profile/na1/erythro25/overview?season=13')
time.sleep(5)

click_update()

scroller()

matches_df2 = match_processor()

##################################

driver.get('https://u.gg/lol/profile/na1/erythro25/overview?season=12')
time.sleep(5)

click_update()

scroller()

matches_df3 = match_processor()

#################################
driver.close()

matches_df = pd.concat([matches_df1,matches_df2,matches_df3])

#################################

matches_df['champion'] = matches_df['champion'].str.upper()

merged_df = pd.merge(matches_df, classes_df, how='left', on='champion')

merged_df.to_csv('C:\\Users\\arshl\\Dropbox\\github\\UGG LoL\\merged_df.csv', index_label='matchnum')

#
#matches_df['killpct'] = matches_df['killpct'].str.replace('%','')
#matches_df[['kills','deaths','assists','level','csscore','killpct']] = matches_df[['kills','deaths','assists','level','csscore','killpct']].apply(pd.to_numeric)
#matches_df['duration'] = pd.to_datetime(matches_df['duration'],format='%M:%S').dt.time



