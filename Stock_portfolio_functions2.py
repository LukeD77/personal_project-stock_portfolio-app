#!/usr/bin/env python
# coding: utf-8

### Function list for stock portfolio project
# 1. plot_stock_prices2
# 2. get_updated_stock_info
# 3. stock_analysis_tab_data_retriever
# 4. stock_analysis_tab_data_retreiver_thread
# 5. draw_figure
# 6. close_figure
# 7. portfolio_pie_plot
# 8. plot_portfolio_stock
# 9. blank_stock_portfolio_performance_plot
# 10. update_portfolio_text


def plot_stock_prices2(period='1d', interval='1m', stock='pick_random_stock'):
    import pandas as pd
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    import PySimpleGUI as sg
    import yfinance as yfi
    import numpy as np
    import pickle
    from PIL import Image

    stock_info_dict = pickle.load(open('stock_info_dictionary.p','rb'))

    if period == '1d':
        period_formated = 'Today'
    elif period == '5d':
        period_formated = '1 Week'
    elif period == '1mo':
        period_formated = '1 Month'
    elif period == '6mo':
        period_formated = '6 Months'
    elif period == '1y':
        period_formated = '1 Year'

    ### Download data of random stock if default or chosen stock. If no data, will cause zero_division_error and rety w new stock
    if stock == 'pick_random_stock':
        dow_df = pd.DataFrame()
        while len(dow_df) == 0:
            try:
                random_stock_index = np.random.randint(low=0,high=len(stock_info_dict))
                random_stock = list(stock_info_dict.keys())[random_stock_index]
                dow_df = yfi.ticker.Ticker(random_stock).history(period=period, interval = interval)
                stock = random_stock
                1/len(dow_df)
            except ZeroDivisionError:
                print('retrying')
                continue
    else:
        try:
            dow_df = yfi.ticker.Ticker(stock).history(period=period, interval = interval)
        except len(dow_df) == 0:
            sg.popup(stock_error_text, no_titlebar=True,grab_anywhere=True, font=14, background_color='red', keep_on_top=True)
            return


    ### Get the change in the stock
    start = dow_df['Open'][0]
    end = dow_df['Close'][-1]
    difference = end-start
    per_difference = (end-start)/start*100
    if per_difference < 0:
        diff_neg = True
    else:
        diff_neg = False

    ### Change datetime object so plots x-tick labels correctly by removing time zone and
    ### then making string object so doesn't plot gap days
    dow_df = dow_df.reset_index()
    i=0
    for a in dow_df['Datetime']:
        dow_df['Datetime'].iloc[i] = a.replace(tzinfo=None)
        i+=1
    dow_df = dow_df.set_index('Datetime')

    date_str_list = []
    i=0

    for a in dow_df.index:
        date_str_list.append(str(dow_df.index[i]).split(' ')[0] + '\n' + str(dow_df.index[i]).split(' ')[1])
        i+=1

    dow_df['date_str'] = date_str_list
    dow_df = dow_df.reset_index()
    dow_df = dow_df.set_index('date_str')

    ### Make a preplot to get the y-limit values in order for the shadow under the plot to work
    fig = plt.figure(figsize=(9,6))
    ax = fig.add_subplot()
    ax.plot(dow_df.index, dow_df['Open'],c='#08F7FE')
    ylim = ax.get_ylim()
    plt.close()

    ### Making the plot
    ### afterglow code source - https://towardsdatascience.com/cyberpunk-style-with-matplotlib-f47404c9d4c5
    fig = plt.figure(figsize=(10,7))
    ax = fig.add_subplot()
    ax.plot(dow_df.index, dow_df['Open'],c='#08F7FE')
    plt.ylim(ylim)

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    ### redrawing lines multiple times to create glow effect
    n_lines = 10
    diff_linewidth = 1.55
    alpha_value = 0.03

    for n in range(1, n_lines+1):
        ax.plot(dow_df.index, dow_df['Open'],
               linewidth = 2+(diff_linewidth*n),
               alpha = alpha_value,
               c='#08F7FE')

    ### Color the areas below the lines:
    ax.fill_between(x=dow_df.index,
                        y1=dow_df['Open'],
                        y2=[0] * len(dow_df),
                        color='#08F7FE',
                        alpha=0.2)

    plt.ylabel('Stock Value', fontsize=16, color='white')
    plt.xlabel('Date',fontsize=16, color='white')
    plt.xticks(rotation=45, fontsize=14, color='white')
    plt.yticks(fontsize=14, color='white')

    random_stock_short_name = stock_info_dict[stock]['shortName']
    suptitle = random_stock_short_name + ' (' + stock + ') -- ' + period_formated
    plt.suptitle(suptitle ,fontsize=24, color='white')

    if diff_neg:
        title = f'{np.round(difference,decimals = 2)} ({np.round(per_difference, decimals=2)}%)'
        plt.title(title, fontsize=20, color='red')
    else:
        title = f'+{np.round(difference,decimals = 2)} (+{np.round(per_difference, decimals=2)}%)'
        plt.title(title, fontsize=20, color='green')


    # ### Putting green or red arrow on image
    # if diff_neg == False:
    #     img_path = ".\\green_triangle_black_background.jpg"
    #     img = Image.open(img_path)
    #     img = img.resize((17,17))
    #     img_array = np.asarray(img)
    #     fig.figimage(img_array, origin='upper',xo=440 + len(title)*4.5, yo=512, alpha=0.8)
    # else:
    #     img_path = ".\\red_triangle_black_background.jpg"
    #     img = Image.open(img_path)
    #     img = img.resize((17,17))
    #     img_array = np.asarray(img)
    #     fig.figimage(img_array, origin='lower',xo=440 + len(title)*4.5, yo=512, alpha=0.8)

    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    plt.grid(axis='both', linestyle='--', linewidth=1,color='gray', alpha=0.5)

    ax.set_facecolor('black')
    fig.set_facecolor('black')
    plt.tight_layout()
    plt.close()
    return stock, fig


