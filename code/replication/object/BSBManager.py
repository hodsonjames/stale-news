from multiprocessing import Process, Queue, Pipe
from Article import Article as Story
import csv
import os
from LL import *
import heapq

def processor(q, simObject, temp_save):
	"""
	Worker that will process a que of stories.
	"""
	with open(temp_save, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(['DATE_EST', 'STORY_ID', 'TICKER', 'STORY_LENGTH', 'CLOSEST_ID', 'SECOND_CLOSEST_ID', 'CLOSEST_SCORE', 'TOTAL_OVERLAP', 'IS_OLD', 'IS_REPRINT', 'IS_RECOMB'])
		companies = dict()
		while True:
			story, ticker = q.get(block=True)
			if ticker == "ad mortem":
				break
			if ticker not in companies:
				companies[ticker] = myLinkedList()
			p = simObject.staleNewsProcedure(ticker, story, companies[ticker])
			writer.writerow(p)


def supplier(pipe, Story, simObject):
	"""
	Worker that cleanes stories.
	"""
	while True:
		et = pipe.recv()
		if et == "ad mortem":
			break
		else:
			s = Story(et)
			simObject.preprocessing(s)
			pipe.send(s)


def merge(endlocation, temp_files):
	"""
	Merges together sorted files into one laregr file.  Deletes the temo_files
	after the megre.
	"""
	files = [open(file, 'r') for file in temp_files]
	filedata = {i: csv.reader(file, delimiter=',') for i, file in enumerate(files)}
	temp = list()
	for i in range(len(temp_files)):
		next(filedata[i])
		newline = next(filedata[i])
		heapq.heappush(temp, (newline[0], i, newline))
	with open(endlocation, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile, delimiter=',')
		writer.writerow(['DATE_EST', 'STORY_ID', 'TICKER', 'STORY_LENGTH', 'CLOSEST_ID', 'SECOND_CLOSEST_ID', 'CLOSEST_SCORE', 'TOTAL_OVERLAP', 'IS_OLD', 'IS_REPRINT', 'IS_RECOMB'])
		while temp:
			_, f, data = heapq.heappop(temp)
			writer.writerow(data)
			try:
				newline = next(filedata[f])
			except StopIteration:
				newline = None
			if newline:
				heapq.heappush(temp, (newline[0], f, newline))
	[file.close() for file in files]
	[os.remove(file) for file in temp_files]


def worker_init(count, t, simObject=None):
	"""
	starts up the worker processes.
	"""
	workers, worker_processes = list(), list()
	for i in range(count):
		if t == "supplier":
			a, b = Pipe()
			worker = Process(target=supplier, args=((b), (Story), (simObject)))
			worker.start()
			workers.append(a)
			worker_processes.append(worker)
		elif t == "processor":
			temp_save = f"temp_file_{i}.csv"
			queue = Queue()
			worker = Process(target=processor, args=((queue), (simObject), (temp_save)))
			worker_processes.append(worker)
			worker.start()
			workers.append(queue)
	return workers, worker_processes
