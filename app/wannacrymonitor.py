import requests
import json
import time
import datetime
import threading
import locale

locale.setlocale(locale.LC_ALL, '')

ADDRESS_URL = 'https://blockchain.info/rawaddr/%s'
TICKER_URL = 'https://blockchain.info/ticker'
 
class WannacryMonitor():
  
    # the bitcoin addresses we want to monitor
    addresses = ['13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94',
             '12t9YDPgwueZ9NyMgw519p7AA8isjr6SMw', 
             '115p7UMMngoj1pMvkpHijcRdfJNXj6LrLn']
    
    # total number of transactions made by these addresses
    tx_count = 0
    
    # total amount of bitcoin received by the addresses
    btc_total_received = 0
    
    # Value of the bitcoin received, converted to a currency
    # USD is the only option for now
    currency_total_received = 0
    
    # total amount of bitcoin sent by the addresses
    btc_total_sent = 0    
    
    # Bitcoin sent, converted to currency
    currency_total_sent = 0
    
    # Average payment, in bitcoin
    btc_average_payment = 0
    
    # Converted average payment
    currency_average_payment = 0
    
    # a list of dictionaries containing the information
    # on the bitcoin addresses
    addr_info_list = []    
    
    # date and time of the last transaction made
    last_tx = 0    
    
    # date and time the statistics were last updated
    last_updated = 0
    
    
    def __init__(self):
        # start the thread to keep statistics up to date
        thread = threading.Thread(target=self.update_loop,)
        thread.daemon = True
        thread.start()
        
    def update_loop(self):
        while True:
            self.update_statistics()
            time.sleep(30)
            
    def retrieve_address(self, address):
        # Retrieve information for a bitcoin address
        # from blockchain.info
        response = requests.get(ADDRESS_URL % address)    
        addr_dict = json.loads(response.text)    
        self.addr_info_list.append(addr_dict)

    def update_addr_info(self):
        # Get up to date information on each
        # bitcoin address in the list
        self.addr_info_list = []
        threads = []
        for address in self.addresses:
            thread = threading.Thread(target=self.retrieve_address, 
                                      args=(address,))
            threads.append(thread)
            thread.start()
    
        for thread in threads:
            thread.join()
            
    def clear_statistics(self):
        # clears all the current values 
        self.tx_count = 0
        self.btc_total_received = 0
        self.currency_total_received= 0
        self.btc_total_sent = 0    
        self.currency_total_sent = 0
        self.last_tx = 0    
        self.btc_average_payment = 0
        self.currency_average_payment = 0
        
    def btc_to_currency(self,currency='USD'):
        ticker = json.loads(requests.get(TICKER_URL).text)
        exchange_rate = ticker[currency]['15m']

        self.currency_total_received = locale.currency(exchange_rate * self.btc_total_received )
        self.currency_total_sent = locale.currency(exchange_rate * self.btc_total_sent)
        self.currency_average_payment = locale.currency(exchange_rate * self.btc_average_payment)


    def update_statistics(self):
        try:
            self.update_addr_info()
        except Exception as e:
            print e
            
        self.last_updated = datetime.datetime.now()
        self.clear_statistics()
        recent_txs = []
        for address_dict in self.addr_info_list:
            # Calculate the total number of transactions
            # to or from all of the addresses
            self.tx_count += int(address_dict['n_tx'])
            # The total of bitcoin received by wannacry addresses
            self.btc_total_received += float(address_dict['total_received']) * .00000001
            # total bitcoin spent by the addresses
            self.btc_total_sent += float(address_dict['total_sent']) * .00000001
    
            recent_txs.append(int(address_dict['txs'][0]['time']))

        self.last_tx = datetime.datetime.fromtimestamp(max(recent_txs))        
        self.btc_average_payment = self.btc_total_received / self.tx_count        
        self.btc_to_currency()