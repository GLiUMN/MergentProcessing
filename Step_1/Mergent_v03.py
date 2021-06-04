############################################################################################################################################################################
#Mergent_v03.py
#Author: Tobey Kass
#Created on June 7, 2020
#This code is used to programatically download companies' annual reports from ProQuest
#It will require access to credentials that subscribe to ProQuest
#The UMN library system subscribes to the site, so you can use your normal UMN username/password
#Note that I have pauses periodically worked in to try to prevent bot detectors (none of the pauses are longer than 2 minutes)
############################################################################################################################################################################


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import random
import os
# import glob
import pandas as pd
import re



def start_driver(selenium_executablepath,user_agent):
############################################################################################################################################################################
    #The function start_driver initalizes a driver instance and goes to the proquest website.
    #After running this function, you will need to input your UMN username and password to access the proquest website.
    #selenium_executablepath is the path where you are storing chromedriver.exe. It should be given as a string.
    #user_agent is your computer's user agent, which can be found using the website https://www.whatismybrowser.com/detect/what-is-my-user-agent
    #It should be given as a string.
############################################################################################################################################################################
    opts = webdriver.ChromeOptions()
    #Set the user agent
    opts.add_argument("user-agent={:s}".format(user_agent))
    #Set these options to disable PDF viewer - this will download the PDF rather than opening them within the browser
    opts.add_experimental_option('prefs', {"download.prompt_for_download": False,"download.directory_upgrade": True, "plugins.always_open_pdf_externally": True})
    #Create a selenium driver instance using Chrome
    driver = webdriver.Chrome(executable_path=selenium_executablepath,options=opts)
    #Go to proquest's site
    driver.get("https://www-mergentarchives-com.ezp1.lib.umn.edu/search.php")
    return driver

def rename_downloaded_report(year,company,filename,save_foldername,download_foldername):
############################################################################################################################################################################
    #The rename_downloaded_report moves the report we downloaded to the company's subdirectory in the save_foldername directory, and renames it to {company}_{report year}.
    #year is the year of the annual report we just downloaded. It should be given as an integer
    #company is the name of the company we are currently on. It should be given as a string.
    #filename is the default filename of the report we just downloaded, as specified by one of the script tags on the report's page. report_filename should be given
    #as a string.
    #save_foldername is the path to the directory where you want to ultimately save the annual reports. They will be saved in a subdirectory within save_foldername 
    #organized by company name.
    #download_foldername is the path to the default download directory (on windows, this is usually {username}/Downloads). Selenium will temporarily download the reports
    #to this folder, and then my code will move them to the save_foldername directory. download_foldername should be given as a string.
############################################################################################################################################################################
    os.rename("{:s}/{:d}-{:s}_{:s}.PDF".format(download_foldername,year,filename[0:-4],filename),"{:s}/{:d}/{:s}_{:d}.pdf".format(save_foldername,year,company,year))
    return

def get_reports_on_page(driver,year,save_foldername,download_foldername):
############################################################################################################################################################################
    #The function get_reports_on_page downloads the report for each company on the current page. It loops through the companies and gets their company name and report link
    #driver is the selenium driver instance that is returned from the function start_driver
    #year is the year of the reports we are downloading on this page. It should be given as an integer
    #save_foldername is the path to the directory where you want to ultimately save the annual reports. They will be saved in a subdirectory within save_foldername 
    #organized by company name
    #download_foldername is the path to the default download directory (on windows, this is usually {username}/Downloads). Selenium will temporarily download the reports
    #to this folder, and then my code will move them to the save_foldername directory. download_foldername should be given as a string
