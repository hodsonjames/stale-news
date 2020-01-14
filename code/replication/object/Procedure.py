from Similarity import *
from BSBManager import *
from Article import Article
import time
import glob
import sys
import os
from multiprocessing import cpu_count
import csv
from ETUtils import *

def procedure(startlocation = 'data', endlocation='export_dataframe.csv', simtest=CosineSimilarity(), worker_count=-1):
	'''
	Performs the procedure for the specified amount of articles. Uses 
	all nml files from startlocation, and exports a csv file at endlocation.

	To paralyze this process, some workers are used to process the articles, 
	and some are used to compare the similarity.  The XML text is sent to all 
	the different suppliers workers then are retrieved in order, this preserves 
	the chronological order.  These are all then sent to the appropriate workers 
	witch process the article in the order that they were received.  This results 
	in the algorithm beinng able to utalize multiple threades while still 
	processing the articles in the appropriate order.
	'''

	if worker_count < 0:
		worker_count += cpu_count() + 1

	# Empirically found that using more threades than were available and allowing 
	# the scheduler to decide which would run decreased run time, belied to be caused 
	# by idle workers. 
	worker_count = int(worker_count * 3)
	
	location = sorted(glob.glob(os.path.join(startlocation,'*.nml')))
	companies = dict()
	suppliers, supplier_processes = worker_init(worker_count, "supplier", simtest)
	processors, processor_processes = worker_init(worker_count, "processor", simtest)
	for f in location:
		print("File processing...",f)
		xtg = textGetter(f)
		
		for supplier in suppliers: # Send out the first batch of articles
			try:
				et = next(xtg)
			except StopIteration:
				break
			supplier.send(et)

		checks, load = 0, 0
		while checks < len(suppliers): # Makes sure to get back all articles before moving on
			for supplier in suppliers:
				if checks >= len(suppliers):
					break

				story = supplier.recv() # Gets back an article in apropriate oreder by waiting

				try:
					et = next(xtg)
					supplier.send(et)
				except StopIteration:
					checks += 1 
				
				if not story.bad and not (story.tickers == []):
					for ticker in story.tickers:
						if '.' in ticker:
							continue
						if ticker not in companies:
							companies[ticker] = load #Assings a ticker to specific worker
							load = (load + 1) % worker_count
						processors[companies[ticker]].put((story, ticker))

	[a.send("ad mortem") for a in suppliers]
	[w.join() for w in supplier_processes]

	[q.put((None, "ad mortem")) for q in processors]
	[w.join() for w in processor_processes]

	merge(endlocation, [f"temp_file_{i}.csv" for i in range(worker_count)])
	print('Procedure finished')

if __name__ == '__main__':
	start = time.time()
	if len(sys.argv) == 3:
		procedure(sys.argv[1], sys.argv[2])
		print(time.time() - start)
	else:
		print(time.time() - start)
		sys.exit(1)
