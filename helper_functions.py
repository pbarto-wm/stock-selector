import csv
from bs4 import BeautifulSoup
import string
import requests
from config import AZURE_KEY
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def get_all_stocks():

    """this function obtains each stock from the NYSE, cleans it, and puts it in a CSV file.
       the CSV file is put in the current directory
    """
    alpha = list(string.ascii_uppercase)

    symbols = []

    for each in alpha:
        url = "http://eoddata.com/stocklist/NYSE/{}.html".format(each)
        resp = requests.get(url)
        site = resp.content
        soup = BeautifulSoup(site, "html.parser")
        table = soup.find("table", {"class":"quotes"})
        for row in table.findAll("tr")[1:]:
            symbols.append(row.findAll("td")[0].text.rstrip())

    symbols_cleaned = []

    for each in symbols:
        each = each.replace(".","-").split("-")[0]
        if each not in symbols_cleaned:
            symbols_cleaned.append(each)

    with open("stocks.csv", "w") as file:
        wr = csv.writer(file, quoting = csv.QUOTE_ALL)
        wr.writerow(symbols_cleaned)

def return_stocks():
    """returns a list from all the stocks in CSV file 
    """
    with open("./stocks.csv", "r", newline="") as file:
        reader = csv.reader(file)
        data = list(reader)[0]

    return data

def chunks(l, n):
    """
        takes in a list, and creates n chunks. we do this because the IEX API doesn't like requests more than 99
        """
    for i in range(0, len(l), n):
        yield l[i:i+n]

def send_email(destination, stocks):

    """this function takes in a destination (email address to send it to) and the list of stocks
       using Azure's sendGrid api, we send an email of the list of stocks to the destination email
    """

    html = html_formatter(stocks)

    message = Mail(
        from_email="phildbarto@gmail.com",
        to_emails=destination,
        subject="Stocks that pass the Benjamin Graham fundamentals Test",
        html_content=html)

    try:
        sg = SendGridAPIClient(AZURE_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

def html_formatter(stocks):
    ###this just formats the HTML so I don't have to do it in the send_email function
    string = """<p>Below is the list of stocks that pass the Benjamin Graham Fundamentals test.</p> <p>Happy Investing!</p>
                <table style = "width:235px;">
                <tbody>
            """
    for stock in stocks:
        string += '<tr><td style="width: 53px;">'+str(stock)+"</td>"
        string += '<td style="width: 186px;"><a href="https://finance.yahoo.com/quote/{}">https://finance.yahoo.com/quote/{}</a></td></tr>'.format(stock, stock)

    string += "</tbody></table>"
    return string