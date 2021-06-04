# This is the module where you set parameters.

# Set the year
year=1991
# The address of the folder storing full annual report files.

source = '/Users/guangqili/PycharmProjects/untitled7/Mergent/{}'.format(year)
# The address of the folder to store extracted pages.
destination = '/Volumes/LaCie/OCR/{}'.format(year)
# The address of the csv file that tracks which pdf files are extracted or not.
csv_address = '/Volumes/LaCie/OCR/OCR_process_{}.csv'.format(year)
# The address of the csv file that records the appearance of each keyword and the score of each page.
score_keyword_csv = '{}/Score_keyword.csv'.format(destination)

# Set the first-level keywords, which will be searched in the first round, and the weight of each keyword.
first_keywords=['reconciliation','income tax rate','State income tax','State tax']
# Set the first-level keywords which will be only counted once even if two keywords both appear.
first_keywords_set1=['Effective tax rate','Effective income tax']
first_keywords_set2=['State income tax','State tax']

# Set the first-level keywords that you want to count how many times they appear.
# The score of each keyword is equal to the product of the times of its appearance and the weight of each appearance.
# You can also set the maximum point of each keyword by setting the max times we put in to the point calculation.
first_keywords_n=['Statutory','statutory']
first_keywords_maxn = 3
# Set the first-level keywords which you want to count its appearance only if the page contains a certain number of digits.
first_keywords_digits=['Income Tax','INCOME TAX']
# Set the amount of digits
digits=150
# Set the weights of each keyword.
first_keywords_weight={'reconciliation':0.27,
                       'income tax rate':0.21,
                       'Effective tax rate':0.54,
                       'Effective income tax':0.54,
                       'State income tax':0.3,
                       'State tax':0.3,
                       'Statutory':0.3,
                       'statutory':0.3,
                       'INCOME TAX':0.18,
                       'Income Tax':0.18}


# Set the second-level keywords, which will be searched only if any of the first_level keywords are found in the pdf.
second_keywords=['%',str(year),str(year-1),'Federal income tax']
# Set the second-level keywords which you only want to count once even if two keywords appear.
second_keywords_set1=['federal','Federal']
second_keywords_set2=['provision','Provision']
# Set the weights of the second-level keywords.
second_keywords_weight={'%':0.08,
                        str(year):0.12,
                        str(year-1):0.07,
                        'federal':0.2,
                        'Federal':0.2,
                        'Federal income tax':0.25,
                        'provision':0.15,
                        'Provision':0.15,
                        'digits':0.15}

# Record the appearance of each keyword
# One means appear and zero means not appear.

keyword_appearance={'Company':0,
                    'Page':0,
                    'Score':0,
                    'reconciliation':0,
                    'income tax rate':0,
                    'Effective tax rate':0,
                    'Effective income tax':0,
                    'State income tax':0,
                    'State tax':0,
                    'Statutory':0,
                    'statutory':0,
                    'INCOME TAX':0,
                    'Income Tax':0,
                    '%':0,
                    str(year):0,
                    str(year-1):0,
                    'federal':0,
                    'Federal':0,
                    'Federal income tax':0,
                    'provision':0,
                    'Provision':0,
                    'digits':0}
