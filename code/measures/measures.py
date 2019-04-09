def intersection(lst1, lst2): 
    """returns the intersection between two lists"""
    if (lst1 == None or lst2 == None):
        return []
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3 

def similaritytest(orig, B):
    """returns a similarity score between stemmed article orig and a stemmed article (text)"""
    return len(intersection(orig.textWords, B.textWords)) / len(orig.textWords)