import databases as d
import utils as u

db = d.MeasuresDatabase("simulated_data.txt")
"""
matches = db.getMatches("E4NR6JIJUR", 0)
for m in matches:
	print(m)
"""
print(u.terms("PRGO", "20150421", db))

