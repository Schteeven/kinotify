from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

# TODO: write your letterboxd credentials here
username = ""
password = ""

#
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


def newest(path):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    return max(paths, key=os.path.getctime)


get_lb_watchlist(username, password)

file = newest(os.getcwd() + "/watchlist")
print(file)

# throwaway csfd credentials in order to use english language
username = 'throwaway666'
password = "7@L9*96HBx%u#I49"

time.sleep(10)
