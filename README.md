# Introduction
This is the GitHub page of the Mergent part of the Tax Reconciliation Data Project directed by Professors Anmol Bhandari and Ellen McGrattan. In this project, we aim to create a database for tax reconciliation data for C-Corporations by extracting tables from 10-K financial reports. Specifically, we want to extract tax reconciliation data from the 10-K files (PDF) between 1980 and 1995 grabbed from Mergent Archives. The HHEI presentation slides and video may be helpful for understanding the motivation and progress of our project. 

We use "Tax Reconciliation project plan.xlsx" and "mergent_progress.csv" to track the progress of our Mergent project.
<details>
  <summary>**Instructions of how to use the tracking files**</summary>
  
  1. Tax Reconciliation project plan.xlsx: 
  * The first spreadsheet is a brief introduction and the main steps of this project. 
  * The second spreadsheet shows the progress of this project: the number of companies that have been processed in each step, the associated market cap of these companies, and the share of market cap relative to the total market cap in Compustat. 
  * The third spreadsheet collects the information of the top 10 companies whose 10K files are missed from our dataset in terms of market cap. The fourth spreadsheet shows the top 10 companies whose 10K files are downloaded but eventually failed to be parsed. 
  
  2. mergent_progress.csv: This file is based on the corporations in compustat. We use this file to figure out which companies are in our dataset and which step the company is in. The keys of this spreadsheet are shown below:
  * fyear: the fiscal year of the data
  * conm: company name in capital letters in compustat
  * conml: company name in compustat
  * cik: CIK number
  * tic: TIC code
  * csho: common shares outstanding
  * prcc_f: price close - annual - fiscal
  * market_cap: market cap
  * company: the associated company name in Mergent if the company's 10K in that year is found in Mergent
  * downloaded: 1 if we downloaded the company's 10K in that year and 0 otherwise
  * extracted: 1 if my classifier extracted PDF pages from the company's 10K in that year and 0 otherwise
  * amazon: 1 if Amazon Textract extracted tables from the selected PDF pages and 0 otherwise
  * classified: 1 if the table is recognized as tax reconciliation table by Thomas's classifier and 0 otherwise
  * parsed: 1 if the tax reconciliation table is parsed and 0 otherwise
     
</details>

## Step 0 Match companies with compustat
Before we get into the tax reconciliation tables, we need to match the corporations in Mergent database with the corporations in Compustat. To do this, we have:
1. Match corporations with Compustat by CIK, CONM, CONML variables.
2. Extract CIK numbers from the first or second page of the 10K files and match the corporations using CIK. 
3. Manually search corporations on Google and SEC to find useful information (e.g. new name) and match the corporations using the information.

Since a lot of corporations have changed their names, merged with other corporations or bankrupted, we are not able to match every corporation in Mergent with Compustat. However, it will still be very helpful if we can match more compranies.

## Step 1 Download PDF files from Mergent
Mergent Archives provides historical 10-K files as PDF documents in the ”SEC Histor-ical Filings” section of its website.  We used the selenium Python package to automatethe downloading of the 10-K files, and the code for this can be found in the file ”Mer-gentv03.py.” This code opens a Chrome browser window,  goes to the main page ofMergent Archives, waits for you to log in, and then loops through all companies forthe given years and downloads each 10-K PDF file in succession. We have downloaded 27616 10K files for roughly 4634 corporations. 
Note: The code and the chrome driver are also stored in folder "Step_1". The code and the introduction of Step 1 is documented by Tobey.

**Issue:** A lot of 10K files we have downloaded are "damaged" files. These files are usually very small. Some examples can be found in folder "Step_1". We can use other forms of financial reports to replace the damaged files. We can either design another algorithm to extract files from Mergent or manually download files from Mergent website. 

## Step 2 Extract Pages from PDFs. 
After downloading the 10K PDF files, we want to find out which specific pages contain the tax reconciliation tables. When looking at the annual reports, we noticed there are certain words that commonly appear within the reconciliation tables, and only occasionally appear outside of the reconciliation tables. This set of words includes "reconciliation, "statutory", "income tax", and "effective tax rate", among others. In order to identify which page of the annual reports includes the reconciliation data tables, we checked how many of these keywords are found in the text extracted from each page. Pages with several of these keywords are more likely to contain the data that we want to compile for our data set. To improve the accuracy of the classfier, we allocated different weights to those keywords. We then summed the weights of all keywords found on a given page. Thus, pages with higher weight sums were more likely to contain the reconciliation data, and so we only kept the pages with the highest sums. We use the 10k reports in 1995 as a "training set" to test the performance of our keywords and weights. 

To use the code, you should set up the addresses, keywords, and associated weights in "Inputs.py" and run the single process code "Driver.py" or the parallel process code "Driver_multiprocess.py". "Utility.py" stores the functions that are used in the classfier. 

**Issues:** The accuracy rate of this classfier is 70%-80%. We need to adjust the selection of keywords and weights to extract pages from the left 10K files.

## Step 3 Extract tables from PDF pages
Then, we want to extract the tax reconciliation tables from the PDF pages using Amazon Textract. Check https://docs.aws.amazon.com/textract/latest/dg/getting-started.html to see how to set up Amazon Textract on your own device. 




## Step 4 Parse the extracted tables

## Step 5 Diagnostics
To be done.

## Appendix