############################################################################################################################################################################
    #Get the table rows, where each row is for a different company on the page
    tablerow_tags = driver.find_element_by_css_selector("div[class='x-grid-viewport']").find_elements_by_css_selector("tr[class^='x-grid-row']")
    for i in range(len(tablerow_tags)):
        tablerow_tag = tablerow_tags[i]
        #Get the company name
        company = tablerow_tag.find_element_by_css_selector("div[class='x-grid-col-0 x-grid-cell-inner']").text.strip().lower()
        #Clean up the name in case it has a slash or period, which will mess up the filename
        company = re.sub(re.compile("[/.]"),"",company)
        #If we haven't already downloaded the report for this company/year pair, go ahead
        if not os.path.isfile("{:s}/{:d}/{:s}_{:d}.pdf".format(save_foldername,year,company,year)):
            #Make sure that the report we are downloading is a 10-K. Mergent has other SEC forms, but for now we only want the 10-K's
            if tablerow_tag.find_element_by_css_selector("div[class='x-grid-col-4 x-grid-cell-inner']").text.strip().lower()=="10-k":
                #Get the filename, which is in the "onclick" attribute of the PDF link in the tablerow
                filename = tablerow_tag.find_element_by_css_selector("a[onclick^='openWindow']").get_attribute("onclick").split("file=")[1].split(".PDF")[0]
                #Going to the following site will download the PDF to your default Downloads folder (note that the driver instance will remain on the current site)
                driver.get("https://www-mergentarchives-com.ezp1.lib.umn.edu/modules/SECHistorical/viewReportBatch.php?file={:s}.PDF&year={:d}".format(filename,year))
                time.sleep(random.uniform(12.5, 15))
                #Move the downloaded report to the "save_foldername" directory
                rename_downloaded_report(year,company,filename,save_foldername,download_foldername)
        tablerow_tags = driver.find_element_by_css_selector("div[class='x-grid-viewport']").find_elements_by_css_selector("tr[class^='x-grid-row']")
    return driver

def loop_through_pages(driver,year,years_progress_df,years_progress_filename,save_foldername,download_foldername):
############################################################################################################################################################################
    #The function loop_through_pages goes through the different pages for a given year in order to download the reports.
    #driver is the selenium driver instance that is returned from the function start_driver
    #year is the year of the reports we are downloading on this page. It should be given as an integer
    #years_progress_df tracks which years have been completed already (in case we have to restart the download). It should be given as a DataFrame
    #years_progress_filename is the path to the file where we will save the years_progress_df DataFrame
    #save_foldername is the path to the directory where you want to ultimately save the annual reports. They will be saved in a subdirectory within save_foldername 
    #organized by company name
    #download_foldername is the path to the default download directory (on windows, this is usually {username}/Downloads). Selenium will temporarily download the reports
    #to this folder, and then my code will move them to the save_foldername directory. download_foldername should be given as a string
############################################################################################################################################################################
    #Get the index of the year in the years_progress_df
    year_index = years_progress_df[years_progress_df["year"]==year].index[0]
    #Get the number of pages previously done
    pages_done = int(years_progress_df.loc[year_index,"pages_done"])
    #If we have already completed pages for this year, go to the first page where we still need to download reports
    if pages_done > 0:
        page_num_box = driver.find_element_by_css_selector("input[id='ext-gen156']")
        page_num_box.clear()
        page_num_box.send_keys(pages_done+1)
        page_num_box.send_keys(Keys.ENTER)
        
    #Get the total number of pages of reports for this year
    total_pages = int(driver.find_element_by_css_selector("span[id='ext-gen159']").text.strip().split(" ")[-1])
#    total_pages = 5
    for page_num in range(pages_done+1,total_pages+1):
        #Download the reports for this page
        driver = get_reports_on_page(driver,year,save_foldername,download_foldername)
        #Track that we've completed this page
        years_progress_df.at[year_index,"pages_done"] = page_num
        if page_num==total_pages:
            #Track that this year has been completed
            years_progress_df.at[year_index,"year_done"] = "X"
            #Save our progress
            years_progress_df.to_csv(years_progress_filename,mode="w+",index=False,header=True)
            #Return to the SEC Historical Filings search page to move to the next year
            driver.find_element_by_css_selector("button[id='ext-gen122']").click()
            time.sleep(random.uniform(1.5,3.0))
            return driver,years_progress_df
        else:
            #Save our progress
            years_progress_df.to_csv(years_progress_filename,mode="w+",index=False,header=True)
            #Move to the next page
            driver.find_element_by_css_selector("button[id='ext-gen162']").click()
            #Wait until the next page has loaded
            for i in range(20):
                time.sleep(0.5)
                if ((page_num*20)+1)==int(driver.find_element_by_css_selector("div[class='x-paging-info']").text.split(" ")[2]):
                    time.sleep(2.0)
                    break
                if i==20:
                    #Raise an exception if the page hasn't loaded after 10 seconds
                    raise Exception("New page may not have loaded")