### get_stock_info from the ticker, is up to date. Have a faster version where already downloaded info data in dictionary
def get_updated_stock_info(stock):
    import yfinance as yfi
    import pandas as pd

    info = yfi.ticker.Ticker(stock).get_info()
    description = info['longBusinessSummary']
    city = info['city']
    state = info['state']
    country = info['country']
    num_employ = info['fullTimeEmployees']
    website = info['website']
    industry = info['industry']
    total_cash = info['totalCash']
    shortname = info['shortName']
    longname = info['longName']
    profit_margin = info['profitMargins']
    target_low_price = info['targetLowPrice']
    revenue_per_share = info['revenuePerShare']
    stock = stock

    data = pd.DataFrame([[description, city, state, country, num_employ, website, industry, total_cash, shortname,
                         longname, profit_margin, target_low_price, revenue_per_share, stock]],
                        columns=['description','city','state','country','num_employ','website','industry','total_cash',
                                'shortname','longname','profit_margin','target_low_price','revenue_per_share','stock'])
    return data
### NEED TO SPEED UP. CAN CHANGE LOOPS TO VERCTORIZING OR .APPLY()

### stock_analysis_tab_data_retriever
def stock_analysis_tab_data_retriever(stock_key):
    import yfinance as yfi
    import pandas as pd

    try:
        recommendation_df = yfi.ticker.Ticker(stock_key).get_recommendations().reset_index()
        stock_data = yfi.ticker.Ticker(stock_key).history(period='1mo',interval='5m')
        stock_lowest = np.sort(stock_data['Low'])[0]
        stock_highest = np.sort(stock_data['High'])[-1]
        return stock_data, stock_lowest, stock_highest, recommendation_df
    except:  ### Can be a str error or an exception that has been defined. Changes with the time so need a catch all since idk whta error will be thrown at what time
        print('Analysis retrieval failed')
        return 'Analysis retrieval failed', '_', '_', '_'



