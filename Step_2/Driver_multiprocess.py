# This is the driver module with multiprocessing function.
# I am using the multiprocessing module to realize parallel processes.
from multiprocessing import Pool
import Utility
import Inputs

print(Inputs.year)
# Firstly, check whether we have a tracking csv or not. If not, the function will create one.
Utility.tracking_csv()
# Get the list of the function. This list contains two elements.
# The first element is the total number of companies in this year.
# The second element is the company which is under extraction or needed to be extracted.
list = Utility.track_progress()
# Set the number of processes
n_process = 2
# Then, use the Pool class to set parallel processes.
# One process works on one full annual report.
for index in range(list[1],list[0],n_process):
    p = Pool(n_process)
    for j in range(n_process):
        p.apply_async(Utility.filter_pdf,args=(index+j,))
    p.close()
    p.join()