def loop_through_years(driver,years_progress_df,years_progress_filename,save_foldername,download_foldername,first_year,last_year):
############################################################################################################################################################################
    #The function loop_through_years moves through the different years to download the reports
    #driver is the selenium driver instance that is returned from the function start_driver
    #years_progress_df tracks which years have been completed already (in case we have to restart the download). It should be given as a DataFrame
    #years_progress_filename is the path to the file where we will save the years_progress_df DataFrame
    #save_foldername is the path to the directory where you want to ultimately save the annual reports. They will be saved in a subdirectory within save_foldername 
    #organized by company name
    #download_foldername is the path to the default download directory (on windows, this is usually {username}/Downloads). Selenium will temporarily download the reports
    #to this folder, and then my code will move them to the save_foldername directory. download_foldername should be given as a string
    #first_year is the earliest year for which we want to download the reports. It should be given as an integer
    #last_year is the latest year for which we want to download the reports. It should be given as an integer
############################################################################################################################################################################
    #Get the list of years that have not been completed yet
    years_to_be_done = years_progress_df[years_progress_df["year_done"]!="X"]["year"].to_list()
#    years_to_be_done=[1987]
    for year in years_to_be_done[0:1]:
        if first_year <= year <= last_year:
            try:
                #Click on the down arrow for the "Year" selector
                driver.find_element_by_css_selector("img[id='ext-gen213']").click()
            except:
                #For the first search, the id's are different than for subsequent searches
                #Click on the down arrow for the "Year" selector
                driver.find_element_by_css_selector("img[id='ext-gen414']").click()
                time.sleep(random.uniform(1.0,2.0))
                #Select the year from the list
                driver.find_element_by_css_selector("div[id='ext-gen421']").find_elements_by_css_selector("div[class^='x-combo-list-item']")[1995-year].click()
                time.sleep(random.uniform(1.0,2.0))
                #Click on the down arrow for the "Doctype" selector
                driver.find_element_by_css_selector("img[id='ext-gen454']").click()
                time.sleep(random.uniform(1.0,2.0))
                #Get the buttons for each doctype
                document_type_tags = driver.find_element_by_css_selector("div[id='ext-gen461']").find_elements_by_css_selector("div[class^='x-combo-list-item']")
                for document_type_tag in document_type_tags:
                    #Select "10-K" from the list
                    if document_type_tag.text.strip()=="10-K":
                        document_type_tag.click()
                time.sleep(random.uniform(1.0,2.0))
                #Click on the search button
                driver.find_element_by_css_selector("button[id='ext-gen487']").click()
                time.sleep(random.uniform(1.0,2.0))
            else:
                time.sleep(random.uniform(1.0,2.0))
                #Select the year from the list
                driver.find_element_by_css_selector("div[id='ext-gen220']").find_elements_by_css_selector("div[class^='x-combo-list-item']")[1995-year].click()
                time.sleep(random.uniform(1.0,2.0))
                #Click on the down arrow for the "Doctype" selector
                driver.find_element_by_css_selector("img[id='ext-gen253']").click()
                time.sleep(random.uniform(1.0,2.0))
                #Get the buttons for each doctype
                document_type_tags = driver.find_element_by_css_selector("div[id='ext-gen260']").find_elements_by_css_selector("div[class^='x-combo-list-item']")
                for document_type_tag in document_type_tags:
                    #Select "10-K" from the list
                    if document_type_tag.text.strip()=="10-K":
                        document_type_tag.click()            
                time.sleep(random.uniform(1.0,2.0))
                #Click on the search button
                driver.find_element_by_css_selector("button[id='ext-gen286']").click()
                time.sleep(random.uniform(1.0,2.0))
            #Wait for the page to load
            WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div[class='x-paging-info']")))

            #If we have not yet created the year's subfolder, then make it now
            if not os.path.isdir("{:s}/{:d}".format(save_foldername,year)):
                os.mkdir("{:s}/{:d}".format(save_foldername,year))

            #Download the reports for this year
            driver,years_progress_df = loop_through_pages(driver,year,years_progress_df,years_progress_filename,save_foldername,download_foldername)
    return driver 

def years_progress_creator(years_progress_filename,first_year,last_year):
############################################################################################################################################################################
    #The function years_progress_creator creates a DataFrame and saves it to a CSV file in order to track the progress of the scraper through the desired years
    #years_progress_filename is the path to the filename where you want to save the progress of the scraper through the years. It should be given as a string.
    #first_year is the earliest year for which we want to download the reports. It should be given as an integer
    #last_year is the latest year for which we want to download the reports. It should be given as an integer
