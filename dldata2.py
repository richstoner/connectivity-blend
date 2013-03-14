# -*- coding: utf-8 -*-
import os, urllib
#import os
#import urllib
import workerpool

from BeautifulSoup import BeautifulStoneSoup

class DownloadJob(workerpool.Job):
    "Job for downloading a given URL."
    def __init__(self, url):
        self.url = url # The url we'll need to download when the job runs
    def run(self):

        save_to = 'rawdata/' + os.path.basename(self.url).split('?')[0]+'.xpz'
        print(save_to)
        urllib.urlretrieve(self.url, save_to)

# String to generate below XML file:
# http://api.brain-map.org/api/v2/data/query.xml?criteria=model::SectionDataSet,rma::criteria,products%5Bid$eq5%5D,rma::include,rma::options[num_rows$eq1000],specimen(injections(primary_injection_structure,structure))

soup = BeautifulStoneSoup(open("all-conn.xml").read())

# need to make rawdata folder 
if not os.path.exists(os.curdir + '/rawdata'):
    os.makedirs('rawdata')
else:
    print 'raw data dir ready'

urls = []

print len(soup.findAll("section-data-set"))

# For each connectivity experiment, we check to see whether it was marked "failed"
for ds in soup.findAll("section-data-set"):
    experimentNumber = int(ds.id.text)
    # print experimentNumber

    if ds.failed.text == "true":
        print "skipping",  experimentNumber, "marked as failed."
        continue

    newFilePath = os.path.join("rawdata", str(experimentNumber) + ".xpz")
    url  = '''http://connectivity.brain-map.org/grid_data/v1/visualize/%i?atlas=378''' % experimentNumber
    urls.append(url)

# Initialize a pool, 5 threads in this case
pool = workerpool.WorkerPool(size=10)

# Loop over urls.txt and create a job to download the URL on each line
for url in urls:
    job = DownloadJob(url.strip())
    pool.put(job)





# Send shutdown jobs to all threads, and wait until all the jobs have been completed
pool.shutdown()

