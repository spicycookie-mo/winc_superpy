from datetime import datetime, timedelta
import argparse
import csv
import pandas as pd
import os
from os.path import exists as file_exists
from prettytable import PrettyTable  
import numpy as np
import warnings
from pandas.core.common import SettingWithCopyWarning
from tools_rich import console

# Class used for data validation
class Type:

    @staticmethod
    def valid_price_buy(price):
        try:
            float(price)
        except ValueError:
            msg = "That does not look right: {0!r}. Please enter a valid number.".format(price)
            raise argparse.ArgumentTypeError(msg)
        if float(price) < 0:
                msg = "So they are paying you to buy that? Must be an amazing product...Try a value greater than 0."
                raise argparse.ArgumentTypeError(msg)
        else:
            return round(float(price),2)   

    @staticmethod
    def valid_price_sell(price):
        try:
            float(price)
        except ValueError:
            msg = "That does not look right: {0!r}. Please enter a valid number.".format(price)
            raise argparse.ArgumentTypeError(msg)
        if float(price) < 0:
            msg = "So you are paying money to sell this? Must be an amazing product...Try a value greater than 0."
            raise argparse.ArgumentTypeError(msg)
        else:
            return round(float(price),2) 

    @staticmethod
    def valid_quantity(quantity):
        try:
            int(quantity)
        except ValueError:
            msg = "That does not look right: {0!r}. Please enter a valid number (integer).".format(quantity)
            raise argparse.ArgumentTypeError(msg)
        if int(quantity) <= 0:
            msg = "Try a value greater than 0."
            raise argparse.ArgumentTypeError(msg)
        return int(quantity)

    @staticmethod
    def valid_date_expiration(date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
            if date >= Date.get_date():
                return date
            else:
                raise argparse.ArgumentTypeError("And who will you sell that to? It's already expired...Go put it back")
        except ValueError or TypeError:
            msg = "The date should be in the YYYY-MM-dd format. Does {0!r} look like the correct format?".format(date)
            raise argparse.ArgumentTypeError(msg)

    @staticmethod
    def valid_date_report(date):
        try:
            datetime.strptime(date, "%Y-%m-%d")    
        except ValueError:
            msg = "The date should be in the YYYY-MM-dd format. Does {0!r} look like the correct format?".format(date)
            raise argparse.ArgumentTypeError(msg)   
        if date <= Date.get_date():
            return date
        else:
            raise argparse.ArgumentTypeError("I can't predict the future. Choose another date")

    @staticmethod
    def valid_timeframe(timeframe):
        start_date = timeframe[0]
        end_date = timeframe[-1]
        if end_date >= start_date:
            timeframe_ok = True
        else:
            timeframe_ok = False
        return timeframe_ok

    @staticmethod
    def valid_days(x):
        if x == 'reset':
            return ('reset')
        else:
            try:
                int(x)
                return int(x)
            except ValueError:
                msg = "That does not look right: {0!r}. Please enter a valid number".format(x)
                raise argparse.ArgumentTypeError(msg)          

    
        
# Class that generates or manipulates dates
class Date:
        
    @staticmethod
    def today():
        now = datetime.now()
        date_format = "%Y-%m-%d"
        today = now.strftime(date_format)
        return today 

    @staticmethod
    def yesterday():    
        with open('date.txt') as datefile:  #reading from file because of advance time feature
            currently_set_date_string =  datefile.read()
        date_format = "%Y-%m-%d"
        currently_set_date_dt = datetime.strptime(currently_set_date_string,date_format)
        yesterday = currently_set_date_dt + timedelta(days=-1)
        yesterday =  yesterday.strftime(date_format)
        return yesterday 

    #not the same as today() because date can be advanced
    @staticmethod
    def get_date():    
        with open('date.txt') as datefile:
            currently_set_date =  datefile.read()
        return currently_set_date

    #changes what the system perceives as "today"
    @staticmethod
    def advance_time(x):
        #resets date to the "real today"
        if x == 'reset':
            with open("date.txt", mode='w') as datefile:
                datefile.write(Date.today())
            with open("days_advanced.txt", mode='w') as datefile:
                datefile.write('0')
            print(f"Date set back to today: {Date.today()}")
        else:
            #taking currently set date
            with open("date.txt") as datefile:
                currently_set_date_string =  datefile.read()
            date_format = "%Y-%m-%d"
            currently_set_date_dt = datetime.strptime(currently_set_date_string,date_format)
            x_days = timedelta(days=x)   
            #advancing date by input value
            advanced_date = currently_set_date_dt + x_days
            advanced_date = advanced_date.strftime(date_format)
            #writing the new date into the file that keeps track of it
            with open("date.txt", mode='w') as datefile:
                datefile.write(advanced_date)
            #if date was already advanced, the total number of days are calculated    
            with open('days_advanced.txt') as datefile:
                days_advanced =  int(datefile.read()) + x
            #writing the amount of days advanced into the file that keeps track of them
            #this is needed for the previous step but also for the "natural" advance of time
            #if you want to be 1 day in the future, after midnight it will know to add +1 again
            with open("days_advanced.txt", mode='w') as datefile:
                datefile.write(str(days_advanced))
            print (f'System date set to {advanced_date}.')

    #checks if date needs to be updated in case after 00:00
    @staticmethod
    def check_for_updates():
        with open('date.txt') as datefile:
            currently_set_date =  datefile.read()
        with open('days_advanced.txt') as datefile:
            days_advanced =  datefile.read()
        today = Date.today()
        update = False #first assuming no update needs to be made
        if days_advanced == '0':
            if currently_set_date == today:
                pass
            else:
                update = True
                with open("date.txt", mode='w') as datefile:
                    datefile.write(today)           
        else:
            date_format = "%Y-%m-%d"
            d1 = datetime.strptime(currently_set_date,date_format)  
            d2 = datetime.strptime(today,date_format)
            days_between = str((d1-d2).days)
            if days_between == days_advanced:
                pass
            else:
                update = True
                updated_date = datetime.strptime(today,date_format) + timedelta(days=int(days_advanced))
                updated_date = datetime.strftime(updated_date,date_format)
                with open("date.txt", mode='w') as datefile:
                    datefile.write(str(updated_date))
        return update


class Files:
    @staticmethod
    def check_files_exist():
        current_directory = os.path.dirname(os.path.realpath(__file__))
        path_bought = os.path.join(current_directory, 'bought.csv')
        path_sold = os.path.join(current_directory, 'sold.csv')
        path_date = os.path.join(current_directory, 'date.txt')
        path_advanced = os.path.join(current_directory, 'days_advanced.txt') 
        path_inventory = os.path.join(current_directory, 'inventory.csv') 
        return (file_exists (path_bought) and file_exists (path_sold) and file_exists (path_date) and file_exists (path_advanced) and file_exists (path_inventory)) 
                
    @staticmethod
    def create_files():
        headers_bought = ["bought_id", "product_name", "buy_date", "buy_price", "expiration_date"] 
        headers_sold = ["id", "bought_id", "sell_date", "sell_price"]
        headers_inventory = ["bought_id", "product_name", "buy_price", "expiration_date"] 
        with open('bought.csv', 'w', newline ='') as csvfile: 
            csv_writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=headers_bought) 
            csv_writer.writeheader()  
        with open('sold.csv', 'w', newline ='') as csvfile: 
            csv_writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=headers_sold) 
            csv_writer.writeheader() 
        with open('inventory.csv', 'w', newline ='') as csvfile: 
            csv_writer = csv.DictWriter(csvfile, delimiter=',', fieldnames=headers_inventory) 
            csv_writer.writeheader() 
        with open("date.txt", mode='w') as datefile:
            datefile.write(Date.today())
        with open("days_advanced.txt", mode='w') as datefile:
            datefile.write('0')

    #the "master" inventory
    @staticmethod
    def generate_current_inventory():
        """"Creates a "master" inventory csv containing products with buy_date =< current date, expiration_date >= current date and not sold.
        Gets rewritten every time date is advanced naturally or manually
        Exists so that join between bought csv and sold csv does not have to be performed before each buy attempt
        Every new buy command will also write here and every successful sell command will also remove item from here"""

        #filtering bought file 
        #excluding products bought in the future(because of advance time) or already expired
        bought_df = pd.read_csv('bought.csv', sep=',') 
        bought_filtered = bought_df[(bought_df.buy_date <= Date.get_date()) & (bought_df.expiration_date >= Date.get_date())] 
        
        #filtering the bought csv
        ## excluding products sold after current_date from sold csv
        sold_df = pd.read_csv('sold.csv', sep=',')
        sold_filtered = sold_df[(sold_df.sell_date <= Date.get_date())] 
        ## find all rows without a match from the first file in the second based on id (bought_id).
        sold_items = list(sold_filtered.bought_id)
        bought_filtered = bought_filtered[ ~ bought_filtered.bought_id.isin(sold_items)] #https://www.listendata.com/2019/07/how-to-filter-pandas-dataframe.html Tilde ~ is used to negate the condition. It is equivalent to NOT operator 
        
        #generating the inventory
        ##remove unneccessary column from bought
        inventory = bought_filtered.drop('buy_date', axis = 1)
        ##sorting the data in place. it will be easier to process when sell atempt. we will want to sell the product that expire sooner first and the ones we bought for cheaper first (assuming bigger revenue sooner)
        inventory.sort_values(['product_name', 'expiration_date', 'buy_price'], axis=0, ascending=True, inplace=True) 
        ##writing result to inventory.csv which is used by buy func
        inventory.to_csv('inventory.csv', index = False) 

    #a temp inventory
    @staticmethod
    def generate_inventory_report(date_type):
        """"Creates a temporary inventory csv used by the report function and based on the date parsed.
        Gets pivoted and printed in terminal.
        Copies of this can be created by request with --export optional."""
        date = None
        start_date = None
        end_date = None
        now = None
        if date_type == 'now':
            now = date_type
        elif type(date_type) == str and date_type != 'now':
            date = date_type
        elif type(date_type) == list:
            start_date = date_type[0]
            end_date = date_type[-1]
        sold_df = pd.read_csv('sold.csv', sep=',')
        bought_df = pd.read_csv('bought.csv', sep=',') 
        if now:
            now = str(Date.get_date())
            #1. Filtering bought df 
            ## Keeping just products bought before or on the date and not yet expired
            bought_filtered = bought_df[(bought_df.buy_date <= now) & (bought_df.expiration_date >= now)] 
            #2. Filtering sold df 
            ## Keeping just the products sold BEFORE OR ON the date (what will have to be excluded from bought_df)
            ## The difference between --now and --today is that --now will no longer show items sold today as part of inventory
            sold_filtered = sold_df[(sold_df.sell_date <= now)]  
        #if single date
        elif date:
            #1. Filtering bought df 
            ## Keeping just products bought before or on the date and not yet expired
            bought_filtered = bought_df[(bought_df.buy_date <= date) & (bought_df.expiration_date >= date)]
            #2. Filtering sold df 
            ## Keeping just the products sold BEFORE the date (what will have to be excluded from bought_df)
            ## The difference between --now and --today is that --today will everything that was in today's inventory (including products sold before the time of interogation) 
            sold_filtered = sold_df[(sold_df.sell_date < date)]      
        #if timeframe
        else:
            #1. Filtering bought df 
            ##1.1. Keeping just products bought before or on the end_date and not yet expired
            bought_filtered = bought_df[(bought_df.buy_date <= end_date) & (bought_df.expiration_date >= start_date)] 
            #2. Filtering sold df 
            ## Keeping just the products sold before the start_date (what will have to be excluded from bought_df)
            sold_filtered = sold_df[(sold_df.sell_date < start_date)] 
        #3.  Excluding products already sold from bought file to generate inventory file
        sold_items = sold_filtered['bought_id'].tolist()
        inventory = bought_filtered[ ~ bought_filtered.bought_id.isin(sold_items)]     
        #4. Writing inventory (writing the resulting df back into a csv because otherwise beautifultable doesn't like its header)
        inventory = inventory.groupby(['product_name','buy_price','expiration_date']).size().reset_index(name="count")
        inventory.set_index('product_name', inplace=True) 
        inventory.to_csv('inventory_temp.csv')
        return inventory

    @staticmethod
    def generate_sales_report(date_type):
        #a workaround a pandas warning I do not understand
        warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)
        #joining the bought and sold csv for complete information
        sold_df = pd.read_csv('sold.csv', sep=',') 
        bought_df = pd.read_csv('bought.csv', sep=',')
        report_df = sold_df.join(bought_df.set_index('bought_id'), on='bought_id',how='right')
        #reordering and renaming columns in resulting df
        report_df = report_df.iloc[:,[1,4,5,6,7,0,2,3]]
        report_df.rename(columns = {'id':'sold_id'}, inplace=True)
        report_df.set_index('bought_id', inplace=True) 
        #filtering by date
        date = None
        start_date = None
        end_date = None
        if date_type == 'now':
            date = Date.get_date()
        elif type(date_type) == str and date_type != 'now':
            date = date_type
        elif type(date_type) == list:
            start_date = date_type[0]
            end_date = date_type[-1]
        if date:
            report_df_filtered = report_df[
                                        (report_df.buy_date <= date) & 
                                        (report_df.expiration_date >= date) &
                                        ((report_df.sell_date == date) | (pd.isnull(report_df.sell_date)))
                                        ]
        else:
            report_df_filtered = report_df[
                                            (report_df.buy_date <= end_date) & 
                                            (report_df.expiration_date >= start_date) & 
                                            (((report_df.sell_date >= start_date) & (report_df.sell_date <= end_date)) | (pd.isnull(report_df.sell_date)))
                                            ]
        #adding a status column
        conditions = [
                        (~pd.isnull(report_df_filtered.sell_date)),
                        ((((pd.isnull(report_df_filtered.sell_date)) & (report_df_filtered['expiration_date'] == date))) | ((pd.isnull(report_df_filtered.sell_date)) & ((report_df_filtered['expiration_date'] >= start_date) & (report_df_filtered['expiration_date'] <= end_date)))),
                        (((pd.isnull(report_df_filtered.sell_date)) & (report_df_filtered['expiration_date'] > date)) | ((pd.isnull(report_df_filtered.sell_date)) & (report_df_filtered['expiration_date'] >= end_date)))
                        ]
        values = ['sold','expired','in inventory']
        report_df_filtered['status'] = np.select(conditions,values)
        report_df_filtered = report_df_filtered.sort_values('status', key=lambda s: s.apply(['sold', 'expired', 'in inventory'].index))
        report_df_filtered['sell_price'] = np.where(report_df_filtered['status']== 'expired', 0, report_df_filtered['sell_price'])
        report_df_filtered.loc['total']= report_df_filtered.sum(numeric_only=True) 
        report_df_filtered.loc[report_df_filtered.index[-1], ('product_name', 'buy_date', 'expiration_date', 'sold_id', 'sell_date', 'status')] = ''
        report_df_filtered = report_df_filtered.round(decimals=2)
        report_df_filtered.to_csv('sales_report_temp.csv')
        report_df = report_df_filtered
        return report_df     

    @staticmethod
    def export_csv(report_type, date_type):
        date = None
        start_date = None
        end_date = None
        if date_type == 'now':
            date = Date.get_date()
        elif type(date_type) == str and date_type != 'now':
            date = date_type
        elif type(date_type) == list:
            start_date = date_type[0]
            end_date = date_type[-1]
        if report_type == 'inventory':
            df = pd.read_csv('inventory_temp.csv')
            df.set_index('product_name', inplace=True) 
            if date:
                if os.path.exists(f'inventory_{date}.csv'):
                    os.remove(f'inventory_{date}.csv')
                df.to_csv(f'inventory_{date}.csv')
            else:
                if os.path.exists(f'inventory_{start_date}_{end_date}.csv'):
                    os.remove(f'inventory_{start_date}_{end_date}.csv')
                df.to_csv(f'inventory_{start_date}_{end_date}.csv')
        if report_type == 'revenue' or 'profit':
            df = pd.read_csv('sales_report_temp.csv')
            df.set_index('bought_id', inplace=True) 
            if date:
                if os.path.exists(f'sales_report_{date}.csv'):
                    os.remove(f'sales_report_{date}.csv')
                df.to_csv(f'sales_report_{date}.csv')
            else:
                if os.path.exists(f'sales_report_{start_date}_{end_date}.csv'):
                    os.remove(f'sales_report_{start_date}_{end_date}.csv')
                df.to_csv(f'sales_report_{start_date}_{end_date}.csv')



  
# Files.generate_sales_report(['2022-11-26', '2022-11-30'])
# Files.generate_sales_report('2022-11-27')

