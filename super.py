import argparse
import csv
import pandas as pd 
from tools import Date as Date
from tools import Type as Type
from tools import Files as Files
import prettytable
from prettytable import from_csv
from prettytable import DOUBLE_BORDER
from tools_rich import console as console
from tools_rich import find_emoji
from tools_rich import rich_style
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import sys


# Do not change these lines.
__winc_id__ = "a2bc36ea784242e4989deb157d527ba0"
__human_name__ = "superpy"


# Your code below this line.
  
    
def parse_args(args=sys.argv[1:]):

    
####################################
## Creating sub-command functions ## 
####################################

    def buy(args):
        product_name = args.name
        price = args.price
        expiration_date = args.expiration
        buy_date = Date.get_date() #reading date.txt file instead of using Date.current_date() to accomodate changing date
        quantity = args.quantity
        with console.status("On it...", spinner="runner"):   
            for i in range(quantity):
                # read file, create list of rows, then count number of rows, to generate id of product
                reader = csv.reader(open('bought.csv'))
                id = len(list(reader))
                # opening file again in append mode and add new line with newly generated id and data from buy parser
                with open('bought.csv', 'a+', newline ='')  as csvfile: 
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([id, product_name , buy_date, price , expiration_date])     
                # open inventory file and add product
                with open('inventory.csv', 'a+', newline ='')  as csvfile: 
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow([id, product_name , price , expiration_date])
            #using a default emoji if there is no emoji for the product
            if find_emoji(product_name):
                emoji = product_name
            else:
                emoji = 'thumbsup'
            if price == 0:
                print (f":flexed_biceps: [green]Got that for free? Good for you![green] :{emoji}:")
            else:
                console.print(f":thumbsup: [green]OK[/green] :{emoji}: X {quantity}", )
  
            
    def sell(args):
        product_name = args.name
        sell_price = args.price
        quantity_request = args.quantity
        with console.status("On it...", spinner="runner"):   
            # search inventory for product 
            with open("inventory.csv", 'r') as icsv:
                reader = csv.DictReader(icsv)
                #creating a temp dict with bought_id as keys and expiration dates as values
                #used to later sort and select the product that expires soonest to sell first
                products = {} 
                for row in reader:
                    if row['product_name'] == product_name: 
                            products[row['bought_id']] = row['expiration_date']
                #if product in inventory
                if products:
                    quantity_offer = len(products) 
                    #if enough products in inventory
                    if quantity_request <= quantity_offer:
                        for i in range(quantity_request):
                            # select product which expires soonest 
                            bought_id = (sorted(products.items(), key=lambda item: item[1])[0][0])   
                            # remove product from the temp dict
                            products.pop(f'{bought_id}')                        
                            sell_date = open('date.txt', 'r').read()
                            # generate sell_id
                            reader = csv.reader(open('sold.csv'))
                            sold_id = len(list(reader))
                            with open("sold.csv", 'a+', newline = '') as csvfile:
                                #register buy in bought.csv
                                csv_writer = csv.writer(csvfile)
                                csv_writer.writerow([sold_id, bought_id, sell_date, sell_price])
                            #register sell in inventory (remove)
                            df = pd.read_csv('inventory.csv')
                            df.set_index('bought_id', inplace = True)
                            df = df.drop(int(bought_id))
                            df.to_csv('inventory.csv')
                        #using a default emoji if there is not emoji for the product
                        if find_emoji(product_name):
                            emoji = product_name
                        else:
                            emoji = 'thumbsup'
                        console.print(f':thumbsup: [green]OK[/green] :{emoji}: X {quantity_request}')
                    #if not enough products in inventory
                    else:
                        if find_emoji(product_name):
                            emoji = product_name
                        else:
                            emoji = 'grimacing'
                        console.print(f':warning: [red]Oops! We only have {quantity_offer} of those.[/red] :{emoji}:')  
                #if product not in inventory
                else:
                    if find_emoji(product_name):
                        emoji = product_name
                    else:
                        emoji = 'scream'
                    console.print (f':thumbsdown: [red]Product not available.[/red] :{emoji}: ')
                        

    def report(args):
        with console.status("On it...", spinner="runner"): 
            #one extra date validation that argparse does not support 
            if type(args.date) == list:
                if not Type.valid_timeframe(args.date):
                    console.print (':warning: Error: End date must be >= start date')  
                    exit()                 
            if args.report_type == 'inventory':
                #generating the temp inventory file based on parsed date
                Files.generate_inventory_report(args.date)  
                #printing the message     
                if args.date == Date.get_date():
                    console.print (f""":information_desk_person: Today's inventory {args.date} :calendar:""")
                elif args.date == Date.yesterday():
                    console.print (f""":information_desk_person: Yesterday's inventory {args.date} :calendar:""")
                elif type(args.date) == list:
                    console.print (f""":information_desk_person: Your inventory for {args.date[0]} - {args.date[-1]} :calendar:""")
                else:
                    console.print (f""":information_desk_person: Your inventory for {args.date} :calendar:""")
                #printing the table
                with open ('inventory_temp.csv') as inv_print:
                    inventory = prettytable.from_csv(inv_print) #using this instead of beautifultable because it prints header of empty table
                    inventory.set_style(DOUBLE_BORDER)
                    print(inventory)
                #if export is parsed, create csv
                if args.export:
                    Files.export_csv(args.report_type, args.date)
                    if args.date == 'now':
                        console.print(f":information: Your export is ready: inventory_{Date.get_date()}.csv :inbox_tray:")
                    elif type(args.date) == str and args.date != 'now':
                        console.print(f":information: Your export is ready: inventory_{args.date}.csv :inbox_tray:")
                    else:
                        console.print(f":information: Your export is ready: inventory_{args.date[0]}_{args.date[-1]}.csv :inbox_tray:")
                #inventory gets printed anyway
                if args.print:
                    pass
                #if chart is parsed, show chart
                if args.chart:
                    inventory_df = pd.read_csv('inventory_temp.csv')
                    fig1 = px.bar(inventory_df, x="product_name", y="count", color="buy_price", title="Products in invenory by name and purchase price")
                    fig1.show()

            elif args.report_type == 'revenue' or args.report_type == 'profit':
                #generating the master report file bases on the dates parsed
                report_df = Files.generate_sales_report(args.date)  # same as report_df = pd.read_csv('sales_report_temp.csv') 
                #calculating the variables           
                revenue = (report_df.loc[report_df["status"] == 'sold', "sell_price"].sum()).round(decimals=2)
                costs_goods_sold =  (report_df.loc[report_df["status"] == 'sold', "buy_price"].sum()).round(decimals=2)
                loss = (report_df.loc[report_df["status"] == 'expired', "buy_price"].sum()).round(decimals=2)
                investment = (report_df.loc[report_df["status"] == 'in inventory', "buy_price"].sum()).round(decimals=2)
                profit = (revenue - costs_goods_sold).round(decimals=2)
                balance = (revenue - costs_goods_sold - loss - investment).round(decimals=2)
                #printing the message
                if args.report_type == 'revenue':
                    if args.date == 'now':
                        console.print (f""":bar_chart: Today's revenue so far is {revenue} :calendar:""")
                    elif args.date == Date.get_date():
                        console.print (f""":bar_chart: Today's revenue so far is {revenue} :calendar:""")
                    elif args.date == Date.yesterday():
                        console.print (f""":bar_chart: Yesterday's revenue is {revenue} :calendar:""")
                    elif type(args.date) == list:
                        console.print(f':bar_chart: Your revenue for {args.date[0]} - {args.date[-1]} is: {revenue} :calendar:')
                    else:
                        console.print (f':bar_chart: Your revenue for {args.date} is {revenue} :calendar:')  
                if args.report_type == 'profit':
                    if args.date == 'now':
                        console.print (f""":bar_chart: Today's profit so far is [{rich_style(profit)}]{profit}[/{rich_style(profit)}] :calendar:""")
                    elif args.date == Date.get_date():
                        console.print (f""":bar_chart: Today's profit so far is [{rich_style(profit)}]{profit}[/{rich_style(profit)}] :calendar:""")
                    elif args.date == Date.yesterday():
                        console.print (f""":bar_chart: Yesterday's profit is [{rich_style(profit)}]{profit}[/{rich_style(profit)}] :calendar:""")
                    elif type(args.date) == list:
                        console.print(f':bar_chart: Your profit for {args.date[0]} - {args.date[-1]} is: [{rich_style(profit)}]{profit}[/{rich_style(profit)}] :calendar:')
                    else:
                        console.print (f':bar_chart: Your profit for {args.date} is [{rich_style(profit)}]{profit}[/{rich_style(profit)}] :calendar:')  
                    console.print(f"You had a revenue of [green]{revenue}[/green]. \nCosts of the goods sold were of [blue]{costs_goods_sold}[/blue] \nYou lost [red]{loss}[/red] due to depreciation. \nYou still have [blue]{investment}[/blue] invested in stock. \nOverall your balance is of [{rich_style(balance)}]{balance}[/{rich_style(balance)}] \n""")
                #if print is parsed, the report is printed in terminal
                if args.print:       
                    with open ('sales_report_temp.csv') as report_print:
                        report_print = prettytable.from_csv(report_print) #using this instead of beautifultable because it prints header of empty table
                        report_print.set_style(DOUBLE_BORDER)
                        print(report_print)   
                #if export is parsed, the report is saved as csv
                if args.export:
                    Files.export_csv(args.report_type, args.date)
                    if args.date == 'now':
                        console.print(f":information: Your export is ready: sales_report_{Date.get_date()}.csv :inbox_tray:")
                    elif type(args.date) == str and type(args.date) != 'now':
                        console.print(f":information: Your export is ready: sales_report_{args.date}.csv :inbox_tray:")
                    else:
                        console.print(f":information: Your export is ready: sales_report_{args.date[0]}_{args.date[-1]}.csv :inbox_tray:")
                #if chart is parsed
                if args.chart:
                    #if single date, bar charts
                    if type(args.date) == str:
                        #preparing data
                        ##dropping total row
                        report_df = report_df.iloc[:-1].reset_index('bought_id')
                        ##splitting by status
                        sales_df = report_df[(report_df["status"] == 'sold')]
                        chart_df_sales = sales_df.groupby(['product_name']).agg(
                                                                            volume = ('sell_price', 'count'),
                                                                            revenue = ('sell_price', 'sum')).reset_index('product_name')
                        depreciation_df = report_df[(report_df["status"] == 'expired')]
                        chart_df_depreciation = depreciation_df.groupby(['product_name']).agg(
                                                                            volume = ('buy_price', 'count'),
                                                                            loss = ('buy_price', 'sum')).reset_index('product_name')
                        #creating the subplots
                        fig = make_subplots(rows=2, cols=2, subplot_titles=("Sales volume by product", "Revenue by product","Depreciation volume by product", "Depreciation costs by product"))
                        fig.add_trace(go.Bar(x=chart_df_sales['product_name'].tolist(), y=chart_df_sales['volume'].tolist()
                                        ,name ='Number of products sold'),
                                        row=1, col=1)
                        fig.add_trace(go.Bar(x=chart_df_sales['product_name'].tolist(), y=chart_df_sales['revenue'].tolist()
                                        ,name ='Revenue generated'),
                                        row=1, col=2)
                        fig.add_trace(go.Bar(x=chart_df_depreciation['product_name'].tolist(), y=chart_df_depreciation['volume'].tolist()
                                        ,name ='Number of products expired'),
                                        row=2, col=1)
                        fig.add_trace(go.Bar(x=chart_df_depreciation['product_name'].tolist(), y=chart_df_depreciation['loss'].tolist()
                                        ,name ='Loss generated'),
                                        row=2, col=2)
                        fig.update_layout(title_text=f"Revenue and costs by product for {args.date}")
                        fig.show()
                    #if interval, line plot
                    elif type(args.date) == list:
                        #filtering data
                        chart_df = report_df[report_df["status"].isin(['sold','expired'])]                   
                        #creating single date column which takes sold_date if product was sold or exp_date if product expired
                        conditions = [
                            (chart_df['status']=='sold'),
                            (chart_df['status']=='expired')
                            ]
                        values = [chart_df['sell_date'], chart_df['expiration_date']]
                        chart_df['date'] = np.select(conditions,values)
                        #creating a count column with 1 all the way, much cleaner than using two types of agg in pivot
                        chart_df['count'] = 1
                        #pivoting the data
                        report_pivot = pd.pivot_table(chart_df, index=['date'], 
                                                    columns=['status'],
                                                    values=['buy_price','sell_price', 'count'],
                                                    aggfunc=(np.sum)).reset_index()
                        #merging two rows (column name and value) into single header
                        report_pivot.columns = ['_'.join(str(s).strip() for s in col if s) for col in report_pivot.columns]
                        report_pivot = report_pivot.rename(columns={'buy_price_expired':'Loss_depreciation', 'buy_price_sold':'Costs_goods_sold', 'count_expired':'Volume_products_expired', 'count_sold':'Volume_products_sold', 'sell_price_sold':'Revenue'})
                        del report_pivot['sell_price_expired']
                        #replacing missing values with 0
                        report_pivot = report_pivot.fillna(0)
                        #adding the calculated Profit column
                        report_pivot['Profit'] = report_pivot['Revenue'] - report_pivot['Costs_goods_sold'] - report_pivot['Loss_depreciation']
                        #creating two subplots: same x axis (date); y axis unit = currency / volume
                        fig = make_subplots(rows = 2, cols = 1, subplot_titles=('Financial',  'Volume'))
                        #each line/trace has to be set up separately
                        for i in range(4):
                            col_names = ['Revenue', 'Profit' , 'Costs_goods_sold', 'Loss_depreciation']
                            col_name = col_names[i]
                            fig.add_trace(go.Scatter(x=report_pivot['date'], y=report_pivot[col_name],
                            mode='lines', 
                            name=col_name), row=1, col=1)
                        for i in range(2):
                            col_names = ['Volume_products_expired',  'Volume_products_sold']
                            col_name = col_names[i]
                            fig.add_trace(go.Scatter(x=report_pivot['date'], y=report_pivot[col_name],
                            mode='lines', 
                            name=col_name), row=2, col=1)
                        fig.update_layout(title_text=f"Sales report for {args.date[0]}-{args.date[-1]}")
                        fig.show()

                                                        
