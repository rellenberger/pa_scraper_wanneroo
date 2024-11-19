import requests
import re
import sqlite3

base_url = 'https://yoursay.wanneroo.wa.gov.au/ccm/the_hive_projects/tools/the_hive_projects_list/load_more/2693?page='
page_num = 0
more_to_load = True
data = []

while more_to_load == True:

    response = requests.get(base_url+str(page_num))
    
    #if response is not ok, or nearly empty text returned, quit loop
    if not response.ok or len(response.text)<100:
        more_to_load = False

    #for this pages results, append the required info to our data list as a tuple
    list = response.json()['result']
    for project in list:
        #only append data if we can find a DA tag in the project description
        if re.search(r".+\((DA.+)\)", project['projectDescription'])!=None:
            data.append((project['projectDescription'] if re.search(r".+\((DA.+)\)", project['projectDescription'])==None else re.search(r".+\((DA.+)\)", project['projectDescription']).group(1),
                        project['projectName'] if re.search(r".+( at | – )([^()]+)", project['projectName'])==None else re.search(r".+( at | – )([^()]+)", project['projectName']).group(2),
                        project['projectDescription'],
                        project['projectPath'],
            )
            )

    #if no more to load, quit loop
    if response.json()['moreToLoad'] != True:
        more_to_load = False

    #if more to load, increment page number    
    page_num += 1


if data != []:
    con = sqlite3.connect('data.sqlite')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS data (council_reference TEXT PRIMARY KEY NOT NULL, address TEXT NOT NULL, description TEXT NOT NULL, info_url TEXT NOT NULL, date_scraped DATE DEFAULT CURRENT_DATE)')
    cur.executemany('INSERT OR REPLACE INTO data (council_reference, address, description, info_url) VALUES(?, ?, ?, ?)', data)
    con.commit()