############################################################################################################################################################################
    try:
        #Read in the current progress, if the file had previously been created
        years_progress_df = pd.read_csv(years_progress_filename)
    except:
        #If the file has not yet been created, create the DataFrame to track the progress
        year_list = list(range(first_year,last_year+1))
        year_list.reverse()
        years_progress_df = pd.DataFrame({"year":year_list,"pages_done":[0]*len(year_list),"year_done":[""]*len(year_list)})
        years_progress_df.to_csv(years_progress_filename,mode="x",index=False,header=True)
    else:
        year_list = years_progress_df["year"].to_list()
        years_progress_df[["year_done"]] = years_progress_df[["year_done"]].fillna("")
        #If the file had previously been created, make sure that all years in range(first_year,last_year+1) are included in the DataFrame and file
        for year in range(first_year,last_year+1):
            if year not in year_list:
                years_progress_df.loc[len(years_progress_df)] = [year,0,""]
        #Save the (possibly) updated DataFrame
        years_progress_df.to_csv(years_progress_filename,mode="w",index=False,header=True)
    return years_progress_df

def mergent_10k_downloader(driver,years_progress_filename,save_foldername,download_foldername,first_year,last_year):
############################################################################################################################################################################
    #The function mergent_10k_downloader is a wrapper to download the 10-K annual reports for the desired years from Mergent
    #driver is the selenium driver instance that is returned from the function start_driver or goto_annualreports_page
    #years_progress_filename is the path to the filename where you want to save the progress of the scraper through the years. It should be given as a string.
    #save_foldername is the path to the directory where you want to ultimately save the annual reports. They will be saved in a subdirectory within save_foldername 
    #organized by company name
    #download_foldername is the path to the default download directory (on windows, this is usually {username}/Downloads). Selenium will temporarily download the reports
    #to this folder, and then my code will move them to the save_foldername directory. download_foldername should be given as a string
    #first_year is the earliest year for which we want to download the reports. It should be given as an integer
    #last_year is the latest year for which we want to download the reports. It should be given as an integer
############################################################################################################################################################################
    
    years_progress_df = years_progress_creator(years_progress_filename,first_year,last_year)
    
    #Move the driver instance to the "SEC Historical Filings" search page
    for a_tag in driver.find_elements_by_css_selector("a[onclick='expandMenu(this)']"):
        if "SEC Filings" in a_tag.text:
            if a_tag.find_element_by_xpath("..").get_attribute("class") != "has-children active-path":
                a_tag.click()
                time.sleep(random.uniform(1.0,2.0))
            break
    driver.find_element_by_css_selector("""a[onclick="return showTab(this, 'SEC Historical')"]""").click()
    time.sleep(random.uniform(3.0,7.0))
    
    #Download the reports
    driver = loop_through_years(driver,years_progress_df,years_progress_filename,save_foldername,download_foldername,first_year,last_year)
#    driver.quit()
    return driver


#This is the path to the directory where you want to ultimately save the reports
save_foldername = "/Users/guangqili/PycharmProjects/untitled7/Mergent"
#This is your computer's default Downloads folder (where the reports will be temporarily downloaded)
download_foldername = r"/Users/guangqili/Downloads"
#This is the path to where you have saved the chromedriver.exe file (from https://chromedriver.chromium.org/downloads)
selenium_executablepath = "/Users/guangqili/PycharmProjects/untitled7/chromedriver"
#Set your user agent (which can be found by going to https://www.whatismybrowser.com/detect/what-is-my-user-agent)
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"
#Set the path to the CSV where we will save the progress of the scraper through the years for which we want the 10-K's
#Running mergent_10k_downloader will create this file (or update it if it had already been created)
years_progress_filename = "/Users/guangqili/PycharmProjects/untitled7/years_progress.csv"
#First and last years define the range of the years for which we want to download the 10-K's
first_year = 1980
last_year = 1995

#Initalize the selenium driver instance
driver = start_driver(selenium_executablepath,user_agent)

#Pause for a minute and a half to give you time to enter your UMN username and password in order to access Proquest
time.sleep(90.0)

#Run this code to download the 10-K's from Mergent
mergent_10k_downloader(driver,years_progress_filename,save_foldername,download_foldername,first_year,last_year)
