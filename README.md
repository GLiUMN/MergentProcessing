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



## Step 0 Download PDF Files from Mergent
Mergent Archives provides historical 10-K files as PDF documents in the ”SEC Histor-ical Filings” section of its website.  We used the selenium Python package to automatethe downloading of the 10-K files, and the code for this can be found in the file ”Mer-gentv03.py.” This code opens a Chrome browser window,  goes to the main page ofMergent Archives, waits for you to log in, and then loops through all companies forthe given years and downloads each 10-K PDF file in succession. We have downloaded 27616 10K files for roughly 4634 corporations. 
Note: The introduction of Step 1 is documented by Tobey.

**Issue:** A lot of 10K files we have downloaded are "damaged" files. These files are usually very small. Some examples can be found in folder "Step_1". We can use other forms of financial reports to replace the damaged files. We can either design another algorithm to extract files from Mergent or manually download files from Mergent website. 

## Step 1 Match Companies with Compustat
Before we get into the tax reconciliation tables, we need to match the corporations in Mergent database with the corporations in Compustat. To do this, we have:
1. Match corporations with Compustat by CIK, CONM, CONML variables.
2. Extract CIK numbers from the first or second page of the 10K files and match the corporations using CIK. 
3. Manually search corporations on Google and SEC to find useful information (e.g. new name) and match the corporations using the information.

Since a lot of corporations have changed their names, merged with other corporations or bankrupted, we are not able to match every corporation in Mergent with Compustat. However, it will still be very helpful if we can match more compranies.
**Add details how to use Tobey's code to do this step**

## Step 2 Extract Pages from PDFs. 
After downloading the 10K PDF files, we want to find out which specific pages contain the tax reconciliation tables. When looking at the annual reports, we noticed there are certain words that commonly appear within the reconciliation tables, and only occasionally appear outside of the reconciliation tables. This set of words includes "reconciliation, "statutory", "income tax", and "effective tax rate", among others. In order to identify which page of the annual reports includes the reconciliation data tables, we checked how many of these keywords were found in the text extracted from each page (using tesseract-ocr). Pages with several of these keywords are more likely to contain the data that we want to compile for our data set. To improve the accuracy of the classfier, we allocated different weights to those keywords. We then summed the weights of all keywords found on a given page. Thus, pages with higher weight sums were more likely to contain the reconciliation data, and so we only kept the pages with the highest sums. We use the 10k reports in 1995 as a "training set" to test the performance of our keywords and weights. 

To run the classfier, you should set up the paths, keywords, and associated weights in "Inputs.py" and run the single process code "Driver.py" or the parallel process code "Driver_multiprocess.py". "Utility.py" stores the functions that are used in the classfier. 

**Make the above user-friendly. Add some examples**

**Issues:** Now the accuracy rate of this classfier is 70%-80%. We need to find a better combination of keywords and weights or even design a better classfier to grab the correct pages from the left PDFs. Our current strategy of filtering out the wrong pages is to apply Thomas's fasttext classfier on the tables extracted by Amazon Textract. 

There are some special cases that we should always keep in mind. 

1. Some corporations do not have a tax reconciliation table, instead, they list their tax reconciliation information in paragraph. To deal with these exceptions, we may use some natural language processing models such as BERT. Check "american home products corp_1981_page_57.pdf", "international business machines corp_1981_page_57.pdf" and "coca cola co_1982_page_100.pdf" in "Step_2". 
2. These old documents can be very blurry so tesseract-ocr cannot read the texts on the pages. Check "american express co_1985.pdf".
3. Since the PDF 10K files are scanned copy of the printed 10K reports, one printed page can be split into multiple PDF pages. If the tax reconciliation table is split into multiple pages, the most left columns usually describe the newest tax reconciliation data, and these columns are often located in the page that we extracted (since this page contains the most keywords). Though our classfier aims to extract all these pages, the pages with very little information (such as "cheyenne software inc_1995_page_95.pdf" and "tektronix inc_1995_page_116.pdf") are often be missed. To better understand this issue, check the PDF pages of cheyenne software inc and tektronix inc.
4. We may find multiple tax reconciliation tables in one 10K file. Except for the case mentioned above, some 10K files have duplicate information about a single firm. We may find a tax reconciliation table appear twice in one 10K file. Another case is that some corporations combined the 10K reports for the parent companies and 10K reports for the subsidiaries together. In both cases, multiple PDF pages will be extracted from the original PDF. We need to be careful with the different tax reconciliation tables extracted from the same 10K form. 


