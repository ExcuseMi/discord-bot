import re
import requests
import time
import json
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import urllib.parse
import traceback

options = webdriver.ChromeOptions()
options.add_argument("--mute-audio")

options.add_argument("--headless")
#driver = webdriver.Chrome(options=options)

def getAllStats(users):
    driver = webdriver.Chrome(options=options)
    map = {}

    for user in users:
        try:
            map[user] = getStats(user, driver)
        except:
            traceback.print_exc()
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    traceback.print_exc()

    return map


def getStats(username, driver):
    url = 'https://api.tracker.gg/api/v2/rocket-league/standard/profile/epic/' + urllib.parse.quote(username)
    driver.get(url)
    driver.implicitly_wait(5)
    content = driver.find_element(By.TAG_NAME, "body").text
    data = json.loads(content)
    if data:
        ranksToRecord = ['Ranked Duel 1v1','Ranked Doubles 2v2','Ranked Standard 3v3','Tournament Matches','Hoops','Snowday']
        userRanks = {}
        for segment in data.get('data').get('segments'):
            if segment.get('type') == 'playlist':
                for rank in ranksToRecord:
                    userRank = getRank(segment, rank)
                    if userRank != None:
                        userRanks[rank] = userRank
    return userRanks

def getRank(segment, name):
    if segment.get('metadata').get('name') == name:
        name = segment.get('stats').get('tier').get('metadata').get('name')
        division = segment.get('stats').get('division').get('metadata').get('name')
        mmr = segment.get('stats').get('rating').get('value')
        return { 'name': name, 'division': division, 'mmr': mmr}
    return None

