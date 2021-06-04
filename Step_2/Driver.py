#This moduel stores the main functions of the program.

import PyPDF2
import io
from PIL import Image
import pytesseract
from wand.image import Image as wi
import os
import pandas as pd
import Inputs

# Import the parameters for convenience
source = Inputs.source
destination = Inputs.destination
csv_address = Inputs.csv_address
score_keyword_csv = Inputs.score_keyword_csv
year = Inputs.year
first_keywords_weight = Inputs.first_keywords_weight
second_keywords_weight = Inputs.second_keywords_weight

# Define the function to check whether the tracking csv file exist or not. If not, then create one.
# The tracking csv sort the company reports by their sizes in order to implement parallel processes.
# It is because that the program won't start the next round until all the parallel processes finish.
# If the program compiles a big file and a tiny fill at the same time, the program will be less efficient.
def tracking_csv():
    # Check whether the csv file exists, if not, then create one.
    if not os.path.isfile(csv_address):
        # Get all the filenames in the source dictionary.
        pdfs = os.listdir(source)
        # Create a list containing each filename and the matched file size.
        pairs = []
        for pdf in pdfs:
            # Get the full file path.
            location = os.path.join(source,pdf)
            # Get the size of each file.
            size = os.path.getsize(location)
            # If the size is 0, then mark it as not extractable, which is -1 in the csv file.
            if size == 0:
                pairs.append([size,pdf,-1])
            else:
                pairs.append([size,pdf,0])
        # Sort the list by the first element, size.
        pairs.sort(key=lambda s:s[0])
        # Create three lists that will be used to create DataFrame.
        # Each list only stores one sort of data.
        # Store the filenames
        filename = []
        # Store the company names
        companies = []
        # The extracted list counts whether each element is extractable (or extracted). The element can be -1, 0, 1, and 2.
        # -1 means the extraction failed. 0 means the extraction hasn't started.
        #  1 means the extraction is finished.
        extracted = []
        # Store the size of each file
        size = []
        # Set the index
        index = []
        i = 1
        for pair in pairs:
            filename.append(pair[1])
            # Get the company names from the filenames.
            x = pair[1].split("_")
            companies.append(x[0])
            extracted.append(pair[2])
            size.append(pair[0])
            index.append(i)
            i = i+1
        tocsv = {"Index":index,
                "Filename":filename,
                "Company":companies,
                 "Size":size,
                 "Extracted":extracted}
        df = pd.DataFrame(tocsv)
        df.to_csv(csv_address,mode="w", index=False)

# Define the function that tracks the latest extracted pdf
def track_progress():
    # Read the csv file
    companies_done = pd.read_csv(csv_address)
    # Set n to be the number of rows.
    n = len(companies_done)
    # Set i to be the index of tracking progress
    i = 0
    # Find the latest file which is under extraction or not being extracted yet.
    while companies_done.at[i,'Extracted'] != 0:
        i = i+1
    # Return a list that stores the the total number of companies and the company that is under extraction or ready to be extracted.
    LIST = [n,i]
    return LIST

# Define the function that splits the full pdf file into one-page pdf files.
def split_pages(index):
    # Read the csv file.
    companies_done = pd.read_csv(csv_address)
    # Get the filename which is not split yet.
    filename = companies_done.at[index,'Filename']
    # Get the address of the full pdf file.
    address = '{}/{}'.format(source, filename)
    # Get the name of this company
    company_name = companies_done.at[index,'Company']
    # Run PDF reader
    with open(address, "rb") as f:
        pdf_file = PyPDF2.PdfFileReader(f, strict=False)
        # Get the number of pages.
        pdf_pages_len = pdf_file.getNumPages()
        # Split pages into pdf files.
        for i in range(pdf_pages_len):
            output = PyPDF2.PdfFileWriter()
            output.addPage(pdf_file.getPage(i))
            string = str(i + 1)
            # Create a new pdf file.
            str1 = '{}/{}_{}_page_{}.pdf'.format(destination, company_name, year, string)
            # Put the page into the pdf file.
            with open(str1, "wb") as outputstream:
                output.write(outputstream)


