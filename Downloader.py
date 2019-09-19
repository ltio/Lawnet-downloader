'''
Created on Sep 5, 2019

@author: Jack
'''

import os, re, time, string, shutil, pyautogui
from distutils.dir_util import copy_tree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def main():
    
    # Read caselist.txt from Download Folder
    search_array = read_caselist()
    
    # Find missing cases
    missing_cases = check_missing(search_array)
    
    username = input("Please enter username: ")
    password = input("Please enter password: ")
    
    # Set driver here so lesser implications
    driver = get_browser()
    
    # Open Lawnet 
    driver.get('https://www.lawnet.sg/lawnet/web/lawnet/home')
    
    # Download missing cases
    download_case(driver, missing_cases, username, password)
    
    driver.find_element_by_id('logoutlink').click()
    time.sleep(3)
    
    # Copy paste required cases into temp file
    move_case(search_array)
    
    # End of main method
    
def read_caselist():
    
    search_array = []
    
    try:
        path_to_casefile = os.path.expanduser('~\Downloads') + '\caselist.txt'
        
        print (path_to_casefile)
        
        f = open(path_to_casefile, 'r')
        
        for line in f:
            
            if re.match('\[', line):
                line = line[1:]
            if line.endswith(']'):
                line = line[:-1]
             
            line = line.replace('\'', '')
            line = line.replace(',', '')
            line = line.rstrip()
            search_array.append(line)
    except:
        print ('File not found')
    finally:
        f.close()
    
    return search_array
    
def move_case(checklist):
    
    # Self-note: Code isn't the most efficient since it reuses code from check_missing(checklist)
    # To be edited in future ver.
    
    case_dict = {}
    keys = string.ascii_uppercase[:len(checklist)]
    key_position = 0
    
    try:
        # Create a file on Desktop
        desktop_path = os.path.expanduser('~\Desktop')
        os.mkdir(desktop_path + '\\temp')
        temp_path = os.path.expanduser('~\\Desktop\\temp')
        
        # Find all the files is current list
        path_to_files = os.path.expanduser('~\\Downloads')
        current_list = os.listdir(path_to_files)
        
        for each_case in checklist:
            bracket_position = each_case.find('[')
            case_id = each_case[bracket_position:]
            for file in current_list:
                if (case_id in file):
                    # s = (path_to_files + '\\' + file)
                    
                    try:
                        # Add to dictionary only if it is a file and not a folder
                        case_dict[keys[key_position]] = file
                        key_position += 1
                        shutil.copy((path_to_files + '\\' + file), temp_path)
                    except:
                        os.mkdir(desktop_path + '\\temp\\' + file)
                        copy_tree((path_to_files + '\\' + file), (temp_path + '\\' + file))
                    
    except:
        # If folder exist, ask user delete/rename
        print ('Folder already exist, please ensure folder is deleted/renamed')
    finally:
        print ('Temp contains: ')
        for k in case_dict:
            print (k, ': ', case_dict[k])    
    
def download_case(driver, missing_cases, username, password):
    
    missing_array = []
    
    try:
        # Enter username & password
        driver.find_element_by_id('_58_login').send_keys(username)
        driver.find_element_by_id('_58_password').send_keys(password)
        driver.find_element_by_name('login').send_keys(Keys.ENTER)
        
        # Main window, first tab
        winHandleBefore = driver.window_handles[0]
        
        for case in missing_cases:
            
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
                    
                    # Citation
                    citation_element = driver.find_element_by_xpath('//div[@class=\'titleCitation\']')
                    citation = citation_element.get_attribute('innerHTML')
                    
                    # Switch to pop-up window
                    driver.switch_to.window(driver.window_handles[2])
                    
                    # Ctrl S and Save PDF
                    time.sleep(1)
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(1)
                    pyautogui.typewrite(citation)
                    time.sleep(1)
                    pyautogui.press('enter', 1)
                    time.sleep(3)
                    
                    driver.close()
                    time.sleep(2)
                    driver.switch_to.window(driver.window_handles[1])
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
                    
                    # Citation
                    citation_element = driver.find_element_by_xpath('//div[@class=\'titleCitation\']')
                    citation = citation_element.get_attribute('innerHTML')
      
                    # Ctrl S and Save HTML
                    time.sleep(1)
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(1)
                    pyautogui.typewrite(citation)
                    time.sleep(1)
                    pyautogui.press('enter', 1)
                    time.sleep(3)
                    
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
                missing_array.append(case)
                driver.get('https://www.lawnet.sg/lawnet/group/lawnet/legal-research/basic-search')
                continue
        
        # In case of breakdown, the missing_array will display last known missing case as well as end session
        if (case.__len__() >= 1):
            print ("list of missing cases are: ")
            print (missing_array)
    except:
        print  ('Username/Password is invalid, please try again.')
                
def get_browser():
    
    try:
        # Find the path with 'chromedriver'
        path_to_chromedriver = os.path.expanduser('~\Desktop') + '\chromedriver'
        '''
        download_dir = os.path.expanduser('~\Desktop')
    
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', {
            "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}], 
            "download": { "prompt_for_download": False, "default_directory": download_dir }
        })
        '''
        browser = webdriver.Chrome(path_to_chromedriver)
    except:
        print ('Driver not found, please drop chromedriver in Desktop')
    
    return browser

def check_missing(checklist):
    
    try:    
        # Find all the files is current list
        path_to_files = os.path.expanduser('~\Downloads')
        current_list = os.listdir(path_to_files)
        
        # Remove all the extension
        files = [os.path.splitext(x)[0] for x in current_list]
        
        # List to store all the case that have yet to be downloaded
        updated_list = []
    
        # If case does not match file in local, mean you will have to download it
        for each_case in checklist:
            match_status = False
            bracket_position = each_case.find('[')
            case_id = each_case[bracket_position:]
            for file in files:
                if (case_id in file):
                    match_status = True
                    break
            if not (match_status == True):
                updated_list.append(each_case)
    except:
        print ('Download file not found, please check path or contact admin.')    
                
    return updated_list
    
if __name__ == '__main__':
    main()