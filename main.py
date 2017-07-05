__author__ = "Richard O'Dwyer"
__email__ = "richard@richard.do"
__license__ = "None"

import re
from operator import itemgetter
import datetime
import matplotlib.pyplot as plt; plt.rcdefaults()
from datetime import timedelta
from collections import OrderedDict
import pandas as pd

IVAL=5  #interval in minutes
ROLL=5  #how many intervals to roll

def process_log(log):
    requests = get_requests(log)
    #files = get_files(requests)
    #totals = file_occur(files)
    totals = get_times(requests)
    return totals

def get_requests(f):
    log_line = f.read()
    pat = (r''
           '(\d+.\d+.\d+.\d+)\s-\s-\s' #IP address
           '\[(.+)\]\s' #datetime
           '"GET\s(.+)\s\w+/.+"\s' #requested file
           '(\d+)\s' #status
           '(\d+)\s' #bandwidth
           '"(.+)"\s' #referrer
           '"(.+)"' #user agent
        )
    requests = find(pat, log_line)
    return requests

def find(pat, text):
    match = re.findall(pat, text)
    if match:
        return match
    return False

def get_times(requests):
    """
    return list of times
    """
    timelist = []
    for req in requests:
        timelist.append(convertStrToDatetime(req[1]))
    return timelist

def convertStrToDatetime(dtstr):
    #03/Jul/2017:09:50:05 +1000
    # we will drop the +1000, so graph will be in UTC
    return datetime.datetime.strptime(dtstr, "%d/%b/%Y:%H:%M:%S +1000")

def generate_graph_dict(times):
    block = timedelta(minutes=IVAL)
    start = times[0]
    graphdict = OrderedDict()
    print start
    for time in times:
        end = start + block
        if(time < end):
            try:
                graphdict[start] += 1
            except:
                graphdict[start] = 1
        else:
            start = end
            print start

    return graphdict
        
def graph(graphdict):
    x = graphdict.keys()
    y = graphdict.values()
    plt.plot(x, y)
    plt.show()

def graphrolling(graphdict):
    #put graphdict into a dataframe
    data = { 'date':graphdict.keys(), 'count':graphdict.values() }
    df = pd.DataFrame(data, columns = ['date', 'count'])
    #print(df)
    df.index = df['date']
    del df['date']
    print df

    #create roll
    dfb = pd.rolling_mean(df, ROLL)
    print dfb

    ax = dfb.plot()
    plt.sca(ax)
    plt.show()

def get_files(requests):
    #get requested files with req
    requested_files = []
    for req in requests:
        # req[2] for req file match, change to
        # data you want to count totals
        requested_files.append(req[2])
    return requested_files

def file_occur(files):
    # file occurrences in requested files
    d = {}
    for file in files:
        d[file] = d.get(file,0)+1
    return d

if __name__ == '__main__':

    #nginx access log, standard format
    log_file = open('access.log', 'r')

    # return dict of files and total requests
    times = process_log(log_file)
    # sort them by total requests descending
    #sorted_by_count = sorted(urls_with_counts.items(), key=itemgetter(1), reverse=True)
    #print(times)
    gd = generate_graph_dict(times)
    for k,v in gd.items():
        if(v > 0):
            print str(k) + " " + str(v)
            #pass
    graph(gd)
    graphrolling(gd)