## Step 3 Extract Tables from PDF Pages
Then, we want to extract the tax reconciliation tables from the PDF pages using Amazon Textract. Traditional OCR tools can only extract texts from PDFs and it is very hard for us to deal with these texts. To directly extract the tax reconciliation tables from PDFs, we employed Amazon Textract, an open source tool developed by Amazon. The advantage of Amazon Textract is that it can detect whether an image or a PDF page contains forms or tables and it can directly extract tables or forms from the original files. Once Amazon Textract detects tables, we can extract the tables from the PDF or image and convert the tables to a manageable format (CSV). We connected Amazon Textract with our own device using API so we can transport a batch of PDFs to Amazon and receive extracted tables and texts. After this step, we extracted tables and texts from the PDF pages from Step 2. We store tables in CSV format and texts in TXT format. 

Check https://docs.aws.amazon.com/textract/latest/dg/getting-started.html about how to set up Amazon Textract on your own device. After this, you should be able to use the code "Amazon_Textract_Utility.py" and "Amazon_Textract_Driver.py" in folder "Step_3". The code stores the extracted texts no matter whether Amazon Textract detects tables or not.
1. convert a PDF page to an image
2. convert the image to a byte array
3. pass the byte array to Amazon Textract
4. receive extracted information and store the texts in a txt file 
6. transform the received information to tables and store every single table in a separate file

Some examples of the extracted tables and original PDFs can also be found in folder "Step_3".

## Step 4 Classify the Extracted Tables
Since every PDF page can contain more than one tables, we want to know which specific table is tax reconciliation table. Hence, we train a classifier using fastText to classify the tables. This classifier is trained by Thomas. The details about the classifier can be found in the tech appendix documentation.
After running the classifier, we obtain a CSV table, indicating which table is classified as target table (tax reconciliation table) or non-target table and the associated confidence level. If the fastText classifier does not classify and tables found in a PDF page as tax reconciliation table, the page is either the wrong page or has the tax reconciliation data in paragraphs instead of tables. 

**Issues:** Sometimes the fastText classifier fails to recognize tax reconciliation table. Some examples can be found in folder "Step_4".

## Step 5 Parse the Tax Reconciliation Tables
Next, we want to combine the tax reconciliation tables of different companies to a single CSV file and parse the tables into a fixed format. An example of the parsed CSV can be found in folder "Step_5". Here are the keys for the columns names:

* company: company name
* year_10k: the year when the 10K form was filed
* year_col: the year of the data
* var: variable name
* data_var: the parsed data
* data_row: the original data in the separate CSVs
* indicator: indicating if the data is in amounts or rates
* i_row: row number of the data
* N_rows: total number of rows of the table

**Issues:** Parsing the tax reconciliation tables is harder than we expect. The qualities of these scanned 10K docuemnts vary a lot across companies across years. Amazon Textract cannot always extract the correct information from from PDFs in a correct format. We need to take care of each type of exceptions and keep developing our parsing code. Here are some special cases:

1. Amazon Textract put multlple values in one cell. Check row 282 in "mergent_1995" and "aurora electronics inc_1995_page_62_2.csv".
2. Amazon Textract split the label of a variable into two or three rows. Check rows 104-121, 703-711 and associated CSV files. One way to fix this is to combine the blank row with the row above it. However, this doesn't always work. Sometiems the blank rows should be merged with the row below it rather than the row above it. 
3. When the tax reconciliation table is plit into multiple pages, we should identify whether the table is cut lengthwise or crosswise in order to merge the separate CSVs together. See the PDF pages of american stores co and amrep corp. More importantly, when only one or two rows are cut out from the bottom, we are very likely to miss them from the previous steps. This leads to missing data.
4. As we mentioned in Step 2 issue 4, one 10K file may contain more than one tax reconciliation tables. It will be a problem if we parse all these tables. 
5. We cannot always find variable indicator (rate or amount) in the tax reconciliation table. 

Since we want to specifically deal with case 3 and 4, we asked our parsing code to skip the companies if more than one tax reconciliation tables are extracted from their 10K reports in one year. The parsing code is still being developed and it will be uploaded later.

## Step 6 Convert Amounts to Rates and Diagnostics

There are several things are pending with this project. Firstly, we want to convert the data in amounts to data in rates. Next, we want to do diagostics to identify wrong data in our datasets. There are a bunch of different problems within each step and we should consider which problems we should care about and which problems we can just ignore. 

## Appendix
The results for each step are being uploaded to Ellen's cluster. Here are the addresses of these files:
1. Downloaded Mergent 10K files: /home/shared/li001122/1_Downloaded_10K_Mergent - being uploaded
2. Extracted pages from Step 2: /home/shared/li001122/2_Extracted_Pages - uploaded
3. Extracted texts and tables from PDFs using Amazon Textract: /home/shared/li001122/3_Extracted_Table_Amazon_Textract. - uploaded
4. The tables that are identified as target table by fastText classifier: /home/shared/li001122/4_Classfied_as_Tax_Table - uploaded
5. The parsed files for each year: /home/shared/li001122/5_Parsed_Tables - to be uploaded


