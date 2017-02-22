# Gather command line arguments
import optparse

usage = "%prog [options] sample_barcode data_file"
version = "%prog 0.1"
parser = optparse.OptionParser(usage=usage, version=version)
parser.add_option("-t", "--tmp", dest="temp_dir",
                  help="Store intermediate files in a temp directory.",
                  default="/tmp/")
parser.add_option("-s", "--syslog", dest="syslog",
                  help="Location of syslog server", default='localhost')
parser.add_option("-p", "--syslog_port", dest="syslog_port",
                  help="Port to connect to syslog server on", default=514)
parser.add_option("-c", "--credentials", dest="credential_dir",
                  help="Directory containing credentials for twitter etc", default="creds")

(options, args) = parser.parse_args()


# Add a syslog handler for logging to graylog
import logging
import logging.handlers as handlers

logging.basicConfig(level=logging.DEBUG)
syslog = handlers.SysLogHandler(address=(options.syslog, options.syslog_port))
syslog.setFormatter(logging.Formatter('ProjectMTwitter:%(message)s'))
syslog.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(syslog)
logging.debug("Completed syslog setup")


# Sort out twitter credentials
logging.debug("Sort out twitter credentials")
import os
import twitter
import json

creds = None
creds_path = os.path.join(options.credential_dir,'credentials.json')
logging.debug("Path to creds is '%s'" % (creds_path))

with open(creds_path) as json_data:
    creds = json.load(json_data)

logging.debug("credentials loaded")
api = twitter.Api(consumer_key=creds['consumer_key'],
                  consumer_secret=creds['consumer_secret'],
                  access_token_key=creds['access_token'],
                  access_token_secret=creds['access_token_secret'])

logging.debug("verifying credentials")
logging.debug(api.VerifyCredentials())


# Load data
import numpy as np

data_file_name = args[1]
logging.debug("loading data file '%s'" % (data_file_name))
a = np.loadtxt(data_file_name, unpack=True)


# Plot images to temp file
import pylab as pl
import matplotlib.pyplot as plt

fig1_file_name = os.path.join(options.temp_dir, 'pic1.png')
logging.debug("Preparing '%s'" % (fig1_file_name))
plt.close()
plt.plot(a[0][100:7000],a[1][100:7000])
plt.ylabel('Intensity')
logging.debug("Saving '%s'" % (fig1_file_name))
pl.savefig(fig1_file_name, bbox_inches='tight')

fig2_file_name = os.path.join(options.temp_dir, 'pic2.png')
logging.debug("Preparing '%s'" % (fig2_file_name))
plt.close()
plt.plot(a[0][100:1000],a[1][100:1000])
plt.ylabel('Intensity')
logging.debug("Saving '%s'" % (fig2_file_name))
pl.savefig(fig2_file_name, bbox_inches='tight')

fig3_file_name = os.path.join(options.temp_dir, 'pic3.png')
logging.debug("Preparing '%s'" % (fig3_file_name))
plt.close()
plt.plot(a[0][1000:2000],a[1][1000:2000])
plt.ylabel('Intensity')
logging.debug("Saving '%s'" % (fig3_file_name))
pl.savefig(fig3_file_name, bbox_inches='tight')

fig4_file_name = os.path.join(options.temp_dir, 'pic4.png')
logging.debug("Preparing '%s'" % (fig4_file_name))
plt.close()
plt.plot(a[0][2000:3000],a[1][2000:3000])
plt.ylabel('Intensity')
logging.debug("Saving '%s'" % (fig4_file_name))
pl.savefig(fig4_file_name, bbox_inches='tight')


# Post the update to twitter
logging.debug("Posting update to twitter")
status = api.PostUpdate('Data collection test 1/... for @basham_mark',
                        media=[fig1_file_name,
                               fig2_file_name,
                               fig3_file_name,
                               fig4_file_name])


