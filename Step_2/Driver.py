# This is the driver module of the program.
import Utility
# Firstly, check whether we have a tracking csv or not. If not, the function will create one.
Utility.tracking_csv()
# Get the list of the function. This list contains two elements.
# The first element is the total number of companies in this year.

# The second element is the company which is under extraction or needed to be extracted.
list = Utility.track_progress()
# Then call the filter_pdf function to remain the page that is most likely to store tax table and delete other pages.
for index in range(list[1],list[0]):
    Utility.filter_pdf(index)

