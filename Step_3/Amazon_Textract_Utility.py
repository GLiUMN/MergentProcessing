# This is the program to extract tables or texts using Amazon Textract
# In this Utility module, the main functions and the addresses will be defined.
# Author: Guangqi Li <li001122@umn.edu>
# To run this program, the following modules are needed:
import boto3
from trp import Document
from wand.image import Image as wi
import io
import pandas as pd
import os

# Set the address of the dictionary which contains the original pdf files.
source = "/Volumes/LaCie/OCR cluster/1986"
# Set the address of the dictionary which you want to put the extracted txt files in.
text_folder = "/Volumes/LaCie/Amazon Textract/OCR/1986_txt"
# Set the address of the dictionary which you want to put the extracted forms in.
forms_folder = ""
# Set the address of the dictionary which you want to put the extracted tables in.
table_folder = "/Volumes/LaCie/Amazon Textract/OCR/1986_table"
# Set the address of the csv file which is used to track the progress.
csv_address = "/Volumes/LaCie/Amazon Textract/OCR/1986_tracking.csv"

# The function creating a tracking csv file.
def tracking_csv():
    # If the tracking csv is not created, then create one.
    if not os.path.isfile(csv_address):
        # Get a list of all the pdf files.
        files = os.listdir(source)
        # Remove a system file on MacOs.
        if ".DS_Store" in files:
            files.remove(".DS_Store")
        # Create lists to store the filename and the status.
        file_list = []
        extracted = []
        for file in files:
            x = file.split(".")
            file_list.append(x[0])
            extracted.append("0")
        # Create the tracking csv
        trackingcsv = {"File":file_list,
                       "Extracted":extracted}
        df = pd.DataFrame(trackingcsv)
        df.to_csv(csv_address,mode="w", index=False)

# The function tracking the extraction progress
def track_progress():
    file_done = pd.read_csv(csv_address)
    # Get the number of files.
    n = len(file_done)
    # Set i to be the index of tracking progress
    i = 0
    # Find the latest file which is under extraction or not being extracted yet.
    while file_done.at[i, 'Extracted'] != 0:
        i = i + 1
    list = [n, i]
    return list

# The function converting a pdf to an image.
# Get the file name of the pdf from the Amazon_tesseract_forms/tables function.
def pdf_to_image(file_name1):
    # Get the file name.
    str1 = "{}/{}.pdf".format(source,file_name1)
    # Convert the pdf to an image.
    pdf = wi(filename=str1, resolution=300)
    pdfImage = pdf.convert('jpeg')

    for img in pdfImage.sequence:
        imgPage = wi(image=img)
        imageBlob = imgPage.make_blob('jpeg')
    pdfImage.destroy()
    # Convert the image to a byte array.
    image_bytes = io.BytesIO(imageBlob)
    return image_bytes

# The function that extracting forms on Amazon Tesseract.
def Amazon_tesseract_forms(index):
    # Read the tracking csv
    file_csv = pd.read_csv(csv_address)
    # Get the name of the file that needs to be processed.
    file_to_be_done = file_csv.at[index,"File"]
    # Call the function and convert the pdf to a byte array.
    image_1 = pdf_to_image(file_to_be_done)
    # Amazon Textract client
    textract = boto3.client('textract')
    # Call Amazon Textract
    response = textract.analyze_document(
        Document={'Bytes':image_1.getvalue()},
        FeatureTypes=["FORMS"])
    # get the response from Amazon
    doc = Document(response)
    # Creates lists to store the forms.
    Key=[]
    Value=[]
    # Print forms
    for page in doc.pages:
        for field in page.form.fields:
            Key.append(field.key)
            Value.append(field.value)
    # Put the form into a csv file.
    tocsv={"Key":Key,
        "Value":Value}
    amazon_csv = pd.DataFrame(tocsv)
    amazon_csv_address = "{}/{}.csv".format(forms_folder,file_to_be_done)
    amazon_csv.to_csv(amazon_csv_address,mode="w", index=False)

    # Print detected text
    output = []
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            output.append(item["Text"])
    amazon_text_address = "{}/{}.txt".format(text_folder,file_to_be_done)

    # Mark the file as "extracted" in the tracking csv.
    with open(amazon_text_address, "w") as text_file:
        for text in output:
            text_file.write("\n"+text)
    file_csv.at[index,"Extracted"] = 1
    file_csv.to_csv(csv_address,mode="w+",index=False)
    print(file_to_be_done)

# The function that extracts tables on Amazon Tesseract.
def Amazon_tesseract_tables(index):
    # Read the tracking csv
    file_csv = pd.read_csv(csv_address)
    # Get the name of the file that needs to be processed.
    file_to_be_done = file_csv.at[index,"File"]
    image_1 = pdf_to_image(file_to_be_done)
    # Amazon Textract client
    textract = boto3.client('textract')
    # Call Amazon Textract
    response = textract.analyze_document(
        Document={'Bytes':image_1.getvalue()},
        FeatureTypes=["TABLES"])

    doc = Document(response)

    for page in doc.pages:
        # Print tables
        # i is the index of the tables
        # One table one csv file.
        i = 0
        for table in page.tables:
            i = i + 1
            # Create a list of the rows.
            # One element is a row in the table.
            data = []
            for row in table.rows:
                # Get the length of the row and create a list of this row
                list = [""] * len(row.cells)
                j = 0
                # Put the content in every cell into the row list.
                for cell in row.cells:
                    list[j] = cell.text
                    j = j + 1
                # Put the row list to the table list.
                data.append(list)

            df = pd.DataFrame(data)
            df.to_csv("{}/{}_{}.csv".format(table_folder,file_to_be_done,i),
                      header=False, mode="w", index=False)
    # Print the extracted text.
    output = []
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            output.append(item["Text"])
    amazon_text_address = "{}/{}.txt".format(text_folder, file_to_be_done)
    with open(amazon_text_address, "w") as text_file:
        for text in output:
            text_file.write("\n"+text)
    # Mark the file as "extracted" in the tracking csv.
    file_csv.at[index,"Extracted"] = 1
    file_csv.to_csv(csv_address,mode="w+",index=False)
    print(file_to_be_done)