#################################        
## Create the top-level parser ##
#################################

    parser = argparse.ArgumentParser(
        prog = 'SuperPy', usage = '%(prog)s',
        description = f'########## Welcome to SuperPy, a friendly supermarket inventory system! ##########', 
        epilog = f'########## Hope you enjoy! ##########', 
        allow_abbrev=False)

    #the only optional argument outside of subparsers    
    parser.add_argument('--advance_time', 
                        type = Type.valid_days, 
                        help = "This command helps you change the internal date of the software with +/- x days. Useful for commiting fraud. Use wisely"
                        )
    
    # create subparsers object with add_subparsers() method
    subparsers = parser.add_subparsers(title='actions')

    # create the parser for the "buy" command
    parser_buy = subparsers.add_parser('buy', 
                                        help = 'Stock up supermarket. Run buy command followed by --help for details')
    parser_buy.add_argument('--name', 
                            type = str, 
                            help = 'What is the name of the product you are buying?', 
                            required = True
                            )
    parser_buy.add_argument('--price', 
                            type = Type.valid_price_buy, 
                            help = 'What is the price of the product? Please insert price using two decimals (e.g. 2.34)', 
                            required = True
                            )
    parser_buy.add_argument('--expiration', 
                            type = Type.valid_date_expiration, 
                            help = 'What is the expiration date of the product? Please insert date in format YYYY-MM-dd', 
                            required = True
                            )
    parser_buy.add_argument('--quantity', 
                            type=Type.valid_quantity,
                            default=1, 
                            nargs='?', 
                            help = "How many of those would you like?"
                            )
    parser_buy.set_defaults(func=buy) # call to set_defaults() so that the buy subparser knows to execute the buy function

    # create the parser for the sell command
    parser_sell = subparsers.add_parser('sell', 
                                        help = "Sell your products. Run sell command followed by --help for details")
    parser_sell.add_argument('--name', 
                            type = str, 
                            help = 'What is the name of the product you are selling?', 
                            required = True
                            )
    parser_sell.add_argument('--price', 
                            type = Type.valid_price_sell, 
                            help = 'How much are you selling your product for? Please insert price using two decimals (e.g. 2.34)',
                            required = True
                            )
    parser_sell.add_argument('--quantity',  
                            type=Type.valid_quantity, 
                            default=1, 
                            nargs='?',
                            help = "How many of those are you selling?"
                            )
    parser_sell.set_defaults(func=sell) # call to set_defaults() so that the buy subparser knows to execute the sell function
    
    # create the parser for the report command
    parser_report = subparsers.add_parser('report', 
                                        help = "Print reports on inventory, revenue or profit on a set date. Run report command followed by --help for details")
    group1 = parser_report.add_argument_group('Report types' , 'Choose one option')
    group1.add_argument(choices=['inventory', 'revenue', 'profit'], 
                        dest='report_type',  
                        help = "Specify the type of report you would like: inventory / revenue / profit"
                        )
    group2 = parser_report.add_mutually_exclusive_group(required=True)
    group2.add_argument('--now', 
                        action='store_const', 
                        const='now', 
                        dest='date', 
                        help='Use this option if you would like a report for now'
                        )
    group2.add_argument('--today', 
                        action='store_const', 
                        const=Date.get_date(), 
                        dest='date', 
                        help='Use this option if you would like a report for today'
                        )
    group2.add_argument('--yesterday', 
                        action='store_const', 
                        const=Date.yesterday(), 
                        dest='date', 
                        help='Use this option if you would like a report for yesterday'
                        )
    group2.add_argument('--date', 
                        type=Type.valid_date_report, 
                        dest='date', 
                        help='Use this option if you would like to input a custom date. Please insert date in format YYYY-MM-dd.'
                        )
    group2.add_argument('--timeframe', 
                        type=Type.valid_date_report, 
                        nargs=2,  
                        dest='date', 
                        help="Use this option if you would like to specify a custom timeframe. Please insert a start date and and end date in format YYYY-MM-dd."
                        )
    group3 = parser_report.add_argument_group('Files and data vizualization', )
    group3.add_argument('--export', 
                        action='store_true', 
                        help = 'Use this command if you would also like to save the report in a csv format'
                        )
    group3.add_argument('--print', 
                        action='store_true', 
                        help = 'Use this command if you would also like to print the report on the screen'
                        )
    group3.add_argument('--chart', 
                        action='store_true', 
                        help = 'Use this command for data vizualization'
                        )
    parser_report.set_defaults(func=report)
    
    return parser.parse_args(args)
    
#####################################################    
## Parsing the arguments and calling the functions ##
#####################################################

def main(args=sys.argv[1:]):    
    #check for necesary files
    if not Files.check_files_exist():
        Files.create_files() 
    #check if date needs update (+1 after 00:00)
    if Date.check_for_updates():
        Files.generate_current_inventory() 
    #so I can call function from test file as well (does not take sys.argv)
    args = parse_args(args)
    # print(args)

    if args.advance_time:
        Date.advance_time(args.advance_time) 
        Files.generate_current_inventory()
    else:
        try: #this is a workaround to a "bug in the Python 3 version of argparse. Python 2, if the script is called with no arguments whatsoever (i.e., no subcommand), it exits cleanly with "error: too few arguments". In Python3, however, you get an unhandled AttributeError." 
            args.func(args)
        except AttributeError:
            print('You seem lost. Use the --help command')
        #     parser.print_help()  #doesn't work anymore since breaking main()
    
    # return sys.stdout

 
        
if __name__ == "__main__":
    main()
    
    # main(['buy', '--name', 'milk', '--price', '1', '--expiration', '2022-11-01'])
    
  


