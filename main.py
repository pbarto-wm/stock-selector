import csv
import helper_functions
from config import T_ACCESS_KEY
import requests
import json 

def main(email):

    def verify_stock(stock):

        """using the stock passed in, we use the results json object to filter out the necessary conditions
           if it fails any of the conditions, we return false. otherwise we return true
        """
        # earnings
        try:
            if results[stock]["earnings"]["earnings"][0]["actualEPS"] < 0:
                return False

            # financials
            currentAssets = results[stock]["financials"]["financials"][0]["currentAssets"]
            totalDebt = results[stock]["financials"]["financials"][0]["totalDebt"]
            currentDebt = results[stock]["financials"]["financials"][0]["currentDebt"]
            if ((totalDebt / currentAssets) > 1.1 or (currentAssets / currentDebt) < 1.5):
                return False

            ##peRatio
            if (results[stock]["advanced-stats"]["peRatio"] < 0) or (results[stock]["advanced-stats"]["priceToBook"] > 1.2):
                return False

            #dividends 
            if (results[stock]["stats"]["stats"]) < .01:
                return False

            return True

        except (KeyError, TypeError, IndexError):
            return False

    """using the return_stocks method, we obtain the stocks and create batches to send to the IEX Finance API
       using list comprehension, we put the stocks that pass the tests, we send an email to the destination
    """

    results = json.loads("{}")

    all_stocks = list(helper_functions.chunks(

        helper_functions.return_stocks(), 99 
        
    ))

    for count, batch in enumerate(all_stocks):
        
        print("requesting batch {}".format(count))

        response = requests.get(
            "https://sandbox.iexapis.com/stable/stock/market/batch",
            params = {
                "symbols" : str(batch[1:-1]),
                "token" : T_ACCESS_KEY,
                "types" : "quote,earnings,dividends,financials,advanced-stats,stats"
            }
        )

        results.update(response.json())

    stocks = [stock for stock in results if verify_stock(stock) == True]

    helper_functions.send_email(destination=email, stocks = stocks)

if __name__ == "__main__":
    email = str(input("Please enter the email to send the stocks to: "))

    main(email)