# Define the function that calculates the score of each page.
def page_score(company_name,text,page):
    # Set a score for this pdf page.
    score = 0
    # Set a dictionary stores whether each keyword appear in the text.
    keyword_appearance = Inputs.keyword_appearance
    keyword_appearance['Company'] = company_name
    keyword_appearance['Page'] = page
    # Then we are ready to search for keywords in the text.
    # Firstly, we search for the first-level keywords.
    for keyword in Inputs.first_keywords:
        if keyword in text:
            # If any keyword is founded in the text, add the weight on the score.
            score = score + first_keywords_weight[keyword]
            # Record the appearance of this keyword in the dictionary.
            keyword_appearance[keyword] = 1
        # If the keyword doesn't appear, we also mark it out in the dictionary.
        else:
            keyword_appearance[keyword] = 0
    # Then, we search for the first-level keywords which will be only counted once even if two keywords both appear.
    for keyword in Inputs.first_keywords_set1:
        if keyword in text:
            keyword_appearance[keyword] = 1
        else:
            keyword_appearance[keyword] = 0
    for keyword in Inputs.first_keywords_set1:
        if keyword_appearance[keyword] == 1:
            score = score + first_keywords_weight[keyword]
            break
    for keyword in Inputs.first_keywords_set2:
        if keyword in text:
            keyword_appearance[keyword] = 1
        else:
            keyword_appearance[keyword] = 0
    for keyword in Inputs.first_keywords_set2:
        if keyword_appearance[keyword] == 1:
            score = score + first_keywords_weight[keyword]
            break
    # Search for the first-level keywords that we want to count how many times they appear.
    for keyword in Inputs.first_keywords_n:
        b = text.count(keyword)
        score = score + b * first_keywords_weight[keyword]
        keyword_appearance[keyword] = b
    # Count the digits in this page.
    digits_n = sum(c.isdigit() for c in text)
    # Search for the first-level keywords only if the page contains a large number of digits.
    for keyword in Inputs.first_keywords_digits:
        if keyword in text and digits_n >= Inputs.digits:
            score = score + first_keywords_weight[keyword]
            keyword_appearance[keyword] = 1
        else:
            keyword_appearance[keyword] = 0
    # If any first-level keywords are founded, we can search for the second-level keywords.
    if score > 0:
        for keyword in Inputs.second_keywords:
            if keyword in text:
                score = score + second_keywords_weight[keyword]
                keyword_appearance[keyword] = 1
            else:
                keyword_appearance[keyword] = 0
        for keyword in Inputs.second_keywords_set1:
            if keyword in text:
                keyword_appearance[keyword] = 1
            else:
                keyword_appearance[keyword] = 0
        for keyword in Inputs.second_keywords_set1:
            if keyword_appearance[keyword] == 1:
                score = score + second_keywords_weight[keyword]
                break
        for keyword in Inputs.second_keywords_set2:
            if keyword in text:
                keyword_appearance[keyword] = 1
            else:
                keyword_appearance[keyword] = 0
        for keyword in Inputs.second_keywords_set2:
            if keyword_appearance[keyword] == 1:
                score = score + second_keywords_weight[keyword]
                break
        if digits_n >= Inputs.digits:
            score = score + second_keywords_weight['digits']
            keyword_appearance['digits'] = 1
        else:
            keyword_appearance['digits'] = 0
    # Put the score in the dictionary.
    keyword_appearance['Score'] = score
    return keyword_appearance

