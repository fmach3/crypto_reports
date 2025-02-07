import only system from os
from os import system, name
 
# import sleep to show output for some time period
from time import sleep
 
import requests
import hmac
import os
import hashlib
import json, requests
import pandas as pd
import talib
from talib import stream
import sys
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import json
from telethon.sync import TelegramClient


#Telegram Variables

session_name = ""
api_id = ""
api_hash = ""
chat_id = "" 


# Configuration Area:

# Set your API key and secret
api_key = 'account-al5CA9LFqSY7IwiXm8Ry'
api_secret = '28JZdRiKcPYa1mrSbMJ9ULhTxn4d'

monitor=0   #initialize the numerical value for buy/sell rating called monitor
bullbear=0  #initialize the numerical value for the bull/bear rating called bullbear
bull = 0
bear = 0


# The URL to the exchange's API
base_url = "https://api.gemini.com/v2"

#initialize default tracker variable
notify="false"



def print_file_contents(file_name):
    """
    This function accepts a file name as a parameter, opens the file,
    and prints its contents to the standard output.
    """
    try:
        with open(file_name, 'r') as file:
            contents = file.read()
            print(contents)
    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")




def load_symbols(filename):
   symbols = []
   try:
       with open(filename, 'r') as file:
           for line in file:
               symbols.append(line.strip())
   except FileNotFoundError:
       print(f"Error, file {filename} not found.")
   return symbols

symbols = load_symbols('symbols.txt')

def Stoch_Red_or_Green(subject):
	if subject > 50:
		return "green"
	if subject < 50:
		return "red"

def RSI_Red_or_Green(subject,price):
	if subject > float(price):
		return "red"
	if subject < float(price):
		return "green"




def evaluate_macd_signal(macd, signal):
    if macd > 0 and signal > 0:
        if macd > signal:
            return "Bullish"
        else:
            return "Neutral"
    elif macd < 0 and signal < 0:
        if macd > signal:
            return "Confused"
        else:
            return "Bearish"
    else:
        if macd > signal:
            return "Bullish"
        else:
            return "Bearish"

def copy_file(file1, file2):
    with open(file1, "r") as f1, open(file2, "w") as f2:
        f2.write(f1.read())


