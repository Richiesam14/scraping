#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Code credit:
https://towardsdatascience.com/image-scraping-with-python-a96feda8af2d
Also thanks for Debjyoti Paul (my friend and data scientist at Amazon) for help with this
"""

import time
import requests 
import io
import hashlib
import os
from selenium import webdriver

from selenium.webdriver.common.keys import Keys


def fetch_image_urls_util(url,driver_path):
    images = []
    # Open main window with URL A
    with webdriver.Chrome(executable_path=driver_path) as wd:

        # Switch to the new window and open URL B
        try:
            wd.get(url)
        except:
            return []

        thumbnail_results = wd.find_elements_by_css_selector("img[class ='irc_mi']")

        for img in thumbnail_results:
            if img.get_attribute('src') and 'http' in img.get_attribute('src'):
                images.append(img.get_attribute('src'))

    return images


def fetch_image_urls(query:str, max_links_to_fetch:int, wd, sleep_between_interactions:int=1,driver_path= None, target_path = None, search_term = None):
    
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))
    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)    
    
    # build the google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

    # load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    image_count2 = 0
    results_start = 0
    i = 0
    d = {}
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # get all image thumbnail results
        thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
        number_results = len(thumbnail_results)
        
        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")
        
        for img in thumbnail_results[50:number_results]:
            # try to click every thumbnail such that we can get the real image behind it
            try:
                img.click()
                time.sleep(sleep_between_interactions)
            except Exception as e:
                print(e)
                continue
            
            links = wd.find_elements_by_css_selector("a[jsname='sTFXNd']")

            for link in links:
                if link.get_attribute('href') and 'http' in link.get_attribute('href'):
                    if link.get_attribute('href') not in d:
                        d[link.get_attribute('href')] = True
                        getactualurl = fetch_image_urls_util(link.get_attribute('href'),driver_path)
                    for imageurl in getactualurl:
                        if imageurl is not None:
                            #print(imageurl)
                            image_urls.add(imageurl)
            
            image_count2 = len(image_urls)
            print(image_count2)
            if image_count2 >= max_links_to_fetch/10:
                print(f"Found: {len(image_urls)} image links, saving!")
                try:    
                    for elem in image_urls:
                        persist_image(target_folder,elem)
                except Exception as e:
                    print(e)
                image_urls = set()
                d = {}

            image_count += image_count2
                
        #image_count = len(image_urls)

        if len(image_urls) >= max_links_to_fetch:
            print(f"Found: {len(image_urls)} image links, done!")
            break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(30)
            return
            load_more_button = wd.find_element_by_css_selector(".mye4qd")
            if load_more_button:
                wd.execute_script("document.querySelector('.mye4qd').click();")

        # move the result startpoint further down
        results_start = image_count

    print(len(image_urls))
    return image_urls



def persist_image(folder_path:str,url:str):
    try:
        image_content = requests.get(url).content

    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")

    try:
        image_file = io.BytesIO(image_content)
        image = Image.open(image_file).convert('RGB')
        file_path = os.path.join(folder_path,hashlib.sha1(image_content).hexdigest()[:10] + '.jpg')
        with open(file_path, 'wb') as f:
            image.save(f, "JPEG", quality=85)
        print(f"SUCCESS - saved {url} - as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")
        
  
    
def search_and_download(search_term:str,driver_path:str,target_path='./datasets',number_images=50):
    target_folder = os.path.join(target_path,'_'.join(search_term.lower().split(' ')))

    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    with webdriver.Chrome(executable_path=driver_path) as wd:
        res = fetch_image_urls(search_term, number_images, wd=wd, sleep_between_interactions=0.5,driver_path= driver_path,target_path= target_path,search_term=search_term)
    try:    
        for elem in res:
            persist_image(target_folder,elem)
    except Exception as e:
        print(e)
        
import time
import requests 
import io
from PIL import Image, ImageDraw
import hashlib
import os
from selenium import webdriver


query = ["Serena Williams"]

for q in query:
    search_and_download(q,"./chromedriver.exe")
    
    
    
    
    
    
    
    
    
    









import requests
import io
import hashlib
import os
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def fetch_image_urls_util(url, driver_path):
    images = []
    # Open new window with URL
    with webdriver.Chrome(executable_path=driver_path) as wd:
        try:
            wd.get(url)
        except:
            return []

        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, "img[class='irc_mi']")

        for img in thumbnail_results:
            if img.get_attribute('src') and 'http' in img.get_attribute('src'):
                images.append(img.get_attribute('src'))

    return images


def fetch_image_urls(query, max_links_to_fetch, wd, sleep_between_interactions=1, driver_path=None, target_path=None,
                     search_term=None):
    target_folder = os.path.join(target_path, '_'.join(search_term.lower().split(' ')))

    def scroll_to_end(wd):
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep_between_interactions)

    # Build the Google query
    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&q={q}"

    # Load the page
    wd.get(search_url.format(q=query))

    image_urls = set()
    image_count = 0
    image_count2 = 0
    results_start = 0
    i = 0
    d = {}
    while image_count < max_links_to_fetch:
        scroll_to_end(wd)

        # Get all image thumbnail results
        thumbnail_results = wd.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
        number_results = len(thumbnail_results)

        print(f"Found: {number_results} search results. Extracting links from {results_start}:{number_results}")

        for img in thumbnail_results[results_start:number_results]:
            # Try to click every thumbnail to get the real image behind it
            try:
                wd.execute_script("arguments[0].click();", img)
                time.sleep(sleep_between_interactions)
            except Exception as e:
                print("Element not interactable. Skipping...")
                continue

            links = wd.find_elements(By.CSS_SELECTOR, "a[jsname='sTFXNd']")

            for link in links:
                if link.get_attribute('href') and 'http' in link.get_attribute('href'):
                    if link.get_attribute('href') not in d:
                        d[link.get_attribute('href')] = True
                        get_actual_url = fetch_image_urls_util(link.get_attribute('href'), driver_path)
                        for image_url in get_actual_url:
                            if image_url is not None:
                                image_urls.add(image_url)

            image_count2 = len(image_urls)
            print(image_count2)
            if image_count2 >= max_links_to_fetch / 10:
                print(f"Found: {len(image_urls)} image links, saving!")
                try:
                    for elem in image_urls:
                        persist_image(target_folder, elem)
                except Exception as e:
                    print(e)
                image_urls = set()
                d = {}

            image_count += image_count2

        if len(image_urls) >= max_links_to_fetch:
            print(f"Found: {len(image_urls)} image links, done!")
            break
        else:
            print("Found:", len(image_urls), "image links, looking for more ...")
            time.sleep(1)
            try:
                load_more_button = wd.find_element(By.CSS_SELECTOR, ".mye4qd")
                if load_more_button:
                    wd.execute_script("document.querySelector('.mye4qd').click();")
            except:
                if i > 5:
                    print("No more images found.")
                    break
                else:
                    print("Error while trying to load more images. Retrying ...")
                    i += 1

        # Move the result startpoint further down
        results_start = len(thumbnail_results)

    if len(image_urls) < max_links_to_fetch:
        print("Unfortunately all", max_links_to_fetch, "could not be downloaded because some images were not downloadable.",
              len(image_urls), "is all we got for this search filter!")

    return d, image_count


def persist_image(folder_path, url):
    try:
        image_content = requests.get(url).content
    except Exception as e:
        print(f"ERROR - Could not download {url} - {e}")
        return

    try:
        image = Image.open(io.BytesIO(image_content)).convert('RGB')
        file_name = hashlib.sha1(image_content).hexdigest()[:10] + '.jpg'
        file_path = os.path.join(folder_path, file_name)
        image.save(file_path)
        print(f"SUCCESS - Saved {url} as {file_path}")
    except Exception as e:
        print(f"ERROR - Could not save {url} - {e}")

    print("Folder path:", folder_path)
    print("URL:", url)
    print("File path:", file_path)


# Main code

query = "Serena Williams"  # Example search query
max_images = 10  # Maximum number of images to download
chrome_driver_path = "C:\\Users\\richardgr\\Documents\\DS\\Untitled Folder 1\\chromedriver.exe"  # Replace with your own ChromeDriver path
output_folder_path = "C:\\Users\\richardgr\\Documents\\DS\\Untitled Folder 1\\datasets"

# Create output folder if it doesn't exist
if not os.path.exists(output_folder_path):
    os.makedirs(output_folder_path)

# Set up Chrome driver options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Uncomment this line if you want to run the Chrome driver in headless mode

# Set up Chrome driver service
driver_service = Service(ChromeDriverManager().install())

# Create Chrome driver instance
driver = webdriver.Chrome(service=driver_service, options=chrome_options, executable_path=chrome_driver_path)

# Fetch image URLs and download images
results, count = fetch_image_urls(query, max_images, driver, driver_path=chrome_driver_path, target_path=output_folder_path,
                                  search_term=query)

# Close Chrome driver
driver.quit()

print("Finished downloading. Total images:", count)
