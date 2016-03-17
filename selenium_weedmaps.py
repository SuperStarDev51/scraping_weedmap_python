import argparse
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import time
import sys
import os
import json
import unicodedata
import codecs
from geopy.geocoders import Nominatim
from pyzipcode import ZipCodeDatabase
from operator import itemgetter

driverpath = ""
chrome_options = Options()
dispensaries_site_url = ""

def init():
    global driverpath, chrome_options, dispensaries_site_url

    driverpath = "C:\Soccer_betting\chromedriver.exe"
    chrome_options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe'

    chrome_options.add_argument('headless')
    chrome_options.add_experimental_option("excludeSwitches", ['enable-logging']);
    chrome_options.add_argument('ignore-certificate-errors')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument("--disable-extensions")
    chrome_options.page_load_strategy = 'eager'
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    dispensaries_site_url = "https://weedmaps.com/dispensaries/in/united-states/"

def get_dispensary_list(location):
    global driverpath, chrome_options, dispensaries_site_url
    url_location = location.lower()
    url_locaton = url_location.replace(' ', '-')
    driver = webdriver.Chrome(driverpath, options=chrome_options)

    city = location.split('/')[1]
    zcdb = ZipCodeDatabase()
    zip_list = zcdb.find_zip(city=city)
    if len(zip_list):
        zip_code = zip_list[0].zip
    else:
        print("  Can't find zip code of given city!")
        zip_code = ""

    print(f"---------------- {location} -  start --------------------------------")
    dispensary_list = []
    
    page_index = 1
    while(1):
        page_url = dispensaries_site_url + url_location + "?page="+ str(page_index)
        driver.get(page_url)
        time.sleep(1)
        containers = driver.find_elements_by_class_name('map-listings-list__ListWrapper-sc-1ynfzzj-0')
        if containers:
            drawer = containers[0]
            
            data_lists = drawer.find_elements_by_class_name('styled-components__Main-sc-1e5myvf-6')
            
            
            if data_lists:
                
                for every_data in data_lists:
                    title = rating = helper = ""
                    title_element = every_data.find_element_by_class_name("base-card__Title-sc-1fhygl1-4")
                    try :
                        rating_element = every_data.find_element_by_class_name("rating__RatingValue-sc-12pds58-1")
                        couting_element = every_data.find_element_by_class_name("rating__Count-sc-12pds58-2")
                    except :
                        rating_element = []
                    helper_element = every_data.find_element_by_class_name("base-card__Helper-sc-1fhygl1-5")
                    if(title_element):
                        title = title_element.text
                    if(rating_element):
                        rating = rating_element.text + couting_element.text
                    if(helper_element):
                        helper = helper_element.text

                    if (title != ""):
                        data_json = { "title" : title, "rating": rating, "helper" : helper , "location": location, "zip code": zip_code }
                        dispensary_list.append(data_json)
                        print("     ",data_json)

            page_index += 1           
        else:
            print("  Sorry, can't find list in this URL ", page_url)

            break

    newlist = sorted(dispensary_list, key=itemgetter('title'))
    print(f"---------------- {location} -  End--------------------------------")
    return newlist

def get_all_brands():
    global driverpath, chrome_options
    basic_url = "https://weedmaps.com/brands/all"
    page_index = 1
    driver = webdriver.Chrome(driverpath,options=chrome_options)
    json_list = []
    print("---------------- Starting scraping brands  --------------------------------")
    while (1):
        
        driver.get(basic_url + '?page=' + str(page_index))
        time.sleep(1)
        container = driver.find_element_by_tag_name('ul')
        
        elements_list = container.find_elements_by_tag_name('li')
        
        if len(elements_list):
            for element in elements_list:
                brand_title = element.text
                
                data_json = {'title': brand_title}
                print("    ",data_json)
                json_list.append(data_json)
            page_index += 1

        else:
            print("  Can't find brands in this url", basic_url + '?page=' + str(page_index))
            break
    print("---------------- END scraping brands  --------------------------------")
    return json_list

def main():
    init()
    cwd = os.getcwd()
    
    arg_list = sys.argv
    if len(arg_list) < 2:
        print("  You have not entered location. will set the default location as 'washington/cathlamet' ")
        location = "washington/cathlamet"
    else:
        location = arg_list[1]

    ############## scraping dispensary ##################################
    dispensary = get_dispensary_list(location)
    str_dispensary = "["
    str_dispensary += ','.join(json.dumps(e,indent=4, ensure_ascii=False) for e in dispensary)
    str_dispensary +="]"
    saving_file_name = location.replace('/','_')

    with open(cwd +'/dispensary_'+ saving_file_name +'.json', 'a') as f:
        f.write(str_dispensary)
    f.close()

    print("  Dispensary Json file has been created!");

    ############## scraping brands  ##################################
    brands = get_all_brands()
    str_brands = '['
    str_brands += ','.join(json.dumps(e,indent=4, ensure_ascii=False) for e in brands)
    str_brands == ']'
    with open(cwd +'/brands.json', 'w', encoding='utf-8') as f:
        f.write(str_brands)
    f.close()
    print("  Brands json file has been created !")

if __name__ == "__main__":
    main()