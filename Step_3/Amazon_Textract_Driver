# This is the Driver module of the Amazon Textract program.
# Author: Guangqi Li <li001122@umn.edu>
# Import the Utility module
import Amazon_Textract_Utility as Utility
# First check whether the tracking csv exists. If not, create one.
Utility.tracking_csv()
# Get the progress of the extraction.
tracking_list = Utility.track_progress()
# Call the extraction functions.
for j in range(tracking_list[1],tracking_list[0]):
    # If you want to extract forms instead of tables, replace the "Utility.Amazon_tesseract_tables(j)" by "Utility.Amazon_tesseract_forms(j)"
    Utility.Amazon_tesseract_tables(j)
