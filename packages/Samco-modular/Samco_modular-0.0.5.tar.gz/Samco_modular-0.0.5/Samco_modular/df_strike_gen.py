import websockets
from websocket import WebSocket
import pandas as pd
import numpy as np
from datetime import datetime, date, time
import time as tym
import pytz # for timezone
from IPython.display import clear_output
import json
from snapi_py_client.snapi_bridge import StocknoteAPIPythonBridge


def df_strikeprice_func(token, iDict, Scripmaster):

    expiry=iDict['expiry']
    underlying_print=iDict['underlying_print']
    entry_time=iDict['entry_time']
    num_strikes=iDict['num_strikes']
    Buy_prm_closest=iDict['Buy_prm_closest']
    Delay_buy=iDict['Delay_buy']
    Sell_prm_closest=iDict['Sell_prm_closest']
    Stop_loss=iDict['Stop_loss']
    buy_sell_order=iDict['buy_sell_order']
    same_day_sqoff=iDict['same_day_sqoff']
    squareoff_time=iDict['squareoff_time'] 
    underlying_samco_index=iDict['underlying_samco_index']
    strike_step=iDict['strike_step']
    qty=iDict['qty'] 
    lots=iDict['lots']
    buy_sell_print=iDict['buy_sell_print']
    token=token
    
    start = tym.time() ## time counter start
    code_start=datetime.now(pytz.timezone('Asia/Kolkata')).time()
    print("New Code start time=",code_start)
    ######### Codes for fetching Underlying live value ##########

    import requests
    headers = {
          'Accept': 'application/json',
          'x-session-token': token
        }

    r = requests.get('https://api.stocknote.com/quote/indexQuote', params={
          'indexName': underlying_samco_index
        }, headers = headers)
    r=r.json()
    print(r)

    underlying_ref=float(r['spotPrice'])
    underlying_spot=underlying_ref
    underlying_ref= round(underlying_ref/strike_step,0)*strike_step

    ######### Codes for strikes generation for Underlying strikes into df_strikeprice ##########

    df_strikeprice=pd.DataFrame(index=range(num_strikes))
    df_strikeprice["Strike_Selection"]=np.nan  ## filling  strike price column with nan values in new column
    df_strikeprice["Scripcode_CE"]=np.nan ## filling CE scripcode column with nan values in new column
    df_strikeprice["Scripcode_PE"]=np.nan ## filling  PE scripcode columnwith nan values in new column
    df_strikeprice["CE_LTP"]=np.nan ## filling  CE LTP columnwidth nan values in new column
    df_strikeprice["PE_LTP"]=np.nan ## filling  PE LTP columnwidth nan values in new column

    for i in range(num_strikes):   ## finding all the strikes referring ATM calculated as above
        df_strikeprice["Strike_Selection"][i]=underlying_ref - strike_step*((num_strikes-1)/2-i)

    ############## Scripmaster filteration #################
    Scripmaster['expiryDate'] = pd.to_datetime(Scripmaster['expiryDate']).dt.date
    Scripmaster['tradingSymbol']=Scripmaster['tradingSymbol'].astype(str)
    Scripmaster['CEPE']=Scripmaster['tradingSymbol'].str[-2:]

    Scripmaster_CE=Scripmaster[(Scripmaster.name == underlying_print) & (Scripmaster.expiryDate == expiry) & (Scripmaster.CEPE=="CE") & (Scripmaster.instrument=="OPTIDX")]  ## Setting filter in columns
    Scripmaster_PE=Scripmaster[(Scripmaster.name == underlying_print) & (Scripmaster.expiryDate == expiry) & (Scripmaster.CEPE=="PE") & (Scripmaster.instrument=="OPTIDX")] ## Setting filter in columns
    Scripmaster_CE.reset_index(inplace=True) ## Resetting the index and after slicing dataframe
    Scripmaster_PE.reset_index(inplace=True) ## Resetting the index and after slicing dataframe

    ################ Filling tradingSymbols into df_strikeprice ##############
    for i in range(len(df_strikeprice.index)):  ## looking for strikes from data extr from CSV and saving respective scripcodes
        for j in range(len(Scripmaster_CE.index)):
            if Scripmaster_CE['strikePrice'][j]==df_strikeprice['Strike_Selection'][i]:
                df_strikeprice['Scripcode_CE'][i]=Scripmaster_CE['tradingSymbol'][j]
        for k in range(len(Scripmaster_PE.index)):
            if Scripmaster_PE['strikePrice'][k]==df_strikeprice['Strike_Selection'][i]:
                df_strikeprice['Scripcode_PE'][i]=Scripmaster_PE['tradingSymbol'][k]
    mid1 = tym.time()

    ################ Codes for fetching and filtering option chain ##############
    headers = {
      'Accept': 'application/json',
      'x-session-token': token
    }

    r = requests.get('https://api.stocknote.com/option/optionChain', params={
      'searchSymbolName': underlying_print
    }, headers = headers)

    r=r.json()
    option_chain=pd.json_normalize(r['optionChainDetails'])
    option_chain['strikePrice']=option_chain['strikePrice'].astype(str)
    option_chain['strikePrice']=option_chain['strikePrice'].astype(float)
    option_chain['expiryDate'] = pd.to_datetime(option_chain['expiryDate']).dt.date
    option_chain['lastTradedPrice']=option_chain['lastTradedPrice'].astype(float)
    option_chain=option_chain[(option_chain.expiryDate == expiry) & (option_chain.strikePrice<=df_strikeprice['Strike_Selection'][len(df_strikeprice)-1]) & (option_chain.strikePrice>=df_strikeprice['Strike_Selection'][0])]  ## Setting filter in columns
    option_chain.reset_index(inplace=True) ## Resetting the index and after slicing dataframe
    
    ############# Code for fetching CE and PE LTPs of strike prices in each row from 5PAISA live data ############

    # temp_dataframe=pd.DataFrame() ##temporary dataframe for receiving historical price table
    # temp_empty=pd.DataFrame() ##empty dataframe only used for making temp_dataframe empty

    for i in range(len(df_strikeprice.index)):
        for j in range(len(option_chain.index)):
            if df_strikeprice['Scripcode_CE'][i]==option_chain['tradingSymbol'][j]:
                df_strikeprice['CE_LTP'][i]=option_chain['lastTradedPrice'][j]
                break
        for k in range(len(option_chain.index)):
            if df_strikeprice['Scripcode_PE'][i]==option_chain['tradingSymbol'][k]:
                df_strikeprice['PE_LTP'][i]=option_chain['lastTradedPrice'][k]
                break
        if np.isnan(df_strikeprice['CE_LTP'][i]):
            df_strikeprice.loc[i,'CE_LTP']=10000 #replacing NaN with large no like 10000
        if np.isnan(df_strikeprice['CE_LTP'][i]):
            df_strikeprice.loc[i,'CE_LTP']=10000 #replacing NaN with large no like 10000
    mid2 = tym.time()

    ########Code for finding Scripcode of CE nearest to sell_prm and buy_prm premiums#######
    lst = df_strikeprice['CE_LTP'].to_numpy()

    CE_indx_SELL= (np.abs(lst - Sell_prm_closest)).argmin()
    CE_indx_BUY= (np.abs(lst - Buy_prm_closest)).argmin()

    CE_Scripcode_SELL=df_strikeprice.loc[CE_indx_SELL,'Scripcode_CE']
    CE_Scripcode_SELL = getattr(CE_Scripcode_SELL, "tolist", lambda: CE_Scripcode_SELL)() ##convert numpy int32 to native int to avoid 5paisa json serializable error
    CE_Scripcode_BUY=df_strikeprice.loc[CE_indx_BUY,'Scripcode_CE']
    CE_Scripcode_BUY = getattr(CE_Scripcode_BUY, "tolist", lambda: CE_Scripcode_BUY)() ##convert numpy int32 to native int to avoid 5paisa json serializable error

    ########Code for finding Scripcode of PE nearest to 110 and 10 premiums#######
    lst = df_strikeprice['PE_LTP'].to_numpy()
    PE_indx_SELL= (np.abs(lst - Sell_prm_closest)).argmin()
    PE_indx_BUY= (np.abs(lst - Buy_prm_closest)).argmin()

    PE_Scripcode_SELL=df_strikeprice.loc[PE_indx_SELL,'Scripcode_PE']
    PE_Scripcode_SELL = getattr(PE_Scripcode_SELL, "tolist", lambda: PE_Scripcode_SELL)() ##convert numpy int32 to native int to avoid 5paisa json serializable error
    PE_Scripcode_BUY=df_strikeprice.loc[PE_indx_BUY,'Scripcode_PE']
    PE_Scripcode_BUY = getattr(PE_Scripcode_BUY, "tolist", lambda: PE_Scripcode_BUY)() ##convert numpy int32 to native int to avoid 5paisa json serializable error

    oDict={'CE_Scripcode_SELL':CE_Scripcode_SELL,
            'CE_Scripcode_BUY':CE_Scripcode_BUY,
            'PE_Scripcode_SELL':PE_Scripcode_SELL,
            'PE_Scripcode_BUY':PE_Scripcode_BUY}
    
    code_completion=tym.time()

    ##########Print strike selection, scripcode and LTPs#######################
    clear_output()

    print("Script= ", underlying_print)
    print("Expiry date= ",expiry)
    print("No of lots= ", lots)
    print("SELL BUY TYPE= ", buy_sell_print[buy_sell_order])
    print("Same day SQOFF= ", same_day_sqoff)

