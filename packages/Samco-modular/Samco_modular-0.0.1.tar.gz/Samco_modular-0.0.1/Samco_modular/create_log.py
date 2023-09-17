import json
from datetime import datetime, date, time
import pytz # for timezone
import pandas as pd
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge

def create_logbook(samco,token):
    order_book=samco.get_order_book()
    order_book=json.loads(order_book) ##str to dict
    order_book=pd.json_normalize(order_book['orderBookDetails'])

    ###########For creating log##############

    datestring=datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y.%m.%d_%H.%M.%S")
    log=pd.DataFrame()

    # order_book.loc[0,'orderTime']
    element = datetime.strptime('16-Sep-2023 13:31:16',"%d-%b-%Y %H:%M:%S")
    log.loc[0,'Date']=datetime.strptime('16-Sep-2023 13:31:16',"%d-%b-%Y %H:%M:%S")

    for i in range(len(order_book.index)):
        log.loc[i,'ExchOrderTime1']=datetime.strptime(order_book.loc[i,'orderTime'],"%d-%b-%Y %H:%M:%S")

    log['Date']=log['ExchOrderTime1'].dt.date
    log['Time']=log['ExchOrderTime1'].dt.time

    log['Type']=order_book['optionType']
    log.loc[(log['Type'] == 'CE'), 'Type'] = 'Call'
    log.loc[(log['Type'] == 'PE'), 'Type'] = 'Put'

    log['Buy/Sell']=order_book['transactionType']
    log.loc[(log['Buy/Sell'] == 'BUY'), 'Buy/Sell'] = 'Buy'
    log.loc[(log['Buy/Sell'] == 'SELL'), 'Buy/Sell'] = 'Sell'

    log['Strike']=order_book['displayStrikePrice']
    log['Qty']=order_book['displayNetQuantity']
    log['price']=order_book['averagePrice']

    log=log.drop(['ExchOrderTime1'], axis=1)
    return log