def calculate_vwap_from_candles(response):
    btc_candle_data = pd.DataFrame(response.json(), columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    btc_candle_data['time'] = pd.to_datetime(btc_candle_data['time'], unit='ms')
    btc_candle_data.set_index('time', inplace=True)
    btc_candle_data.sort_values(by=['time'], inplace=True)
    btc_candle_data['price_volume'] = btc_candle_data['close'] * btc_candle_data['volume']
    vwap = btc_candle_data['price_volume'].sum() / btc_candle_data['volume'].sum()
    return vwap

def get_symbols():
	# Gemini API endpoint
	symbolurl = "https://api.gemini.com/v1/symbols"

	# Send a GET request to the endpoint
	response = requests.get(symbolurl)

	# Parse the JSON response
	data = response.json()

	# Extract the list of symbols
	# symbols = [item['symbol'] for item in data]
	#print (data)
	return data

# retrieve all symbols from gemini
# symbols = get_symbols()

intervals = [
'1day', 
'6hr',
'1hr',
'30m',
'15m',
'5m',
'1m'
]

path = '/home/cryptobot/'



def time_difference_from_now(file_path):
    """
    Calculate the time difference between the current time and the timestamp of the file.

    :param file_path: The path to the file.
    :return: A string describing the time difference.
    """
    if not os.path.exists(file_path):
        return "File does not exist."

    # Get the last modified time of the file
    file_timestamp = os.path.getmtime(file_path)
    file_datetime = datetime.fromtimestamp(file_timestamp)

    # Get the current time
    current_datetime = datetime.now()

    # Calculate the difference
    time_diff = current_datetime - file_datetime

    # Return the difference in a readable format
    return str(time_diff)



# ----------- Telegram functions


def check_and_alert(filename, message):
    # Check if the file exists
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            current_content = file.read()
        # Check if the current content of the file matches the message
        if current_content == message:
            return
        else:
            # Write the new message to the file
            with open(filename, 'w') as file:
                file.write(message)
    else:
        # If file does not exist, write the message to a new file
        with open(filename, 'w') as file:
            file.write(message)

    # write the alert to the HTML web interface
    write_to_alert_file(message)
    # Call the send_telegram_alert function after updating the file
    send_telegram_alert(message)
    # send an email alert to administrator
    # send_alert(message)

# Telegram Alert
def send_telegram_alert(message):
    TOKEN = "5696483844:AAGEPEfwTm5O-EwHpTXzbzk3wm_0QLMtWGo"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    return(requests.get(url).json())



# ----------------------------------------------







def get_file_safe_name():
    now = datetime.now()
    date = now.date()
    time = now.time()

    date_str = date.strftime("%Y-%m-%d")
    time_str = time.strftime("%H-%M-%S")

    safe_name = f"{date_str}_{time_str}"
    return safe_name

# write to file shown to visitors
def write_to_alert_file(message):
    db_file = '/home/cryptobot/alerts/alerts.txt'
    try:
        with open(db_file, 'a') as f:
            f.write(message + '\n')
    except FileNotFoundError:
        print(f"Error: The file '{db_file}' could not be found.")
    except PermissionError:
        print(f"Error: You do not have permission to write to '{db_file}'.")
    except Exception as e:
        print(f"Error: {e}")

# Function to send an email alert
def send_alert(subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, EMAIL_PASSWORD)
    server.send_message(msg)
#    send_telegram_alert(message)
    server.quit()



# a function to display the filename provided
def display_file(filename):
    try:
        with open(filename, 'r') as file:
            print(file.read())
    except FileNotFoundError:
        print("File not found!")
    except:
        print("An error occurred!")



def pivot_points(high, low, close):
    # Calculate pivot point
    pivot = (high + low + close) / 3

    # Calculate support and resistance levels
    support1 = (2 * pivot) - high
    support2 = pivot - (high - low)
    resistance1 = (2 * pivot) - low
    resistance2 = pivot + (high - low)

    return pivot, support1, support2, resistance1, resistance2

def slope(lst):
#    print (lst)
    if (lst[-1] - lst[-2]) / (lst[-3] - lst[-2]) > 0:
        return '↑'
    elif (lst[-1] - lst[-2]) / (lst[-3] - lst[-2]) < 0:
        return '↓'
    else:
        return '→'
    return

def chart(symbol):
		#<!-- TradingView Widget BEGIN -->
		print(f'<div class="tradingview-widget-container">')
		print(f'<div id="tradingview_118fe"></div>')
		print(f'<div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/BTCUSD/?exchange=GEMINI" rel="noopener" target="_blank"><span class="blue-text">Bitcoin chart</span></a> by TradingView</div>')
		print(f'<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>')
		print(f'<script type="text/javascript">')
		print(f'new TradingView.widget(')
		print('{')
		print(f'"autosize": true,')
		print(f'"symbol": "GEMINI:{symbol}",')
		print(f'"interval": "D",')
		print(f'"timezone": "Etc/UTC",')
		print(f'"theme": "dark",')
		print(f'"style": "1",')
		print(f'"locale": "en",')
		print(f'"toolbar_bg": "#f1f3f6",')
		print(f'"enable_publishing": false,')
		print(f'"allow_symbol_change": true,')
		print(f'"studies": [')
		print(f'   "RSI@tv-basicstudies",')
		print(f'   "StochasticRSI@tv-basicstudies",')
		print(f'   "MACD@tv-basicstudies"')
		print(f'   ],')
		print(f'"container_id": "tradingview_118fe"')
		print('}')
		print(f');')
		print(f'</script>')
		print(f'</div>')
		#<!-- TradingView Widget END -->


def printV(value):
    print("{:0.2f}".format(value))


def TV_tech_analysis(symbol, interval):
		#<!-- TradingView Widget BEGIN -->
		print(f'<div class="tradingview-widget-container">')
		print(f'<div class="tradingview-widget-container__widget"></div>')
		print(f'<div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/{symbol}/?exchange=GEMINI" rel="noopener" target="_blank"><span class="blue-text">Bitcoin analysis</span></a> by TradingView</div>')
		print(f'<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>')
		print('{')
		print(f'"interval": "{interval}",')
		print(f'"width": 425,')
		print(f'"isTransparent": false,')
		print(f'"height": 450,')
		print(f'"symbol": "GEMINI:{symbol}",')
		print(f'"showIntervalTabs": true,')
		print(f'"locale": "en",')
		print(f'"colorTheme": "dark"')
		print('}')
		print(f'</script>')
		print(f'</div>')
		#<!-- TradingView Widget END -->


def avg_time_between_peaks_valleys(df):
    rsi_values = df['rsi'].tolist()
    timestamps = df['timestamp'].tolist()
    peaks = []
    valleys = []
    for i in range(1, len(rsi_values) - 1):
        if rsi_values[i] > rsi_values[i - 1] and rsi_values[i] > rsi_values[i + 1]:
            peaks.append(timestamps[i])
        elif rsi_values[i] < rsi_values[i - 1] and rsi_values[i] < rsi_values[i + 1]:
            valleys.append(timestamps[i])

    n = min(len(peaks), len(valleys), 3)
    time_differences = [peaks[i] - valleys[i] for i in range(n)]
    avg_time_difference = sum(time_differences) / n
    return avg_time_difference

def write_moving_averages_to_file(data, filename="./data/movingaverages.php"):
    moving_averages_list = moving_averages(data)
    with open(filename, "w") as outfile:
        outfile.write("\n".join(moving_averages_list))



def get_symbol_data(symbol, bull, bear, monitor):

		# Set the API endpoint URL
		url = 'https://api.gemini.com/v1/pubticker/'+symbol

		#symbolpath = path+'{symbol}.php'

              
		# send output to a file instead of standard output
		sys.stdout = open(outputfile, 'w')


		# 	Create a HMAC-SHA384 signature of the request payload, signed with your secret API key
		payload = ''
		signature = hmac.new(bytes(api_secret, 'latin-1'), bytes(payload, 'latin-1'), hashlib.sha384).hexdigest()

		# Set the headers for the request
		headers = {
	    	'Content-Type': 'text/plain',
		    'Content-Length': str(len(payload)),
		    'X-GEMINI-APIKEY': api_key,
		    'X-GEMINI-PAYLOAD': payload,
	    	'X-GEMINI-SIGNATURE': signature,
		}

		# Make a GET request to the API
		response = requests.get(url, headers=headers)

		# Check the status code to make sure the request was successful
		if response.status_code == 200:
			# The request was successful, so parse the response data
			data = response.json()
			# The current price is in the "last" field of the response data
			price = data['last']
		else:
			print ('api error')
			price = 'api error'

		print (f'<meta http-equiv="refresh" content="20">')
		print (f"<?php $symbol = \'{symbol}\' ?>")
		print ('<TABLE><TR>')
		print (f'<TD valign=top><TABLE><TR>')

		price_slope = ""

		print(f'<A target=_newish HREF=http://cryptobot.graphinex.com?symbol={symbol}>{symbol}</a> Price: {price_slope} {price} Date: {date} Time: {time}')


		print (f'<TD>Interval</TD>')
		print (f'<td>VWAP</td>')
		print (f'<td>200MA</td>')
		print (f'<td>100MA</td>')
		print (f'<td>50MA</td>')
		print (f'<td>33MA</td>')
		print (f'<td>14MA</td>')
		print (f'<td>9MA</td>')
		print (f'<TD>RSI</TD>')
		print (f'<td>MACD</td>')
		print (f'<td>Stoch RSI</td>')
		print (f'<td>OB/OS</td>')
		print (f"<td>Weight</td>")

		#print(f"<td>PP</td>")
		#print(f"<td>S1</td>")
		#print(f"<td>S2</td>")
		#print(f"<td>R1</td>")
		#print(f"<td>R2</td>")

		print('</TR>')


		#print("Pivot point: ", pivot)
		#print("Support 1: ", support1)
		#print("Support 2: ", support2)
		#print("Resistance 1: ", resistance1)
		#print("Resistance 2: ", resistance2)


		interval_1m_macd_status = 0 # initialize variable
		interval_3m_macd_status = 0 # initialize variable
		interval_5m_macd_status = 0 # initialize variable
		interval_15m_macd_status = 0 # initialize variable
		interval_30m_macd_status = 0 # initialize variable
		interval_1hr_macd_status = 0 # initialize variable
		interval_4hr_macd_status = 0 # initialize variable
		interval_6hr_macd_status = 0 # initialize variable
		interval_1d_macd_status = 0  # initialize variable
		interval_3d_macd_status = 0  # initialize variable
		interval_1w_macd_status = 0  # initialize variable
        
        
		totalRSI = 0


		for interval in intervals: 

			# reset default varaibles
			weight = 1

			if interval == "1m":
				weight = .00523
			if interval == "5m":
				weight = .02616
			if interval == "15m":
				weight = .07849
			if interval == "30m":
				weight = .15699
			if interval == "1hr":
				weight = .31397
			if interval == "6hr":
				weight = .353532
			if interval == "1day":
				weight = .388383

			# now call function we defined above
			#clear()
			print (f'<TR>')
			print (f'<TD>{interval}</TD>')
			#print (interval)
			requeststring = base_url + "/candles/"+symbol+"/"+interval
			response = requests.get(requeststring)
			#print (f'Request: {requeststring}')
			btc_candle_data = pd.DataFrame(response.json(), columns =['time','open','high','low','close','volume'])

			btc_candle_data['time'] = pd.to_datetime(btc_candle_data['time'], unit='ms')
			btc_candle_data.set_index('time', inplace=True)
			btc_candle_data.sort_values(by =['time'], inplace = True)


				#text = "The current price of Bitcoin on Gemini is ${price}\n" 
		 		#with open("index.txt", "a") as f:
   				#	f.write(text)


			#else:
			    # The request was not successful, so handle the error
			    #print('An error occurred while trying to get the Bitcoin price from Gemini')

			#vwap = calculate_vwap_from_candles(btc_candle_data)
			vwap=""
			#print(f"VWAP: {vwap:.2f}")
			fontcolor="black"
			print (f'<td><font color={fontcolor}> {vwap}</font></td>')
			#print (f'<td><font> comingsoon</font></td>')

			sma = talib.SMA(btc_candle_data["close"], timeperiod=14)
			latest = stream.SMA(btc_candle_data["close"], timeperiod=14)

			fastk, fastd = talib.STOCHRSI(btc_candle_data["close"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
			f, fd = stream.STOCHRSI(btc_candle_data["close"], timeperiod=14, fastk_period=5, fastd_period=3, fastd_matype=0)
			#print(fastk[-1], f)
			stochrsi = fastk[-1],f
			#print (data)
			#print (btc_candle_data)
			array_length = len(btc_candle_data)-1
			fontcolor = "black"







			#MATWOHUNDRED = round(btc_candle_data.close.rolling(200).mean()[array_length],2)
			MATWOHUNDRED = btc_candle_data.close.rolling(200).mean()[array_length]
			#print (MATWOHUNDRED)
			#print (price)

              
			if MATWOHUNDRED > float(price):
				fontcolor = "red"
			if MATWOHUNDRED  < float(price):
				fontcolor = "green"

			print (f'<td><font color={fontcolor}> {MATWOHUNDRED}</font></td>')


			MAONEHUNDRED = btc_candle_data.close.rolling(100).mean()[array_length]
			fontcolor = RSI_Red_or_Green(MAONEHUNDRED,price)
			print (f'<td><font color={fontcolor}> {MAONEHUNDRED}</font></td>')

			MAFIFTY = btc_candle_data.close.rolling(50).mean()[array_length]
			fontcolor = RSI_Red_or_Green(MAFIFTY,price)
			print (f'<td><font color={fontcolor}> {MAFIFTY}</font></td>')

			MATHIRTYTHREE = btc_candle_data.close.rolling(33).mean()[array_length]
			fontcolor = RSI_Red_or_Green(MATHIRTYTHREE,price)
			print (f'<td><font color={fontcolor}> {MATHIRTYTHREE}</font></td>')



			#MAFOURTEEN = round(btc_candle_data.close.rolling(14).mean()[array_length],2)
			MAFOURTEEN = btc_candle_data.close.rolling(14).mean()[array_length]
			if MAFOURTEEN > float(price):
				fontcolor = "red"
			if MAFOURTEEN < float(price):
				fontcolor = "green"
			print (f'<td><font color={fontcolor}> {MAFOURTEEN}</font></td>')
			#print (f'200 mean: {btc_candle_data.close.rolling(200).mean()[array_length]}')
			#print (f'14 mean: {btc_candle_data.close.rolling(14).mean()[array_length]}')
	
			MANINE = btc_candle_data.close.rolling(9).mean()[array_length]
			fontcolor = RSI_Red_or_Green(MANINE,price)
			print (f'<td><font color={fontcolor}> {MANINE}</font></td>')


			# Extract the close prices from the data
			#close_prices = [x["close"] for x in data]
			close_prices = btc_candle_data.close
 

			# Calculate the RSI using ta-lib
			rsi = talib.RSI(close_prices, timeperiod=14)

			rsi = round(rsi,2)

			# we need to send an alert if 1hr RSI reaches certain point
           #send_alert(subject, message)
			rsi_lower_trigger = 25
			rsi_upper_trigger = 75

			color="black"
			subject="Cryptobot {symbol} RSI Alert"



#######------------------- RSI ALERT


			if rsi[array_length] > rsi_upper_trigger:
				message = f"{symbol} RSI on {interval} is higher than {rsi_upper_trigger}: {rsi[array_length]} " 
				if (interval == "1day"):
					# Check and send an alert
					#check_and_alert()
					check_and_alert(f'chats/RSI_{symbol}_{interval}_{chat_id}.txt', message)
				color="green"
			if rsi[array_length] < rsi_lower_trigger: 
				message = f"{symbol} RSI on {interval} is lower than {rsi_lower_trigger}: {rsi[array_length]}" 
				if (interval == "6hr") or (interval == "1day"):
					check_and_alert(f'chats/RSI_{symbol}_{interval}_{chat_id}.txt', message)
				color="red"



			#write_to_alert_file(message)
			#rsi_slope = slope(rsi)
			rsi_slope = ""
			#print (f'<td><font color={color}>{rsi[array_length]} {rsi_slope}</font></td>')
			print (f'<td><font color={color}>{rsi_slope} {rsi[array_length]}</font></td>')
			#print (f'<td><font color=>{rsi[array_length]}</font></td>')
			#print (f'RSI: {rsi[array_length]}')
			#print (rsi[array_length])

			# Calculate the MACD using ta-lib

			macd, macd_signal, macd_hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)

			#macd_display1 = round(macd[-1],1)
			#macd_displayhist1 = round(macd_hist[-1],1)
			#macd_signaldisplay1 = round(macd_signal[-1],1)
			macd_display1 = macd[-1]
			macd_displayhist1 = macd_hist[-1]
			macd_signaldisplay1 = macd_signal[-1]
			macd_status = ""
			macd_status = evaluate_macd_signal(macd_display1, macd_signaldisplay1)
			macd_slope = slope (macd_hist)

			last_rsi = rsi.iloc[-1]
			last_macd = macd.iloc[-1]
			last_macdsignal = macd_signaldisplay1
			last_macdhist = macd_displayhist1
			#prev_macdhist =  macdhist.iloc[-2]


			if macd_status == "Bullish":
				bull = bull + (1*weight) 
				#bull = bull + weight
			if macd_status == "Bearish":
				bear = bear - (1*weight)
				#bear = bear - weight
			if macd_status == "Confused":
				bull = bull + (.5*weight)
				#bull = bull + weight
			if macd_status == "Neutral":
				bear = bear - (.5*weight)
				#bear = bear - weight



			if interval == '1m':
				interval_1m_rsi = last_rsi
				interval_1m_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_1m_macd_signal = last_macdsignal
				interval_1m_macd_slope = macd_slope
				interval_1m_macd = last_macd
			if interval == '3m':
				interval_3m_rsi = last_rsi
				interval_3m_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_3m_macd_signal = last_macdsignal
				interval_3m_macd_slope = macd_slope
				interval_3m_macd = last_macd
			if interval == '5m':
				interval_5m_rsi = last_rsi
				interval_5m_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_5m_macd_signal = last_macdsignal
				interval_5m_macd_slope = macd_slope
				interval_5m_macd = last_macd
			if interval == '15m':
				interval_15m_rsi = last_rsi
				interval_15m_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_15m_macd_signal = last_macdsignal
				interval_15m_macd_slope = macd_slope
				interval_15m_macd = last_macd
			if interval == '30m':
				interval_30m_rsi = last_rsi
				interval_30m_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_30m_macd_signal = last_macdsignal
				interval_30m_macd_slope = macd_slope
				interval_30m_macd = last_macd
			if interval == '1hr':
				interval_1hr_rsi = last_rsi
				interval_1hr_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_1hr_macd_signal = last_macdsignal
				interval_1hr_macd_slope = macd_slope
				interval_1hr_macd = last_macd
			if interval == '4h':
				interval_4hr_rsi = last_rsi
				interval_4hr_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_4hr_macd_signal = last_macdsignal
				interval_4hr_macd_slope = macd_slope
				interval_4hr_macd = last_macd
			if interval == '6h':
				interval_6hr_rsi = last_rsi
				interval_6hr_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_6hr_macd_signal = last_macdsignal
				interval_6hr_macd_slope = macd_slope
				interval_6hr_macd = last_macd
			if interval == '1day':
				interval_1d_rsi = last_rsi
				interval_1d_macd_status = evaluate_macd_signal(last_macd, last_macdsignal)
				interval_1d_macd_signal = last_macdsignal
				interval_1d_macd_slope = macd_slope
				interval_1d_macd = last_macd


#####--------------- MACD Status Alignment Alert


			alert_file = f"chats/macd_{macd_status}_alignment_{symbol}_{chat_id}.txt"
			time_stamp = time_difference_from_now(alert_file)
			if (macd_status == "Bearish"):
				alert_message = f"{symbol}:{interval}: Bearish Alignment - lapsed: {time_stamp}"

			if (macd_status == "Bullish"):
				alert_message = f"{symbol}:{interval}: Bullish Alignment - lapsed: {time_stamp}"


			print (f'<td>{macd_slope} {macd_display1} {macd_signaldisplay1} {macd_status}</td>')
			#print (f'<td> {macd_display1} {macd_signaldisplay1} {macd_status}</td>')
			last_status = ""
			# track the status of 1hr and 1day intervals and email alert if changed
			if (interval == "1hr") or (interval == "1day") or (interval == "3hr") or (interval =="4hr") or (interval == "2hr")  :
				market_status =  macd_status
				macd_status_file = "macd/"+symbol+"_"+interval+"_"+market_status+"_status.txt"
				time_stamp = datetime.now()
				if os.path.exists(macd_status_file):
					time_stamp = time_difference_from_now(macd_status_file)
					with open(macd_status_file, "r") as f:
						last_status = f.read().strip()
				if last_status != market_status:
					message = f"{symbol}:{interval} is now {market_status} at {time} on {date} (was {last_status})- time lapsed since last {market_status}: {time_stamp}"
					print (f"Sending alert! status_file: {macd_status_file}")
					check_and_alert(macd_status_file, message)
					#send_alert(message)
					print (f"Writing {macd_status_file}")
					with open(macd_status_file, "w") as f:
						f.write(market_status)
						print (market_status)





			# Calculate the st:ochastic RSI using ta-lib

			#stoch_rsi = talib.:STOCHRSI(close_prices, fastk_period=14, slowk_period=3, slowd_period=3)
			stoch_rsi = talib.STOCH(rsi, rsi, rsi)




			stoch_rsi_display = round(stochrsi[0],2)



					

			stochrsi_difference = round(stochrsi[len(stochrsi)-1] - stochrsi[len(stochrsi)-2])
			stochrsiA = round(stochrsi[0])
			stochrsiB = round(stochrsi[1])                  
			stoch_color="Black"
			if stochrsiA > 67:
				stoch_color="Green"
			if stochrsiA < 32:
				stoch_color="Red"
			print (f'<td><font color={stoch_color}>{stochrsiA} {stochrsiB} {stochrsi_difference}</font></td>')

			currentmacd=macd[array_length]
			currentrsi=rsi[array_length]
			currentstoch=stoch_rsi_display
			recommendation = ''

			if currentrsi > 67:
				if currentstoch > 67:
					recommendation = '<font color=Green>OverBought</font>'


			if currentrsi < 33:
				if currentstoch < 33:
					recommendation = '<font color=Red>OverSold</font>'

			totalRSI = totalRSI + last_rsi

			#peakorvalley = avg_time_between_peaks_valleys(pd)

			#print (f"<td>{peakorvalley}</td>")
			print (f"<td>{recommendation}</td>")

			print (f"<td>{bull} {bear} / {weight} </td>")

			print (f'</TR>')

		avgRSI = totalRSI / 7
		print (f' Average RSI:{avgRSI}')


		# scale the average RSI for use as RSI monitor:
		scaled_rsi = scale_rsi_to_chart(avgRSI)
        
		monitor = scaled_rsi

		sys.stdout = sys.__stdout__

		#if abs(monitor) > 1.318:
		if abs(monitor) > 10:
			sender_email = "graphinex@gmail.com"
			receiver_email = "frankcell@graphinex.com"
			password = "zsfypbaujjalwpbn" 
			# send_alert
			message = """\
Subject: Cryptobot Alert for """+symbol+"""

Check: http://cryptobot.graphinex.com?symbol="""+symbol+""" for TA result: """+str(monitor)
			server = smtplib.SMTP('smtp.gmail.com', 587)
			server.starttls()
			server.login(sender_email, password)
			server.sendmail(sender_email, receiver_email, message)
			# print("Email sent!")
			server.quit()
			message=symbol+" for TA result: "+str(monitor)
			write_to_alert_file(message)

		return path+'/hits/'+str(monitor)+'_'+symbol+'_'+price+'_'+get_file_safe_name()+'_'+str(bull)+'_'+str(bear)+'.php'

def scale_value(value, min_original, max_original, min_scale, max_scale):
    # Normalize the value to a 0-1 scale
    normalized = (value - min_original) / (max_original - min_original)

    # Scale the normalized value to the desired range
    scaled_value = normalized * (max_scale - min_scale) + min_scale

    return scaled_value



def scale_rsi_to_chart(rsi):
    # Scale from 0-100 to -1.38 to 1.38 (past 0)

#    return scale_value(rsi, 0, 100, -1.38, 1.38)
    if 0 <= rsi < 50:
        # Scale from 0-49 to -1.38 to 0
        return (-1.38 * (((50 - rsi)/50)))
        #return scale_value(rsi, 0, 49, -1.38, 0)
    elif 50 <= rsi <= 100:
        # Scale from 50-100 to 0 to 1.38
        return (1.38 * (((rsi-50)/50)))
        #return scale_value(rsi, 50, 100, 0, 1.38)
    else:
        raise ValueError("RSI value must be between 0 and 100")



# MAIN PROGRAM
 

try:

	# process each symbol
	for symbol in symbols:

		# Generate current date and time for timestamps
		now = datetime.now()
		date = now.date()
		time = now.time()
		# create a filename for timestamped reports
		
		
		# stout takes a few seconds to write to the file, so to lower the chance a web page visitor will get an empty file read we'll output to a temporary file and then copy to the completed file
		#print (symbol)
		symbolfile = path+'/symbols/'+symbol+'.php'
		outputfile = path+'/output/'+symbol+'.php'

		# get symbol data and run technical analysis
		#print (symbol)
		price="0"
		#monitor = get_symbol_data(symbol,price)
		#reportfile = path+'/hits/'+str(monitor)+'_'+symbol+'_'+price+'_'+get_file_safe_name()+'.php'
		reportfile = get_symbol_data(symbol, bull,bear, monitor)
		
		#reportfile = path+'/hits/'+symbol+'/'+str(monitor)+'_'+symbol+'_'+get_file_safe_name()+'.php'

		#copy_file(outputfile, reportfile)
		#if abs(monitor)>0:
		#	copy_file(symbolfile, reportfile)
		# generate a report regardless of result monitor
		copy_file(symbolfile, reportfile)

		pass

except ExceptionType as e:
	pass
