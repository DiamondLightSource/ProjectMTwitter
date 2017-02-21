# Initial prototype work, needs turning into a proper process.

import twitter

import json

creds = None
with open('credentials.json') as json_data:
    creds = json.load(json_data)
    #print(creds)

api = twitter.Api(consumer_key=creds['consumer_key'],
                  consumer_secret=creds['consumer_secret'],
                  access_token_key=creds['access_token'],
                  access_token_secret=creds['access_token_secret'])

print(api.VerifyCredentials())


import numpy as np

a = np.loadtxt('412940-mythen_summed.dat', unpack=True)

import pylab as pl
import matplotlib.pyplot as plt
plt.close()
plt.plot(a[0][100:7000],a[1][100:7000])
plt.ylabel('Intensity')
pl.savefig('pic1.png', bbox_inches='tight')

plt.close()
plt.plot(a[0][100:1000],a[1][100:1000])
plt.ylabel('Intensity')
pl.savefig('pic2.png', bbox_inches='tight')

plt.close()
plt.plot(a[0][1000:2000],a[1][1000:2000])
plt.ylabel('Intensity')
pl.savefig('pic3.png', bbox_inches='tight')

plt.close()
plt.plot(a[0][2000:3000],a[1][2000:3000])
plt.ylabel('Intensity')
pl.savefig('pic4.png', bbox_inches='tight')

status = api.PostUpdate('Data collection test 1/... for @basham_mark',
                        media=['pic1.png',
                               'pic2.png',
                               'pic3.png',
                               'pic4.png'])


