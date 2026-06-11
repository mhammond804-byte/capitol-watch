import json
data = json.load(open("/Users/michaelhammond/Desktop/capitol-watch/bill-analysis.json"))
print("Cache size: {}".format(len(data)))
