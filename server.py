import http.server
import socketserver
import json

import requests

PORT = 7272
Handler = http.server.SimpleHTTPRequestHandler

access_token = "a9de8862e25eaacccd9095bbf920ba8f47c8269a"

headers = {'Host':'api-ssl.bitly.com', 'Authorization':'Bearer '+access_token}

#provides user information including the user's default group
user_address = "https://api-ssl.bitly.com/v4/user"
user_content = requests.get(user_address, headers=headers)

print(user_content.status_code)
user_json = user_content.json()
#print(user_json)

group_guid = user_json["default_group_guid"]


#provides paged information about the Bitlinks for a provided group
bitlink_param = {"size": 50}
bitlink_address = "https://api-ssl.bitly.com/v4/groups/"+group_guid+"/bitlinks"
bitlink_content = requests.get(bitlink_address, headers=headers, params=bitlink_param)

print(bitlink_content.status_code)
bitlink_json = bitlink_content.json()
#print(bitlink_json)

bitlink = bitlink_json["links"][0]["id"]



#provides the number of user clicks, broken down by country, for a provided Bitlink
country_param = {"unit": "day", "units":-1}
n_clicks = 0

country_address = "https://api-ssl.bitly.com/v4/bitlinks/"+bitlink+"/countries"
country_content = requests.get(country_address, headers=headers, params=country_param)

print(country_content.status_code)
country_json = country_content.json()
#print(country_json)

n_metrics = len(country_json["metrics"])
#print(n_metrics)

#get total amount of clicks
total_clicks = 0
for i in range(0,n_metrics-1): 
    #print(country_json["metrics"][i]["clicks"])
    total_clicks = total_clicks + country_json["metrics"][i]["clicks"]

#associate average with respective country
average_click = {}
for j in range(0,n_metrics):
    country = country_json["metrics"][j]["value"]
    click = country_json["metrics"][j]["clicks"]
    average_click[country] = click / total_clicks
print(average_click)


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()