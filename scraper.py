import mysql.connector
import requests
from bs4 import BeautifulSoup
import numpy as np
import smtplib, ssl
import os
from apscheduler.schedulers.blocking import BlockingScheduler



# Contains previous list of cars

# Connecting to SQL Database
mydb = mysql.connector.connect(host="localhost", port="8889", user="testuser", passwd="testuser", database="used_cars")
cursor = mydb.cursor(buffered=True)


print('hi')
# Scrapes Craigslist 
def get_links():
    URL = 'https://sfbay.craigslist.org/search/cta?condition=60'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.90 Safari/537.36'}
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    links = soup.find_all('a', class_="result-title hdrlnk")
    currList = []
    for link in links:
        currLink = link["href"]
        dbLink = link["href"].translate(str.maketrans({":": r"", "/":r""}))
        sql = "SELECT * FROM all_links WHERE link = '%s'" % (dbLink)
        cursor.execute(sql)
        print(cursor.rowcount)
        if(cursor.rowcount == 0):
            currList.append(link['href'])
            sql = "INSERT INTO all_links VALUES ('%s')" % (dbLink)
            cursor.execute(sql) 
            mydb.commit()
    return currList

def send_email(list_to_send):
    email = os.environ.get('EMAIL')

    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "car.scrape1@gmail.com"
    password = os.environ.get('PASSWORD')

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)
        # TODO: Send email here
        subject = "Car Links"
        if(len(list_to_send) == 0):
            body = "There are no new listings"
        else:
            body = ""
            for link in list_to_send:
                body = body + "\n" + link

        msg = f'Subject: {subject}\n\n{body}'
        server.sendmail(email, email, msg)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()

def run_methods():
    return send_email(get_links())

scheduler = BlockingScheduler()
scheduler.add_job(run_methods, 'interval', seconds=30)
scheduler.start()
