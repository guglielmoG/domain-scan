import subprocess
import sys
import csv
from urllib.parse import urlparse
import urllib.request
import os

#database name
customCsv = "results/phantomas.csv"
#phantomas command
command = os.environ.get("PHANTOMAS_PATH", "phantomas")

interesting_metrics = [
    'Domain',
    'requests',
    'httpsRequests',
    'timeToFirstByte',
    'timeToLastByte',
    'httpTrafficCompleted',
    'domContentLoaded',
    'domComplete',
    'timeBackend',
    'timeFrontend',
]

def scan(site):
    #choose the protocol for the connection
    protocol = ""
    if not(site.startswith("https://") or site.startswith("http://")):
        try:
            urllib.request.urlopen("https://"+site, None)
            protocol="https://"
        except:
            urllib.request.urlopen("http://"+site,None)
            protocol="http://"
    #create subprocess that execute phantomas
    site= protocol+site
    print(site)
    proc = subprocess.Popen([command, site],stdout=subprocess.PIPE, shell=True)
    #get the output of phantomas
    out = proc.stdout.read()
    #splits the output to get only the wanted data
    out = str(out).split("\\n\\n")[1][1:].split("\\n*")
    #get the domain name
    domain = urlparse(site).hostname
    if domain.startswith("www"):
        domain = domain[4:]
    #create the full dictionary
    data = {'Domain':domain}
    for line in out:
        parts = line.lstrip().split(":")
        data[parts[0]]=parts[1].lstrip()
    #create a smaller dictionary with only necessary parts
    newData = {}
    for metric in interesting_metrics:
        newData[metric] = data[metric]
    return newData
    return ""

def multiple_scan(csvFile):
    domains = ""
    with open(csvFile,'r') as file:
        domains = file.read().split("\n")[:-1]
    temp_data = []
    for domain in domains:
        temp_data.append(scan(domain.split(",")[0]))
    #write data to a csv file 
    with open(customCsv, 'w') as output_file:
        writer = csv.writer(output_file, lineterminator="\n")
        writer.writerow(interesting_metrics)
        for data in temp_data:
            if data!="":
                writer.writerow(data.values())

def single_scan(url):
    temp_data = scan(url)
    with open(customCsv, 'w') as output_file:
        writer = csv.writer(output_file, lineterminator="\n")
        writer.writerow(interesting_metrics)
        writer.writerow(temp_data.values())


if __name__ == "__main__":
    arg = sys.argv[1]
    if str(arg).endswith(".csv"):
        multiple_scan(arg)
    else:
    	single_scan(arg)
    print("Ended scan")