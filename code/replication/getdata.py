import xml.etree.ElementTree as ET
import re

#get data (but it needs to be cleaned)
with open("../data/data.nml") as f:
    xml = f.read()

#clean
q = re.sub(r"(<\?xml[^>]+\?>)", "", xml)
q = re.sub(r"<!DOCTYPE[^>]+>", "", q)
q = "<root>" + q + "</root>"

#create root
root = ET.fromstring(q)

#show some data (2 articles)
for i in range(2):
    text = ""
    for element in root[i][0][1][1]: #likely slow, fix later
        text += element.text
    print(text)