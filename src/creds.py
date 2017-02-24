# Convinience script to create a credentials.json file

import json



creds = {'consumer_key':'XXX',
         'consumer_secret':'XXX',
         'access_token':'XXX',
         'access_token_secret':'XXX',
         'ispyb_user':'XXX',
         'ispyb_pw':'XXX',
         'ispyb_db':'XXX',
         'ispyb_host':'XXX',
         'ispyb_port':'XXX'
         }

for key in creds.keys():
    creds[key] = input("Please enter %s : " % (key))

with open('credentials.json', 'w') as fp:
    json.dump(creds, fp)
