
import requests
import pandas
import csv
from io import StringIO
import time
import datetime
import email_sendgrid
import email_smtp


# Yahoo finance API
YAHOO_FINANCE_API          = "http://finance.yahoo.com/d/quotes.csv"
YAHOO_FINANCE_SYMBOL_PARAM = "s"
YAHOO_FINANCE_FORMAT_PARAM = "f"
YAHOO_FINANCE_52_WEEK_HIGH = "k"
YAHOO_FINANCE_52_WEEK_LOW  = "j"
YAHOO_FINANCE_BID_PRICE    = "b"
YAHOO_FINANCE_52_ASK_PRICE = "a"
YAHOO_FINANCE_52_CLOSE_PRICE = "p"
YAHOO_FINANCE_52_PERCENT_LOW_CHANGE = "j6"
YAHOO_FINANCE_52_PERCENT_HIGH_CHANGE = "k5"
YAHOO_FINANCE_52_LOW_CHANGE = "j5"
YAHOO_FINANCE_52_HIGH_CHANGE = "k4"
YAHOO_FINANCE_DIV_YIELD = 'y'


# File containing list of stocks to process
STOCKS_FILE = "s&p500.csv"

# Number of symbols to request in a batch
BATCH_SIZE = 10

# File contain email address to email to
EMAILS_FILE = "emails.csv"

# Return list of top N values
TOP_N = 100

# Email information
FROM_EMAIL = 'youremailaddress@emai.com'



def read_stock_list():
    """
    Reads the list of stocks and returns a dictionary object.
    :return: a dictionary object of all the stocks where the key is the symbol
    """
    print("Reading list of stocks.")
    stocks = {}
    with open(STOCKS_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stocks[row['Symbol']] = (row['Name'], row['Sector'])
    return stocks


def get_52_week_high_low_for_stocks(stocks):
    """
    Returns a pandas dataframe of stocks sorted by stocks that are closer/lower than their 52-week lows
    :param stocks:
    :return:
    """
    print("Fetching stock quotes.")
    # Build a full list of symbols
    symbols = []
    for key in stocks.keys():
        symbols.append(key)

    num_of_batches = int(len(symbols)/BATCH_SIZE) + 1

    all_stocks_df = pandas.DataFrame()

    #all_stocks_df = pandas.DataFrame()

    # Get quotes for all the stocks in batches
    for i in range(0, num_of_batches):
        print("Fetching quotes in batch: " + str(i+1) + "/" + str(num_of_batches))
        start = i*BATCH_SIZE
        end = start + BATCH_SIZE
        batch_symbols = symbols[start: end]
        batch_symbols_query = '+'.join(batch_symbols)
        request_url = YAHOO_FINANCE_API + "?" + YAHOO_FINANCE_SYMBOL_PARAM + "=" + batch_symbols_query +\
                      "&" + YAHOO_FINANCE_FORMAT_PARAM + "=" + YAHOO_FINANCE_SYMBOL_PARAM + YAHOO_FINANCE_52_ASK_PRICE +\
                      YAHOO_FINANCE_BID_PRICE + YAHOO_FINANCE_52_CLOSE_PRICE + YAHOO_FINANCE_52_WEEK_LOW +\
                      YAHOO_FINANCE_52_WEEK_HIGH + YAHOO_FINANCE_52_LOW_CHANGE +\
                      YAHOO_FINANCE_52_HIGH_CHANGE + YAHOO_FINANCE_DIV_YIELD
        r = requests.get(request_url)

        # Read the returned CSV as a pandas table
        # Returned format is NAME,ASK,BID,52-wLow,52-wHigh
        df = pandas.read_table(StringIO(r.text), header=None, sep=',')
        all_stocks_df = all_stocks_df.append(df, ignore_index=True)

        # Delay to slow down things
        time.sleep(1)


    # Assign columns
    print("Stock quotes have been fetched. Beginning analysis...")
    all_stocks_df.columns=['symbol', 'ask', 'bid', 'close', '52w-low', '52w-high', '52w-low-change', '52w-high-change', 'div-iteryield']

    # Add the percent change columns
    all_stocks_df['52w-%-low-change'] = all_stocks_df['52w-low-change']/all_stocks_df['52w-low']*100
    all_stocks_df['52w-%-high-change'] = all_stocks_df['52w-high-change'] / all_stocks_df['52w-high'] * 100

    # Add the names and sectors
    all_stocks_df['name'] = ""
    all_stocks_df['sector'] = ""
    for index, row in all_stocks_df.iterrows():
        all_stocks_df.loc[index, 'name'] = stocks[row['symbol']][0]
        all_stocks_df.loc[index, 'sector'] = stocks[row['symbol']][1]


    # Process the received quotes
    sorted_values = all_stocks_df.sort_values('52w-%-low-change')

    # Done
    print("Analysis completed.")
    return sorted_values


def email_report(pd_dataframe):
    emails = {}
    print("Emailing result of analysis.")
    with open(EMAILS_FILE) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            emails[row['Name']] = row['Email']

    dt = str(datetime.datetime.now())
    subject = dt + " - 52-week low/high S&P500 stock quote"

    text_msg = '52-week low/high S&P500 stock quotes for ' + dt
    html_msg = '<html><head></head><body>' + str(pd_dataframe.head(TOP_N).to_html(index=False)) + '</body></html>'

    for to_name in emails.keys():
        if email_sendgrid.send_email(emails[to_name], to_name, FROM_EMAIL, subject, text_msg, html_msg) == False:
            print("Error: Failed to send email to : " + to_name + "(" + emails[to_name] + ").")
        else:
            print("Report email to : " + to_name + "(" + emails[to_name] + ").")


def main():
    print("Starting:" + str(datetime.datetime.now()))
    stocks = read_stock_list()
    df = get_52_week_high_low_for_stocks(stocks)
    email_report(df)
    print("Done! " + str(datetime.datetime.now()))


if __name__ == "__main__":
    main()











