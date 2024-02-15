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

    # TODO:
    username_text = "s_teek"
    password_text = ""

    username.send_keys(username_text)
    password.send_keys(password_text)

    driver.find_element(By.XPATH, "//input[@value='Sign in']").click()
    cookies = driver.get_cookies()

    watchlist = "https://letterboxd.com/" + username_text + "/watchlist/export"
    driver.get(watchlist)
    for cookie in cookies:
        driver.add_cookie(cookie)
    params = {'behavior': 'allow', "downloadPath" : os.getcwd()}
    driver.execute_cdp_cmd("Page.setDownloadBehavior", params)

    driver.refresh()

    path = "//a[@href='/" + username_text + "/watchlist/export/']"
    driver.find_element(By.XPATH, path).click()


get_lb_watchlist(username, password)
