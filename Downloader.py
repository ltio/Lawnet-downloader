'''
Created on Sep 5, 2019

@author: Jack
'''

import os, time, pyautogui
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

def main():
    # Set driver here so lesser implications
    driver = get_browser()

    # Open Lawnet
    driver.get('https://www.lawnet.sg/lawnet/web/lawnet/home')

    # Enter username & password
    # To be replaced with more secure options
    driver.find_element_by_id('_58_login').send_keys('[username]')
    driver.find_element_by_id('_58_password').send_keys('[password]')
    driver.find_element_by_name('login').send_keys(Keys.ENTER)

    search_array = ['[list of cases seperated by commas]']

    # missing_cases = check_missing(search_array)

    missing_array = []

    # Main window, first tab
    winHandleBefore = driver.window_handles[0]

    for case in search_array:

        try:
        # Search
            driver.find_element_by_id('basicSearchKey').send_keys(case)
            driver.find_element_by_class_name('submitBtnHolder2').send_keys(Keys.ENTER)
        except:
            missing_array += case
            driver.get('https://www.lawnet.sg/lawnet/group/lawnet/legal-research/basic-search')
            continue

        # Check if there's any results, if no results return to search
        # Output list of failed and successful downloads
        try:
            links = driver.find_elements_by_class_name('document-title')
            links[0].send_keys(Keys.CONTROL + Keys.RETURN)
            driver.switch_to.window(driver.window_handles[1])
            # If PDF is available
            if((driver.find_elements_by_name("printType")[1].is_enabled())):

                driver.find_element_by_xpath('//*[@title="Download the PDF"]').click()
                time.sleep(2)
                driver.close()
                time.sleep(2)

                driver.switch_to.window(winHandleBefore)
                driver.get('https://www.lawnet.sg/lawnet/group/lawnet/legal-research/basic-search')

            # Else it will be HTML only
            else:

                action = ActionChains(driver)

                print_icon = driver.find_element_by_class_name("iconPrint")
                action.move_to_element(print_icon).perform()
                secondLevelMenu = driver.find_elements_by_name("printType")
                secondLevelMenu[0].click()
                thirdLevelMenu = driver.find_element_by_class_name('submitBtnHolder')
                thirdLevelMenu.click()

                # Switch to pop-up window
                driver.switch_to.window(driver.window_handles[2])

                # Ctrl S and Save HTML
                time.sleep(1)
                page_title = driver.title
                pyautogui.hotkey('ctrl', 's')
                time.sleep(1)
                pyautogui.typewrite(page_title + '.html')
                time.sleep(1)
                pyautogui.press('enter', 1)
                time.sleep(5)

                driver.close()
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[1])
                time.sleep(2)
                driver.close()
                time.sleep(2)
                driver.switch_to.window(winHandleBefore)
                driver.get('https://www.lawnet.sg/lawnet/group/lawnet/legal-research/basic-search')
        # Case is not found
        except:
            missing_array += case
            driver.get('https://www.lawnet.sg/lawnet/group/lawnet/legal-research/basic-search')
            continue

    driver.find_element_by_id('logoutlink').click()
    time.sleep(3)
    # In case of breakdown, the missing_array will display last known missing case as well as end session
    if (case.__len__() >= 1):
        print ("list of missing cases are: ")
        print (missing_array)

def get_browser():

    """Get the browser (a "driver")."""
    # Find the path with 'chromedriver'
    path_to_chromedriver = ('[Path to the chromedriver]')
    download_dir = "[Path to downloads folder]"

    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
        "download": { "prompt_for_download": False, "default_directory": download_dir }
    })

    browser = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
    return browser

# KIV first, to confirm naming convention
def check_missing(checklist):

    # Find all the files is current list
    current_list = os.listdir('[Path to downloads folder]')

    # Remove all the extension
    files = [os.path.splitext(x)[0] for x in current_list]

    # Compare files with list of case to download
    updated_list = (set(checklist).difference(files))

    return updated_list

if __name__ == '__main__':
    main()
