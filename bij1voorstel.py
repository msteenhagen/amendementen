#!/usr/local/bin/python3
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
import json
import sys
import credentials 

# Make a separate file credentials.py, containing the following information:
# 	access_token = 'sEcreTandLongAcceSStoken'
# 	room_id = '!ROOMiDeNTiFIER:matrix.example.org'
# 	url = 'https://matrix.example.org/_matrix/client/r0/rooms/' + room_id + '/send/m.room.message'

pd.set_option('display.max_colwidth', None)

access_token = credentials.access_token
room_id = credentials.room_id
url = credentials.url

def matrix_message(message):
	headers = {
			}
	params = {
			    'access_token': access_token,
			}
	json_data = {
			    'msgtype':'m.text','body':message,
			}
	response = requests.post(
			        url,
			        params=params,
			        headers=headers,
			        json=json_data,
			)

# Put the table from the website in a dataframe
URL = "https://bij1.org/programma-voorstellen/"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
table = soup.figure.find('table')
data = []
for row in table.find_all('tr'):
    row_data = []
    for cell in row.find_all('td'):
        row_data.append(cell.text)
    data.append(row_data)

# WEB DATA
df = pd.DataFrame(data)
df.columns = df.iloc[0]
df = df[1:]

# LOCAL DATA (This is too sloppy, you need to have a csv with the right header row already):
# Nummer, Naam,Pagina,Regelnummers,Handeling,Betreft de tekst,Toevoegen / wijzigen in,Toelichting,Samenvatting
df_old = pd.read_csv('voorstellen.csv', header=None)
df_old.columns = df_old.iloc[0]
df_old = df_old[1:]

# DIFFERENCE (boolean series)
diff = df.Samenvatting.isin(df_old.Samenvatting)

def fetch_value(df, ix, label):
	return df.loc[[ix]][label].to_string(index=False)

f = open("index.html", "w").close()
with open('head.html','r') as headfile, open('index.html','a') as f:
    for line in headfile:
             f.write(line)
f.close()

counter = 0
found_new = False
for row in diff:
	if row == False:
		ix = counter + 1
		found_new = True
		A = fetch_value(df, ix, "Naam")
		B = fetch_value(df, ix, "Handeling")
		C = fetch_value(df, ix, "Samenvatting")
		D = fetch_value(df, ix, "Betreft de tekst")
		E = fetch_value(df, ix, "Pagina")
		F = fetch_value(df, ix, "Regelnummers")
		G = fetch_value(df, ix, "Toevoegen / wijzigen in")
		H = fetch_value(df, ix, "Toelichting")
		I = fetch_value(df, ix, "Nummer")
		message = '''\

# Voorstel {} 

## {}

Ingediend door {} ({}),

Betreft de tekst: {} (p. {}, regels {})

Voorstel: {}

Toelichting: {}

		'''.format(I, C,  A, B, D, E, F, G, H)

		html_block = '''\

<h1>Voorstel {}</h1> 

<h2>{}</h2>

<p>Ingediend door {} ({}),</p>

<p>Betreft de tekst: {} (p. {}, regels {})</p>

<p>Voorstel: {}</p>

<p>Toelichting: {}</p>

		'''.format(I, C,  A, B, D, E, F, G, H)
		print(message)
		# Gooi dit ook even in de index.html file
		f = open("index.html", "a")
		print(html_block, file=f)
		f.close()
		# matrix_message(message) # uncomment if you want Matrix messages to be broadcast
		df.loc[[counter + 1]].to_csv('voorstellen.csv', mode='a', index=False, header=False)
	counter = counter + 1

if found_new == False:
	print ("No new amendments found")

with open('footer.html','r') as footfile, open('index.html','a') as f:
    for line in footfile:
             f.write(line)
f.close()


#Let's do some stats
df_old = pd.read_csv('voorstellen.csv', header=None )
df_old = df_old[1:]
ranking = '''\
======== INDIENERS RANGORDE ========

{}
'''.format(df_old[1].value_counts().to_string())
print(ranking)