### stock analysis tabe data retriever with multithreading
def stock_analysis_tab_data_retriever_thread(analysis_indicator, mainthread_queue, stock_key):
    '''Function to get the stock analysis data but do so with multithreading.'''
    import yfinance as yfi
    import pandas as pd
    import numpy as np

    try:
        stock_data = yfi.ticker.Ticker(stock_key).history(period='1mo',interval='5m')
        stock_lowest = np.sort(stock_data['Low'])[0]
        stock_highest = np.sort(stock_data['High'])[-1]
        recommendation_df = yfi.ticker.Ticker(stock_key).get_recommendations().reset_index()
        print('thread finished')
        mainthread_queue.put([stock_data,stock_lowest,stock_highest, recommendation_df])
        return 'Success'
    except Exception:
        print('Analysis retrieval failed')
        return 'Analysis retrieval failed'



### draw_figure
def draw_figure(canvas, figure):
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates

    matplotlib.use("TkAgg")
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

### delete figure
def close_figure(figure_canvas_agg):
    import matplotlib.pyplot as plt
    figure_canvas_agg.get_tk_widget().forget()
    plt.close('all')


### Portfolio pie plot
def portfolio_pie_plot():
    '''Plots a donut chart of the stocks owned'''
    import numpy as np
    import matplotlib.pyplot as plt
    import yfinance as yfi
    import pandas as pd
    import pickle

    with open('stock_portfolio_dict_TEST.p', 'rb') as handle:
        portfolio_dict = pickle.load(handle)

    with open('money_made.txt','r', encoding='utf-8') as file:
        money_made = float(file.read())

    if len(portfolio_dict) == 0:
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot()
        ax.pie([1], labels = [''], colors=['gray'],
                  pctdistance=0.85, textprops={'color':'white', 'size':14})

        center_circle = plt.Circle((0, 0), 0.70, fc='black')
        fig = plt.gcf()
        fig.gca().add_artist(center_circle)

        plt.annotate(f'Total value of portfolio \n${0}', (0,0), color='white', fontsize=18,
                    ha='center')
        plt.title('Your stock portfolio', fontsize=18, color='white')

        ax.set_facecolor('black')
        fig.set_facecolor('black')
        plt.tight_layout()
        plt.close()
        return fig

    else:
        portfolio_price_list = []
        portfolio_stock_sym_list = []
        portfolio_stock_list = []
        portfolio_original_total = 0
        for stock in portfolio_dict:
            stock_sym = stock.split('~')[0]
            portfolio_price_list.append(yfi.Ticker(stock_sym).history().iloc[-1]['Close']*portfolio_dict[stock]['num_stocks'])
            portfolio_stock_sym_list.append(stock_sym)
            portfolio_stock_list.append(stock)
            portfolio_original_total =  portfolio_original_total + portfolio_dict[stock]['price_bought_at']*float(portfolio_dict[stock]['num_stocks'])


        fig = plt.figure(figsize=(7,7))
        ax = fig.add_subplot()
        ax.pie(portfolio_price_list, labels = portfolio_stock_list, autopct='%1.1f%%',
                  pctdistance=0.85, explode =[(0.05)]*len(portfolio_price_list) , textprops={'color':'white', 'size':14})

        center_circle = plt.Circle((0, 0), 0.70, fc='black')
        fig = plt.gcf()
        fig.gca().add_artist(center_circle)


        portfolio_current_total = np.round(np.sum(portfolio_price_list), 2)
        portfolio_percent_return = np.round((portfolio_current_total-portfolio_original_total)/portfolio_original_total*100,2)

        if portfolio_percent_return < 0:
            plt.annotate(f'Total value of portfolio \n${portfolio_current_total:,}\n',(0,-0.2), color='white', fontsize=18,
                     horizontalalignment='center')
            plt.annotate(f'\n\n({portfolio_percent_return}%)',(0,-0.2), color='red', fontsize=18, horizontalalignment='center')
        else:
            plt.annotate(f'Total value of portfolio \n${portfolio_current_total:,}\n',(0,-0.2), color='white', fontsize=18,
                              horizontalalignment='center')
            plt.annotate(f'\n\n(+{portfolio_percent_return}%)',(0,-0.2), color='green', fontsize=18, horizontalalignment='center')


        plt.suptitle('Your stock portfolio', fontsize=18, color='white', y=0.96)
        plt.annotate('Money made so far:', color='white', xy=(-1.25,1.25), fontsize=14, ha='left')
        plt.annotate(f'${money_made:,}', color='green', xy =(-0.38,1.25), fontsize=14, ha='left')

        ax.set_facecolor('black')
        fig.set_facecolor('black')
        plt.tight_layout()
        plt.close()
        return fig