# Apply the pytesseract on every pdf and extract text from each pdf.
# Then we need to see how likely this pdf contains the information we want.
# In this function, we set a score for every pdf file.
# If any keywords are founded in the text, a specific score will be added.
# Finally we remain the pdf that gains the highest score.
# This function also creates a csv file tracking how many scores each pdf gains.
def filter_pdf(index):
    # Read the csv file.
    companies_done = pd.read_csv(csv_address)
    # Get the company name.
    company_name = companies_done.at[index,'Company']
    # Set a list of pdf files
    pdfs = []
    # Get all filenames in this dictionary.
    all_files = os.listdir(destination)
    # Check the file name of each pdf.
    # If no one starts with the company name, we should call the split_pages to split the full PDF.
    if not any(file.startswith(company_name) for file in all_files):
        split_pages(index)
    all_files2 = os.listdir(destination)
    # Then get all the filenames that start with the company name.
    for file in all_files2:
        if file.startswith(company_name):
            # Get the page number
            i = file.split('_')
            j = i[3].split('.')
            # The first element in each sublist is the filename.
            # The second element is the exact page where it is located in the full pdf.
            pdfs.append([file,int(j[0])])
    # Sort the list by the page number
    pdfs.sort(key=lambda x:x[1])
    # Set up the max score of this company.
    max = 0
    # Set a list that contains the remaining pdf files.
    pages_remaining = []
    # Set a list that contains the score of each page and the keyword appearance in each page.
    # The format of the element in this list is dictionary.
    Record_keyword = []

    # Start filtering
    for pdf in pdfs:
        # Get the pdf address.
        pdf_address = '{}/{}'.format(destination,pdf[0])
        # Convert the pdf file to a image.
        image = wi(filename=pdf_address,resolution=300)
        pdfImage = image.convert('jpeg')
        imageBlobs = []
        for img in pdfImage.sequence:
            imgPage = wi(image=img)
            imageBlobs.append(imgPage.make_blob('jpeg'))
        pdfImage.destroy()
        recognized_text = []
        # Convert image to text.
        for imgBlob in imageBlobs:
            im = Image.open(io.BytesIO(imgBlob))
            text = pytesseract.image_to_string(im, lang='eng')
            recognized_text.append(text)
            ListToStr = ''.join([str(elem) for elem in recognized_text])
        text = ListToStr
        # Call the page_score function to calculate the score of this page and collect the appearance of the keywords.
        Keyword_appearance = page_score(company_name,text,pdf[1])

        score = Keyword_appearance['Score']
        # If the page gains any scores, then we can record the information of this page.
        if score > 0:
            Record_keyword.append(Keyword_appearance.copy())

        # If the score is greater than the current max score.
        if score > max:
            # Update the max score.
            max = score
            # If this is the first page that scores, directly remain this page.
            if len(pages_remaining) == 0:
                pages_remaining.append([pdf_address,pdf[1]])
            # Otherwise, delete every pdf file remained and remain the current page.
            else:
                for pages in pages_remaining:
                    os.remove(pages[0])
                pages_remaining = []
                pages_remaining.append([pdf_address,pdf[1]])
        # If the last page gets the highest score and the current page also scores then the current page is remained.
        # The current page probably also contains some tax information.
        elif score != 0 and len(pages_remaining) != 0 and int(pages_remaining[-1][1]) == int(pdf[1]) - 1:
            pages_remaining.append([pdf_address,pdf[1]])
        # Remove the page if it gets 0 score or the score is less than the max score.
        elif score == 0 or score < max:
            os.remove(pdf_address)
        # If the score of this page is equal to the maximum we have, remain all of them.
        elif score != 0 and score == max:
            pages_remaining.append([pdf_address,pdf[1]])
    # Export the record of each page to the csv file.
    for record in Record_keyword:
        OCR_data = pd.DataFrame(record,index=[0])
        if not os.path.isfile(score_keyword_csv):
            OCR_data.to_csv(Inputs.score_keyword_csv, mode='a', index=False)
        else:
            OCR_data.to_csv(Inputs.score_keyword_csv, mode='a', index=False, header=False)
    # If the there are any pages remained, then we mark this company as 1, which means "Extracted".
    companies_done = pd.read_csv(csv_address)
    if len(pages_remaining) > 0:
        companies_done.at[index, 'Extracted'] = 1
    # If no page is remained, then we mark it as -1, which means failed extraction.
    else:
        companies_done.at[index, 'Extracted'] = -1
    companies_done.to_csv(csv_address, mode='w+', index=False)











