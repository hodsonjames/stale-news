from timeit import default_timer as timer
start = timer()

import datetime
import xml.etree.ElementTree as ET
from dateutil import parser
import pandas as pd
import numpy as np

import sys
import os
import argparse
import csv

sys.path.append("../measures")
from measure_constants import MeasureConstants
from article import Article
from bow_similarity import BOWSimilarity
from cosine_similarity import CosineSimilarity

sim = BOWSimilarity()

def filter_old_articles(company_article_map, curr_article, k_hours=sim.measure_const.NUM_HOURS):
    """
    Check the set of articles mapped to curr_article.company, and 
    filter out articles that are at least k_hours older than curr_article. 
    
    Arguments:
        curr_article: An Article object, used to compare time stamps with all other
            articles in company_article_map[curr_article.company]. 
        k_hours: An int, default 72. All articles in company_article_map[curr_article.company] 
            that have at least k_hours elapsed time between that article and 
            curr_article.timestamp will be filtered from the map.
            
    Returns:
        company_article_set: A new set to map to curr_article.company, with 
            old articles filtered out, with "old" specified as k_hours.
    """
    
    k_seconds = k_hours * 60 * 60
    curr_company = curr_article.company
    
    company_article_set = company_article_map.get(curr_company, False)
    
    if company_article_set == False:
        return set()
    
    articles_to_remove = {article for article in company_article_set 
                         if curr_article.elapsed_time_between(article) >= k_seconds}
    company_article_set.difference_update(articles_to_remove)
    
    return company_article_set  

# 

############### CHANGE THE NAME OF THIS ######################
def create_article_map(directory_path, output_csv_name, k_hours=sim.measure_const.NUM_HOURS):
    """
    Main parsing function. Takes in a directory containing .nml files
    and returns a dictionary with keys that correspond to company symbols,
    and values that are sets of Article objects whose articles are about
    that company. 
    
    Arguments:
        directory_path: A string representing the filepath for directory containing .nml files to parse. 
        output_csv_name: Name of .csv file to output with articles and similarity
            information. 
        k_hours: Argument passed in to filter_old_articles(). Determines
            article filtering. Default is 72, so articles mapped to any
            given company which are at least 72 hours older than the
            current article being parsed will be filtered from the map.
    
    Returns:
        company_article_map: Map from companies to sets of Articles about
            those companies. The set for each company will contain articles that
            were published within k_hours hours of each other. 
    """
    company_article_map = {}
    curr_file_str = ""
    header_df = pd.DataFrame(columns=["company", "headline", "time", "id"
                                     "old_score", "closest_neighbor", "is_reprint", "is_recombination"])
    header_df.to_csv(output_csv_name, index = False)

    f = open(output_csv_name, "a")
    csv_writer = csv.writer(f)

    directory = os.fsencode(directory_path)
    
    nml_files = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if ".nml" not in filename:
            continue
        else:
            nml_files.append(directory_path + filename)


    for filename in sorted(nml_files):
        with open(filename) as myfile:
            for next_line in myfile:
                curr_file_str += next_line
                if next_line == "</doc>\n":

                    xml_elem = ET.fromstring(curr_file_str)
                    company = xml_elem.find(".//djn-company-sig")
                    if company is None:
                        curr_file_str = ""
                        continue

                    md5_hash = xml_elem.attrib['md5']
                    timestamp = xml_elem.find(".//djn-mdata").attrib['display-date']
                    headline = xml_elem.find(".//headline").text.lstrip()
                    all_text = xml_elem.find(".//text")
                    article_text = "".join(all_text.itertext())
                    text_stemmed_filtered = sim.stem_and_filter(article_text)
                    for c in company:
                        if c.attrib.get('about', False) != 'Y':
                            curr_file_str = ""
                            continue
                        company = c.text

                        new_article = Article(company, timestamp, headline, text_stemmed_filtered, md5_hash)
                        company_articles = filter_old_articles(company_article_map, new_article, k_hours)
                        
                        if len(company_articles) == 0:
                            company_articles.add(new_article)
                            company_article_map[company] = company_articles
                            curr_file_str = ""
                            continue
                        else:
                            old, closest_neighbor = sim.compute_sim_measure(new_article, company_articles)
                            new_row = [new_article.company, new_article.headline, new_article.timestamp, md5_hash
                                      old, closest_neighbor, sim.is_reprint(old, closest_neighbor),
                                      sim.is_recombination(old, closest_neighbor)]
                            csv_writer.writerow(new_row)

                            company_articles.add(new_article)
                            company_article_map[company] = company_articles
                            
                        curr_file_str = ""
    
    f.close()
    return company_article_map


# Running parser from command line

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("dir_path", help = "filepath to directory containing .nml files to be parsed")
arg_parser.add_argument("csv_name", help = "name of .csv file you want to output")
if len(sys.argv) < 1:
    arg_parser.print_help(sys.stderr)
args = arg_parser.parse_args()
article_map = create_article_map(args.dir_path, args.csv_name)
print("Parsing done!")

end = timer()
print(end - start)