### NEED TO MAKE DEFAULT WITH THE PORTFOLIO
### Need to make the period be the shortest time while still encapsulating the time stock was bought
def plot_portfolio_stock(stock=''):
    import pandas as pd
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.dates as mdates
    import PySimpleGUI as sg
    import yfinance as yfi
    import numpy as np
    import pickle
    from PIL import Image
    import numpy.ma as ma
    from matplotlib.lines import Line2D

    stock_sym = stock.split('~')[0]
    stock_info_dict = pickle.load(open('stock_info_dictionary.p','rb'))
    interval_list = ['1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo']
    portfolio_dict = pickle.load(open('stock_portfolio_dict_TEST.p', 'rb'))

    ### Download data of stock with each interval so can get most detailed data for whatever time frame
    dow_df = pd.DataFrame()
    try:
        i=0
        while len(dow_df) == 0:
            dow_df = yfi.ticker.Ticker(stock_sym).history(start=portfolio_dict[stock]['date'],
                                                           interval = interval_list[i])
            i += 1
        1/len(dow_df)
    except ZeroDivisionError:
        sg.popup(stock_error_text, no_titlebar=True,grab_anywhere=True, font=14, background_color='red', keep_on_top=True)
        return

    ### Get the change in the stock
    start = portfolio_dict[stock]['price_bought_at']
    end = dow_df['Close'][-1]
    difference = end-start
    per_difference = (end-start)/start*100
    if per_difference < 0:
        diff_neg = True
    else:
        diff_neg = False

    ### Change datetime object so plots x-tick labels correctly by removing time zone and
    ### then making string object so doesn't plot gap days
    dow_df = dow_df.reset_index()
    i=0
    for a in dow_df['Datetime']:
        dow_df['Datetime'].iloc[i] = a.replace(tzinfo=None)
        i+=1
    dow_df = dow_df.set_index('Datetime')

    date_str_list = []
    i=0

    for a in dow_df.index:
        date_str_list.append(str(dow_df.index[i]).split(' ')[0] + '\n' + str(dow_df.index[i]).split(' ')[1])
        i+=1

    dow_df['date_str'] = date_str_list
    dow_df = dow_df.reset_index()
    dow_df = dow_df.set_index('date_str')


    ### Make a preplot to get the y-limit values in order for the shadow under the plot to work
    fig = plt.figure(figsize=(9,6))
    ax = fig.add_subplot()
    ax.plot(dow_df.index, dow_df['Open'],c='#08F7FE')
    ylim = ax.get_ylim()
    if float(start) < ylim[0]:
        ylim = (start-1, ylim[1])
    if float(start) > ylim[1]:
        ylim = (ylim[0], start+1)

    plt.close()


    ### Making the plot
    ### afterglow code source - https://towardsdatascience.com/cyberpunk-style-with-matplotlib-f47404c9d4c5
    fig = plt.figure(figsize=(10,7))
    ax = fig.add_subplot()
    ax.plot(dow_df.index, dow_df['Open'],c='red')
    mask_show_above = ma.masked_less(value = start, x=dow_df['Open'].values)
    mask_show_below = ma.masked_greater(value = start, x=dow_df['Open'].values)
    ax.plot(dow_df.index, mask_show_above, c='green')
    plt.ylim(ylim)


    ax.xaxis.set_major_locator(mdates.AutoDateLocator())

    ### redrawing lines multiple times to create glow effect
    n_lines = 10
    diff_linewidth = 1.55
    alpha_value = 0.03

    for n in range(1, n_lines+1):
        ax.plot(dow_df.index, mask_show_above,
               linewidth = 2+(diff_linewidth*n),
               alpha = alpha_value,
               c='green')

    for n in range(1, n_lines+1):
        ax.plot(dow_df.index, mask_show_below,
               linewidth = 2+(diff_linewidth*n),
               alpha = alpha_value,
               c='red')

    ### Color the areas below the lines:
    ax.fill_between(x=dow_df.index,
                        y1=mask_show_above,
                        y2=[0] * len(dow_df),
                        color='green',
                        alpha=0.2)

    ax.fill_between(x=dow_df.index,
                        y1=mask_show_below,
                        y2=[0] * len(dow_df),
                        color='red',
                        alpha=0.2)

    plt.axhline(y=start, color='gray', linestyle='solid',
               linewidth = 3)

    plt.ylabel('Stock Value', fontsize=16, color='white')
    plt.xlabel('Date',fontsize=16, color='white')
    plt.xticks(rotation=45, fontsize=14, color='white')
    plt.yticks(fontsize=14, color='white')

    mid = (fig.subplotpars.right + fig.subplotpars.left)/2
    random_stock_short_name = stock_info_dict[stock_sym]['shortName']
    suptitle = random_stock_short_name + ' (' + stock_sym + ')'
    plt.suptitle(suptitle ,fontsize=24, color='white', x=mid+0.02)



    if diff_neg:
        title = f'{np.round(difference,decimals = 2)} ({np.round(per_difference, decimals=2)}%) from buy price'
        plt.title(title, fontsize=20, color='red')
    else:
        title = f'+{np.round(difference,decimals = 2)} (+{np.round(per_difference, decimals=2)}%) from buy price'
        plt.title(title, fontsize=20, color='green')


    custom_lines = [Line2D([0], [0], color='gray', lw=4)]
    plt.legend(custom_lines, ['Stock buy price'], fontsize=14, facecolor='black', labelcolor ='white',
              frameon=True, loc='upper left', edgecolor='black')

    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    plt.grid(axis='both', linestyle='--', linewidth=1,color='gray', alpha=0.5)

    ax.set_facecolor('black')
    fig.set_facecolor('black')
    plt.tight_layout()
    plt.close()
    return fig


