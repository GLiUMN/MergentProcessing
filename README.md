# Introduction
This is the GitHub page of the Mergent part of the Tax Reconciliation Data Project directed by Professors Anmol Bhandari and Ellen McGrattan. In this project, we aim to create a database for tax reconciliation data for C-Corporations by extracting tables from 10-K financial reports. Specifically, we want to extract tax reconciliation data from the 10-K files (PDF) between 1980 and 1995 grabbed from Mergent Archives. The HHEI presentation slides and video may be helpful for understanding the motivation and progress of our project. 

## Step 0 Match companies with compustat
Before we get into the tax reconciliation tables, we need to match the corporations in Mergent database with the corporations in Compustat. To do this, we have:
1. Match corporations with Compustat by CIK, CONM, CONML variables.
2. Extract CIK numbers from the first or second page of the 10K files and match the corporations using CIK. 
3. Manually search corporations on Google and SEC to find useful information (e.g. new name) and match the corporations using the information.

Since a lot of corporations have changed their names, merged with other corporations or bankrupted, we are not able to match every corporation in Mergent with Compustat. 

## Step 1 Download PDF files from Mergent
Mergent Archives provides historical 10-K files as PDF documents in the ”SEC Histor-ical Filings” section of its website.  We used the selenium Python package to automatethe downloading of the 10-K files, and the code for this can be found in the file ”Mer-gentv03.py.” This code opens a Chrome browser window,  goes to the main page ofMergent Archives, waits for you to log in, and then loops through all companies forthe given years and downloads each 10-K PDF file in succession. We have downloaded 27616 10K files for roughly 4634 corporations. 
Note: The code and the introduction of Step 1 is documented by Tobey.
## Step 2 Extract Pages from PDFs. 
After downloading the 10K PDF files, we want to find out which specific pages contain the tax reconciliation tables. When looking at the annual reports, we noticed there are certain words that commonly appear within the reconciliation tables, and only occasionally appear outside of the reconciliation tables. This set of words includes "reconciliation, "statutory", "income tax", and "effective tax rate", among others. In order to identify which page of the annual reports includes the reconciliation data tables, we checked how many of these keywords are found in the text extracted from each page. Pages with several of these keywords are more likely to contain the data that we want to compile for our data set. To improve the accuracy of the algorithm, we allocated different weights to those keywords. We then summed the weights of all keywords found on a given page. Thus, pages with higher weight sums were more likely to contain the reconciliation data, and so we only kept the pages with the highest sums. We use the 10k reports in 1995 as a "training set" to test the performance of our selection 



## Step 3 Extract tables from PDF pages

## Step 4 Parse the extracted tables

## Step 5 Diagnostics
To be done.
