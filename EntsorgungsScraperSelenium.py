# -*- coding: utf-8 -*-

from lxml import html
import requests
import json
import datetime
import time
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import os
import sys

print "Script started..."

url = 'https://potsdam.abfuhrkalender.de/default.aspx'
months_btn_ids = ['btMCMonth1', 'btMCMonth2', 'btMCMonth3', 'btMCMonth4', 'btMCMonth5', 'btMCMonth6', 'btMCMonth7', 'btMCMonth8', 'btMCMonth9', 'btMCMonth10', 'btMCMonth11', 'btMCMonth12']

PATH = "/Users/max/Developer/Abfallentsorgung/www_revamped/scraped_streets/"

XPATH_SELECTORS = [
    '//*[@id="pnlMonthCalendarDays"]/div[@class="RowStandard"]',
    '//*[@id="pnlMonthCalendarDays"]/div[@class="RowStandard Postponed"]',
    '//*[@id="pnlMonthCalendarDays"]/div[@class="RowStandard Holiday"]'
]


start_index = 0
amount_streets = 1042
time_to_wait = 1

current_year = datetime.datetime.now().year

def scrape(start_index, last_index):
    try:
        global driver
        #options = webdriver.FirefoxProfile()
        os.environ['MOZ_HEADLESS'] = '1'
        binary = FirefoxBinary('/Applications/Firefox Beta.app/Contents/MacOS/firefox', log_file=sys.stdout)
        binary.add_command_line_options('-headless')
        driver = webdriver.Firefox(firefox_binary=binary)
        #driver.set_window_size(640, 480)

        #options = webdriver.ChromeOptions()
        #options.add_argument('headless')
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument("--test-type")
        #options.add_argument('window-size=1200x600')
        #options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        #driver = webdriver.Chrome(chrome_options=options)

        print "Start scraping with street_index " + str(start_index) + ", stop at index " + str(last_index) + " (inclusive)"

        disposals_all = []

        start_index = int(start_index)
        last_index = int(last_index) + 1

        street_index_pointer = -1
        for street_index in range(start_index, last_index):
            street_index_pointer = street_index

            driver.get(url)
            assert "Abfuhrkalender der Landeshauptstadt Potsdam" in driver.title

            # Change Ortsteil
            element = driver.find_element_by_xpath('//*[@id="ddOrtsteil"]')
            options = element.find_elements_by_tag_name('option')

            for option in options:
                if option.get_attribute('value') == '-1':
                    option.click()
                    break

            # Wait until drop down is enabled
            wait = WebDriverWait(driver, 10)
            element = wait.until(EC.element_to_be_clickable((By.ID,'ddStrasse')))
            option = element.find_element_by_xpath('//*[@id="ddStrasse"]/option[@value="'+ str(street_index) +'"]')
            street_name = option.text
            option.click()
            #amount_streets = len(options) - 1 # minus 1 because one empty option inside the select
            #print str(amount_streets) + " Streets"

            disposals = {}
            disposals[street_name]= {}

            #
            #   Loop through months of <STREET>
            #
            start = time.time()
            print street_name + ":"
            for month_id in range(1, 13):
                month = "btMCMonth" + str(month_id)

                disposals[street_name][month] = {}

                wait = WebDriverWait(driver, 10)
                element = wait.until(EC.element_to_be_clickable((By.ID, month)))
                element.click()

                print "\t...scraping " + month

                # waiting()

                arr = []
                for index, xpath_selector in enumerate(XPATH_SELECTORS):
                    rows = driver.find_elements_by_xpath(xpath_selector)

                    for row in rows:
                        wd = row.find_element_by_class_name('Date1').text.encode('utf-8').strip()
                        date = row.find_element_by_class_name('Date2').text.encode('utf-8').strip()

                        if index == 0:      # Default
                            descr = row.find_element_by_class_name('SymbolDescription').text.encode('utf-8').strip()
                            type = "default"

                        elif index == 1:    # Postponed
                            descr = row.find_element_by_class_name('SymbolDescription').text.encode('utf-8').strip()
                            type = "postponed"

                        elif index == 2:    # Holiday
                            descr = row.find_element_by_class_name('ColumnHoliday1').text.encode('utf-8').strip()
                            type = "holiday"


                        if descr != '':
                            year = current_year+1 if month_id < datetime.datetime.now().month else current_year

                            dic = {
                                "date": str(datetime.date(year, month_id, int(date))),
                                "wd": wd,
                                "descr": descr,
                                "type": type
                            }

                            arr.append(dic)

                disposals[street_name][month] = arr
                end = time.time()

            measured_time = (end - start)
            print "Finished in " +  street_name + " (" + str(street_index) + ") in " + str(measured_time) + "s"

            # Put into all disposals array
            disposals_all.append(disposals)

            # Write to single street file
            with open(PATH + str(street_index) + " " + street_name +'.txt', 'w') as outfile:
                json.dump(disposals, outfile)

            # Choose a new street
            driver.get(url)

        # Close session
        driver.close()
        driver.quit()

        # Write to summary file
        #with open(PATH + 'entsorgungstermine.txt', 'w') as outfile:
        #    json.dump(disposals_all, outfile)
    except StaleElementReferenceException:
        print "StaleElementReferenceException... start over with index " + str(street_index_pointer) + " as start_index and " + str(last_index) + " as last_index"
        scrape(street_index_pointer, last_index)


def waiting():
    time.sleep(time_to_wait)
    driver.implicitly_wait(time_to_wait)  # seconds


if __name__ == '__main__':
    if len(sys.argv) > 1:
        scrape(sys.argv[1], sys.argv[2])
    else:
        scrape(1, 10)