def blank_stock_portfolio_performance_plot():
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(11,8))
    ax = fig.add_subplot()
    ax.plot([1,2,3,4,5,6,7,8,9], [1,2,3,4,5,6,7,8,9])
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    #plt.grid(axis='both', linestyle='--', linewidth=1,color='gray', alpha=0.5)

    plt.ylabel('Joy!', fontsize = 20, color='white')
    plt.xlabel('Time spent exploring investing', fontsize = 20, color='white')
    plt.suptitle('Experience when using this app', fontsize = 24, color='white', x=0.5)
    plt.title('This is 100% accurate', fontsize = 20, color='white', x=0.475)

    ax.set_facecolor('black')
    fig.set_facecolor('black')
    plt.tight_layout()
    plt.close()
    return fig

def update_portfolio_text():
    import pickle
    import yfinance as yfi
    import numpy as np

    with open('stock_portfolio_dict_TEST.p', 'rb') as handle:
        portfolio_dict = pickle.load(handle)
    text_list = ''
    if len(portfolio_dict) > 0:
        for stock in portfolio_dict:
            stock_sym = stock.split('~')[0]
            current_price = float(yfi.Ticker(stock_sym).history().iloc[-1]['Close'])
            original_total = portfolio_dict[stock]['price_bought_at']*float(portfolio_dict[stock]['num_stocks'])
            total_val = current_price*portfolio_dict[stock]['num_stocks']
            percent_return = (total_val-original_total)/original_total*100
            num_stocks = portfolio_dict[stock]['num_stocks']
            purchase_price = portfolio_dict[stock]['price_bought_at']
            text = f'{stock} : Total value = ${np.round(total_val, 2)} | Curret % return = {np.round(percent_return,2)} |\n# of shares owned = {num_stocks} | Purchase price = ${purchase_price} per stock'
            text_list = text_list + text + '\n' + '-'*85 + '\n'
    else:
        text_list = "Empty portfolio. Go get investing! :)"
    return text_list
