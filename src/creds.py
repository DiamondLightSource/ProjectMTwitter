# Convinience script to create a credentials.json file

import json

creds = {'consumer_key':'XXX',
         'consumer_secret':'XXX',
         'access_token':'XXX',
         'access_token_secret':'XXX'
         }

with open('credentials.json', 'w') as fp:
    json.dump(creds, fp)
