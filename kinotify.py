from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
from csv import reader
from html.parser import HTMLParser
from email.message import EmailMessage
import ssl
import smtplib


# TODO: write your email and letterboxd credentials in 
#       os enviroment variables named EMAIL, EMAIL_PASSWORD
#       LETTERBOXD_LOGIN and LETTERBOXD_PASSWORD or hardcode them yourselves

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)


class ScheduleHMTLParser(HTMLParser):
    cinema_name = ""
    current_date = ""
    current_film = ""
    schedule = []
    set_cinema_name = False
    set_date = False
    set_film = False
    set_time = False
    
    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.set_cinema_name = True
        elif tag == "div" and ("class", "box-sub-header") in attrs:
           self.set_date = True
        elif tag == "a" and ("class", "film-title-name") in attrs:
            self.set_film = True
        elif tag == "td" and ("class", "td-time") in attrs:
            self.set_time = True

    def handle_data(self, data):
        if self.set_cinema_name:
            self.cinema_name = data
            self.set_cinema_name = False
        elif self.set_date:
            self.current_date = data.strip()
            self.set_date = False
        elif self.set_film:
            self.current_film = data.strip()
            self.set_film = False
        elif self.set_time:
            self.set_time = False
            self.schedule.append((self.current_date, self.current_film, data.strip()))
         

def get_lb_watchlist(username_text, password_text):
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


def choose_file(path):
    for file in os.listdir(path):
        if file.startswith("watchlist"):
            return file


def format_watchlist(filename):  
    films_in_watchlist = set()

    with open(os.getcwd() + "/watchlist/" + filename) as csv_file:
        csv_reader = reader(csv_file)
        for row in csv_reader:
            films_in_watchlist.add(row[1])

    return films_in_watchlist


def delete_downloaded_files():
    os.system('rm -rf watchlist/*')


def scrape_cinemas():
    # throwaway csfd credentials in order to use english language
    csfd_username = 'throwaway666'
    csfd_password = "7@L9*96HBx%u#I49"

    driver.get("https://www.csfd.cz/prihlaseni/")
    # only use when --headless option removed
    # driver.find_element(By.XPATH, "//button[@id='didomi-notice-agree-button']").click()
    username = driver.find_element(By.XPATH, "//input[@name='username']")
    password = driver.find_element(By.XPATH, "//input[@name='password']")
    username.send_keys(csfd_username)
    password.send_keys(csfd_password)
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@name='send']").click()
    time.sleep(5)
    driver.get("https://www.csfd.cz/kino/?district=55&period=month")
    
    spalicek = get_schedule("//section[@id='cinema-10']")
    cit = get_schedule("//section[@id='cinema-3153']")
    art = get_schedule("//section[@id='cinema-6']")

    return [art, spalicek, cit]

def get_schedule(cinema_elem):
    cinema_html = driver.find_element(By.XPATH, cinema_elem).get_attribute("outerHTML")

    parser = ScheduleHMTLParser()
    parser.feed(cinema_html)    
    cinema_schedule = parser.schedule
    cinema_name = parser.cinema_name
    parser.close()

    return cinema_name, cinema_schedule


def choose_films_to_see(watchlist, in_cinemas):
    to_see_in_cinemas = []

    for cinema, schedule in in_cinemas:
        to_see_in_cinemas.append("\n\n")
        to_see_in_cinemas.append(cinema)
        to_see_in_cinemas.append(":")

        last_date = ""

        for date, name, time in schedule:
            if name in watchlist:
                if date != last_date:
                    last_date = date
                    to_see_in_cinemas.append("\n")
                    to_see_in_cinemas.append(last_date)
                    to_see_in_cinemas.append(":\n")
                to_see_in_cinemas.append("    ")
                to_see_in_cinemas.append(time)
                to_see_in_cinemas.append("  ")
                to_see_in_cinemas.append(name)
                to_see_in_cinemas.append("\n")
    return to_see_in_cinemas


def send_email(email_text):
    sender = os.environ.get("EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    em = EmailMessage()
    em['From'] = sender
    em['To'] = sender
    em['Subject'] = "Your watchlist in cinemas"
    em.set_content(email_text)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, sender, em.as_string())


get_lb_watchlist(os.environ.get("LETTERBOXD_LOGIN"), os.environ.get("LETTERBOXD_PASSWORD"))
watchlist = format_watchlist(choose_file(os.getcwd() + "/watchlist"))
delete_downloaded_files()
in_cinemas = scrape_cinemas()
to_see_in_cinemas = choose_films_to_see(watchlist, in_cinemas)
send_email("".join(to_see_in_cinemas))