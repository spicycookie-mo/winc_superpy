# Report

## 1. Inventory

Super.py has two functions for generating the inventory and two different resulting csv files.
### The "master" inventory
- Files.generate_current_inventory() -> inventory.csv.
- Quick: eliminates the need to join and filter the sold and bought files for each sell attempt.
- Any expired products are removed daily.
- Each buy command also adds the newly bought product(s).
- Each sell command removes the sold products.

#### In tools:

	def generate_current_inventory():
	
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

#### In parser:

	if Date.check_for_updates():
        Files.generate_current_inventory() 
    
    if args.advance_time:
        Date.advance_time(args.advance_time) 
        

### The inventory report
- Files.generate_inventory_report(date_type) -> inventory_temp.csv
- Used for the report parser 
- Allows for a custom selection of an inventory snapshot by date (now/today/yesterday/custom date/timeframe)
- Returns data easy to pivot and use in charts.

#### In tools:

	def generate_inventory_report(date_type):
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

#### In report subparser:

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
                    if type(args.date) == str:
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

## 2. tools_rich
I wanted to be able to print an emoji of the product sold/bought after each succesful attemp IF there is an emoji for that product, and a thumbs up emoji if there isn't.

Obstacle: rich has it built in to print :[missing emoji name]: instead of nothing or something else.

Foud the code behind the module and did not manage to change it, but I used it to create a list of all available emojis in the library and then search though it. 

#### In tools_rich:

	def find_emoji(emoji):
		emojis_list = []

        for name in sorted(EMOJI.keys()):
            if "\u200D" not in name:
                emojis_list.append(name)
        # print(emojis_list)        
        if emoji in emojis_list:
            return True
        else:
            return False

#### In subparser func:

	if find_emoji(product_name):
		emoji = product_name
	else:
		emoji = 'thumbsup'

## 3. Profit
Calculating profit was a chalenge - clearly I do not master these accounting terms well.
Af first, I saw it as revenue - cost of goods sold, but then I thought: what if I also had some products that expired? Should I also substract that cost. What about everything I've already spent on inventory? 

That's how I came to know that there are different types of profits. Chose an implementation that satisfies all tastes: 

📊 Your profit for 2022-01-01 - 2022-09-17 is: 250.4 📆
You had a revenue of 627.5.
Costs of the goods sold were of 377.1
You lost 39.8 due to depreciation.
You still have 218.5 invested in stock.
Overall your balance is of -7.9

Key to that was generate_sales_report(date_type) and the aggregations within the report func.

#### In tools:

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


#### In subparser report:

	revenue = (report_df.loc[report_df["status"] == 'sold', "sell_price"].sum()).round(decimals=2)
                costs_goods_sold =  (report_df.loc[report_df["status"] == 'sold', "buy_price"].sum()).round(decimals=2)
                loss = (report_df.loc[report_df["status"] == 'expired', "buy_price"].sum()).round(decimals=2)
                investment = (report_df.loc[report_df["status"] == 'in inventory', "buy_price"].sum()).round(decimals=2)
                profit = (revenue - costs_goods_sold).round(decimals=2)
                balance = (revenue - costs_goods_sold - loss - investment).round(decimals=2)

## Fail: Plotly
I chose plotly over matplotlib because it has more extensive and explicit documentation and because I was able to find a lot more examples on forums. I regret it. It'is not really easy to customize and often it times out and only works from the second try. 

## Fail: Pytest
If was difficult to understand how to call main from a different file. At that point I had everything under a main() function. It took a while but then I broke it in half and added a default argument for it.

I stll did not understand if there is a was for pytest to test my functions without actually calling them because currently running pytest will impact my files and reset the date, buy and sell products.

I also did not get what exactly I should be asserting when testing the parser so I started by testing the functions that validate the type of the arguments the parser receives (test_tools) to confirm it will not accept invalid arguments. 

Then to test the parser itself I found a way to check which output it prints with various arguments.