#     print("Code start time=",code_start)
#     print("time till fetching data from 5paisa=", mid1-start)
#     print("Time for fetching LTPs from 5paisa/above looptime=", mid2-mid1)
#     print("Time after loop=",code_completion-mid2)
    print("Code Execution time=",code_completion-start)

    print("\n"+underlying_print+" LTP= ",underlying_spot)
    print("Strike SELL CE=",int(df_strikeprice.loc[CE_indx_SELL,'Strike_Selection']),
          "  Price=",df_strikeprice.loc[CE_indx_SELL,'CE_LTP'],
         "   Scripcode=",CE_Scripcode_SELL)
    print("Strike SELL PE=",int(df_strikeprice.loc[PE_indx_SELL,'Strike_Selection']),
          "  Price=",df_strikeprice.loc[PE_indx_SELL,'PE_LTP'],
         "   Scripcode=",PE_Scripcode_SELL)
    print("Strike BUY CE=",int(df_strikeprice.loc[CE_indx_BUY,'Strike_Selection']),
          "  Price=",df_strikeprice.loc[CE_indx_BUY,'CE_LTP'],
         "   Scripcode=",CE_Scripcode_BUY)
    print("Strike BUY PE=",int(df_strikeprice.loc[PE_indx_BUY,'Strike_Selection']),
          "  Price=",df_strikeprice.loc[PE_indx_BUY,'PE_LTP'],
         "   Scripcode=",PE_Scripcode_BUY)


    return [df_strikeprice,oDict]