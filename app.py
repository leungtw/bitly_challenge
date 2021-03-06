from flask import Flask, render_template, redirect, flash, request
import requests
import json
app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')

@app.route('/api', methods=['GET','POST'])
def api():
    access_key = request.form['access_key'] #received from html form
    #print(access_key)

    access_token = access_key
    headers = {'Host':'api-ssl.bitly.com', 'Authorization':'Bearer '+access_token}



    #provides user information including the user's default group
    user_address = "https://api-ssl.bitly.com/v4/user"
    user_content = requests.get(user_address, headers=headers)

    print(user_content.status_code)
    user_json = user_content.json()
    #print(user_json)

    group_guid = user_json["default_group_guid"]



    #provides paged information about the Bitlinks for a provided group
    #retrieve all the bitlinks
    bitlink_param = {"size": 50}
    bitlink_address = "https://api-ssl.bitly.com/v4/groups/"+group_guid+"/bitlinks"
    bitlink_content = requests.get(bitlink_address, headers=headers, params=bitlink_param)

    print(bitlink_content.status_code)
    bitlink_json = bitlink_content.json()
    print("pagination ",bitlink_json)

    n_bitlinks = request.form['n_links']
    if n_bitlinks == 0:
        n_bitlinks = len(bitlink_json["links"])

    n_bitlinks = int(n_bitlinks)

    bitlinks = []
    for x in range(0,n_bitlinks): 
        bitlinks.append(bitlink_json["links"][x]["id"])
    print(bitlinks)


    n_days = request.form['n_days'] #received from html form

    if n_days == 0:
        n_days = 30

    #provides the number of user clicks, broken down by country, for a provided Bitlink
    country_param = {"unit": "day", "units":n_days} #specify past 30 days
    country_dic = {}
    total_clicks = 0

    for x in range(0,n_bitlinks): 
        country_address = "https://api-ssl.bitly.com/v4/bitlinks/"+bitlinks[x]+"/countries"
        country_content = requests.get(country_address, headers=headers, params=country_param)
        country_json = country_content.json()
        print("*",country_json)

        n_metrics = len(country_json["metrics"])
        print(n_metrics)

        for i in range(0,n_metrics): 
            #print(country_json["metrics"][i]["clicks"])
            total_clicks = total_clicks + country_json["metrics"][i]["clicks"]
            country = country_json["metrics"][i]["value"]
            click = country_json["metrics"][i]["clicks"]

            if country not in country_dic:
                country_dic[country] = click
            else:
                country_dic[country] += click

    """
    print(country_dic)
    print(country_content.status_code)
    country_json = country_content.json()
    print("country ",country_json)
    """
    print(country_dic)
    #associate average with respective country
    average_click = {}
    for key, val in country_dic.items():
        country = key
        click = val
        average_click[country] = click / total_clicks
    #print(average_click)

    return render_template('output.html', value=average_click)

if __name__ == '__main__':
    app.run()