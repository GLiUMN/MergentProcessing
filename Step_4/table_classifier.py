#This is example code of how to use a pretrained table classifer. There are
#several TODO items that need to be updated in order to apply this to your
#application.
#
#The biggest TODO is converting your tables into strings. For example, if the
#table is a csv file, you need to extract every cell of the csv file and concatenate
#that table into a single string. Each table needs to be a seperate string.
#
#The table classifer will produce two labels: __table_target__ and __table_nontarget__
#where __table_target__ is what the classifer labels as the tax reconciliation table.
#The classifer will also output a confidence (which lies between zero and one),
#which is how confident the classifer is in its label.
#
#Author: Thomas J. May <may00013@umn.edu>
import table_classifier_
import fasttext
import os
import re
import pandas as pd

class Text_Normalizer:
    """
    This normalizes text for the the fasttext text classifier. This is an object
    to pre-compile some re patterns
    """

    def __init__(self):
        """
        Initialize the object
        """

        #Generate some regular expression patterns to normalize the data
        self.html_tag_re      = re.compile('<.*?>|&(([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});)+') #The pattern for any html tag
        self.whitespace_re    = re.compile("\s+") #Remove multiple white spaces and convert them into one
        self.us_correct_re    = re.compile("u.s.") #This is to replace "u.s." with "us" instead of "u s"
        self.normalization_re = re.compile("(-|[_:;#%$&.!?,\"/()<>]|[0-9]|xxx+)") #The things we need to remove

    def __call__(self,text):
        """
        This normalizes the input text. If this data comes from html or xml, you
        need to remove all the tags before hand

        Arguments:
            text - the text we want to normalize

        Returns:
            the normalized text
        """

        #Normalize the text
        normalized_text = text.lower()
        normalized_text = re.sub(self.html_tag_re," ",normalized_text)
        normalized_text = re.sub(self.us_correct_re,"us",normalized_text)
        normalized_text = re.sub(self.normalization_re," ",normalized_text)
        normalized_text = re.sub(self.whitespace_re," ",normalized_text)

        return normalized_text

fasttext_model_file = "/Users/guangqili/PycharmProjects/untitled2/tax_table.model" #TODO This needs to be changed to the file path to the model file

#Initialize
model      = fasttext.load_model(fasttext_model_file)
normalizer = Text_Normalizer()

Source_address = "/Volumes/LaCie/Amazon Textract/OCR/1986_table"
#Generate table strings
string=[]
csvs = os.listdir(Source_address)

for csv in csvs:
    with open('{}/{}'.format(Source_address,csv)) as f:
        print(csv)
        str = f.read()
        string.append(str)

#Load the set of tables
tables_strings = string #TODO You need to plug in your table strings here.

#Loop over the tables and generate labels
table_classification = []
#generate lists to build a dataframe
index1 = []
label1 = []
confidence1 = []

for (index,table_cur) in enumerate(tables_strings):
    #Normalize the table
    normalized_table = normalizer(table_cur)

    #Classify the table
    result     = model.predict(normalized_table)
    label      = result[0][0]
    confidence = result[1][0]

    #Store the result
    table_classification.append((index,label,confidence))
    index1.append(index)
    label1.append(label)
    confidence1.append(confidence)

#TODO Do something with the table_classification
dict={"Index":index1,
      "File":csvs,
      "Label":label1,
      "Confidence":confidence1,
      }
df=pd.DataFrame(dict)
df.to_csv("/Volumes/LaCie/Amazon Textract/OCR/1986_table_classifier.csv",mode="w",index=False)
