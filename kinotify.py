from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from csv import reader

# TODO: write your letterboxd credentials here
username = ""
password = ""

def get_lb_watchlist(username_text, password_text):
    driver = webdriver.Chrome()

    driver.get("https://letterboxd.com")
    driver.find_element(By.XPATH, "//button[@aria-label='Consent']").click()
    driver.find_element(By.XPATH, "//a[@href='/sign-in/']").click()


    username = driver.find_element(By.XPATH, "//input[@name='username']")
    password = driver.find_element(By.XPATH, "//input[@name='password']")

    username.send_keys(username_text)
    password.send_keys(password_text)

    driver.find_element(By.XPATH, "//input[@value='Sign in']").click()
    cookies = driver.get_cookies()
    time.sleep(5)


    watchlist = "https://letterboxd.com/" + username_text + "/watchlist"
    
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    
    params = {'behavior': 'allow', "downloadPath" : os.getcwd() + "/watchlist", }
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

    driver.get(watchlist + "/export")
    time.sleep(5)


def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


def format_watchlist(filename):
    
    films_in_watchlist = set()

    with open(filename) as csv_file:
        csv_reader = reader(csv_file)
        for row in csv_reader:
            films_in_watchlist.add((row[1], row[2]))

    return films_in_watchlist


get_lb_watchlist(username, password)
watchlist = format_watchlist(newest(os.getcwd() + "/watchlist"))

    

# throwaway csfd credentials in order to use english language
username = 'throwaway666'
password = "7@L9*96HBx%u#I49"

