# Gather command line arguments
import optparse

usage = "%prog [options] sample_barcode data_file sample_images .."
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
parser.add_option("-l", "--twitter_lookup", dest="twitter_lookup",
                  help="Directory containing credentials for twitter etc",
                  default="test_data/twitter_lookup.csv")
parser.add_option("-e", "--experiment_count", dest="experiment_count",
                  help="The experiment number",
                  default=7777)

(options, args) = parser.parse_args()


# Add a syslog handler for logging to graylog
import logging
import logging.handlers as handlers

logging.basicConfig(level=logging.DEBUG)
syslog = handlers.SysLogHandler(address=(options.syslog, options.syslog_port))
syslog.setFormatter(logging.Formatter('ProjectMTwitter:%(message)s'))
syslog.setLevel(logging.DEBUG)
logging.getLogger('').addHandler(syslog)
logging.info("Completed syslog setup")
logging.getLogger('requests_oauthlib').setLevel(logging.INFO)
logging.getLogger('requests').setLevel(logging.INFO)
logging.getLogger('oauthlib').setLevel(logging.INFO)


# Sort out twitter credentials
logging.info("Sort out twitter credentials")
import os
import twitter
import json

creds = None
creds_path = os.path.join(options.credential_dir,'credentials.json')
logging.info("Path to creds is '%s'" % (creds_path))

with open(creds_path) as json_data:
    creds = json.load(json_data)

logging.info("credentials loaded")
api = twitter.Api(consumer_key=creds['consumer_key'],
                  consumer_secret=creds['consumer_secret'],
                  access_token_key=creds['access_token'],
                  access_token_secret=creds['access_token_secret'])

logging.info("verifying credentials")
logging.debug(api.VerifyCredentials())


# Connect to DB
# logging.info("Connecting to ISPyB")
# import mysql.connector

# conn = mysql.connector.connect(user=creds['ispyb_user'],
#                                password=creds['ispyb_pw'],
#                                host=creds['ispyb_host'],
#                                database=creds['ispyb_db'],
#                                port=int(creds['ispyb_port']))

# if conn is not None:
#     conn.autocommit=True

# cursor = conn.cursor(dictionary=True, buffered=True)

# # Retrieve the school name for the given sample barcode
# barcode = args[0]
# query = """SELECT lab.name
# FROM Laboratory lab
#   INNER JOIN Person p on p.laboratoryId = lab.laboratoryId
#   INNER JOIN LabContact lc on lc.personId = p.personId
#   INNER JOIN Shipping s on s.returnLabContactId = lc.labContactId
#   INNER JOIN Dewar d on d.shippingId = s.shippingId
#   INNER JOIN Container c on c.dewarId = d.dewarId
#   INNER JOIN BLSample bls on bls.containerId = c.containerId
# WHERE
#   bls.name = %s""" % (barcode)

# cursor.execute(query)

# rs = cursor.fetchone()
# if len(rs) == 0:
#     logging.warn("Couldn't find a school for sample barcode %s" % barcode)

# school = rs['name']
# logging.info("School identified as '%s'" % school)
# cursor.close()
# conn.close()
school = args[0]

# Look-up the twitter handle for the school 
from numpy import genfromtxt
logging.info("Loading twitter lookup table from '%s'" % options.twitter_lookup)
tl = genfromtxt(options.twitter_lookup, delimiter=',', dtype=None)

names = [i[0].decode('UTF-8') for i in tl]
matches = tl[[school.lower() in name.lower() for name in names]]
school_name = school.strip()
logging.debug("School name is '%s'" % (school_name))

twitter_handle = school_name
if len(matches) > 0:
    match = matches[0][1].decode('UTF-8')
    twitter_handle = match
logging.info("Twitter handle identified as '%s'" % twitter_handle)


## Get the experiment count
#import os, stat
#
#experiment_count = {'count':0} 
#try:        
#    with open(options.experiment_count) as count_data:
#        experiment_count = json.load(count_data)
#except:
#    pass
#
#experiment_count['count'] += 1
#
#with open(options.experiment_count, 'w') as count_data:
#    json.dump(experiment_count, count_data)
#
## make sure the file is writable to the next user
#try:
#    os.chmod(options.experiment_count, stat.S_IRWXO | stat.S_IRWXG | stat.S_IRWXU)
#except:
#    # if we dont own it then this cant happen so not an issue.
#    pass

experiment_number = int(options.experiment_count)  # experiment_count['count']
logging.info("experiment_number is %i" % experiment_number)


# Load data
import numpy as np

data_file_name = args[1]
logging.info("loading data file '%s'" % (data_file_name))
a = np.loadtxt(data_file_name, unpack=True)


# Plot images to temp file
import pylab as pl
import matplotlib.pyplot as plt

fig1_file_name = os.path.join(options.temp_dir, 'pic1.png')
logging.info("Preparing '%s'" % (fig1_file_name))
plt.close()
plt.plot(a[0],a[1])
plt.title('Experiment %i: for %s' % (experiment_number, school_name))
plt.ylabel('Intensity')
plt.xlabel(r'$2\theta$(degrees)')
logging.info("Saving '%s'" % (fig1_file_name))
pl.savefig(fig1_file_name, bbox_inches='tight')


# Compile images to tweet
image_list = [fig1_file_name]

for i in range(2, len(args)):
    image_list.append(args[i])

logging.info("Image list before checks is : " + str(image_list))

image_list = [file_name for file_name in image_list if os.path.exists(file_name)]
logging.info("Image list after checks is : " + str(image_list))


# Post the update to twitter
logging.info("Posting update to twitter")
post_string = 'Experiment %i completed for %s_test as part of @DLSProjectM_test on the #I11 beamline @DiamondLightSou_test' 
if "Ysgol Glan Clwyd" in school:
    post_string = 'Arbrawf %i cwblhau ar gyfer %s_test fel rhan o @DLSProjectM_test ar y beamline #I11 @DiamondLightSou_test'

status = api.PostUpdate(post_string % (experiment_number, twitter_handle),
                        media=image_list)


