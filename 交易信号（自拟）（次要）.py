# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 19:25:18 2021

@author: Phoenix
"""
import pandas as pd
import datetime as dt
import numpy as np
R_b = 0.002
R_a = 0.001
c = 0
asset = 5000000
big_float = 6
a=20
b=50
trade_multi = 5
dfh = pd.read_csv("C:\\Users\\Phoenix\\Desktop\\Data (2)\\Data\\high_adj_fake.csv")
dfl = pd.read_csv("C:\\Users\\Phoenix\\Desktop\\Data (2)\\Data\\low_adj_fake.csv")
dfcp = pd.read_csv("C:\\Users\\Phoenix\\Desktop\\Data (2)\\Data\\pre_cp_adj_fake.csv")
dfccp = pd.read_csv("C:\\Users\\Phoenix\\Desktop\\Data (2)\\Data\\cp_adj_fake.csv")

'''初始化循环内所要用到的存储变量，为了方便获得相同的index，直接使用循环第一步的代码获取index'''
df_e = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
asset_line = [asset for index in range(1944)]
df_e['asset'] = asset_line
zeros = [0 for index in range(1944)]
df_e['buying_cost'] = zeros
df_e['total_marketprice'] = zeros
dfh['hour'] = pd.to_datetime(dfh['hour'])
dfh['date'] = dfh['hour'].dt.date
dfh1 = dfh[['hour','A','date']]
hd = dfh1.sort_values(['date','A'],ascending=False)
hd = hd.drop_duplicates(subset='date')
hd = hd.sort_values('date',ascending=True)
dfpp = hd.set_index(hd['date'])
df_e = df_e.set_index(hd['date'])

'''
一、先对数据进行处理，将小时数据转换为日数据
'''
'''
1、处理high_price数据，先将导入的时间数据转换为datetime格式，然后提取年月日形成一列新的
datetime格式数据date，以这一新的数据作为分组依据，用sort_values进行组内大小由高到低的排序，
利用drop_duplicates删除组内非最大值，最后为保证时间数据由小到大递增，再利用sort_values
矫正排序，最后使用date作为新的index.
'''
idx = ['A','AG','AL','AP','AU','BU','C','CF','CU','EG','FG','HC','I','J','JD','JM','M','MA','NI','P','PP','RB','RM','RU','SF','SM','SR','TA','Y','ZC','ZN']
idx1 = ['ZN']
for i in idx:
    current_running = i
    dfh['hour'] = pd.to_datetime(dfh['hour'])
    dfh['date'] = dfh['hour'].dt.date
    dfh1 = dfh[['hour',i,'date']]
    hd = dfh1.sort_values(['date',i],ascending=False)
    hd = hd.drop_duplicates(subset='date')
    hd = hd.sort_values('date',ascending=True)
    df = hd.set_index(hd['date'])
    '''
    2、处理low_price数据，与1类似，唯一不同便是第一次sorting的时候ascending直接取True，
    不用进行第二次sorting.
    '''
    dfl['hour'] = pd.to_datetime(dfl['hour'])
    dfl['date'] = dfl['hour'].dt.date
    dfl1 = dfl[['hour',i,'date']]
    ld = dfl1.sort_values(['date',i],ascending=True)
    ld = ld.drop_duplicates(subset='date')
    df2p = ld.set_index(ld['date'])
    df['lprice'] = df2p[i]
    '''
    3、处理pre_price数据
    '''
    dfcp['hour'] = pd.to_datetime(dfcp['hour'])
    dfcp['date'] = dfcp['hour'].dt.date
    cpd = dfcp.drop_duplicates(subset='date')
    df2cp=cpd.set_index(cpd['date'])
    df['pcprice'] = df2cp[i]
    '''
    4、处理cp_price数据，取当天最迟的收盘价作为当天收盘价
    '''
    dfccp['hour'] = pd.to_datetime(dfccp['hour'])
    dfccp['date'] = dfccp['hour'].dt.date
    ccpd = dfccp.sort_values(['date','hour'],ascending=False)
    ccpd = dfccp.drop_duplicates(subset='date')
    ccpd = ccpd.sort_values('date',ascending=True)
    df2ccp=ccpd.set_index(ccpd['date'])
    df['cprice'] = df2ccp[i]
    df.rename(columns = {i:'hprice'},inplace=True)
    
    
    '''
    二、计算海龟交易方法的重要变量
    '''
    df['tr'] = ''
    num = len(df['hprice'])
    for i in range(0,num):
        df['tr'][i] = max(df['hprice'][i]-df['lprice'][i],abs(df['hprice'][i]-df['pcprice'][i]),abs(df['lprice'][i]-df['pcprice'][i]))
    df['atr_buy'] = df['tr'].rolling(b).mean()
    df['atr_sell'] = df['tr'].rolling(a).mean()
    df['position_buy'] = R_b*asset/(df['atr_buy']*trade_multi)
    df.dropna(inplace = True)
    df['position_buy'] = df['position_buy'].astype(int)
    df['position_add'] = R_a*asset/(df['atr_buy']*trade_multi)
    df['position_add'] = df['position_add'].astype(int)
    '''
    *保存一些df的series备用
    '''
    df_position_buy = df['position_buy']
    df_position_add = df['position_add']
    df_hprice = df['hprice']
    df_lprice = df['lprice']
    df_pcprice = df['pcprice']
    df_cprice = df['cprice']
    dummy = [0 for index in range(len(df))]
    df['dummy1'] = dummy
    df['dummy2'] = dummy
    df['dummy3'] = dummy
    df_sell_time = df['dummy1']
    df_add_time = df['dummy2']
    df_buy_time = df['dummy3']
    df_date = df['date']
    edit = False
    sig_open = df['hprice'].first_valid_index()
    df_buy_time.loc[sig_open] = 1
    '''
    三、模拟交易：
    由于海龟交易并未特意强调入场时机，在此作出假设：
    第一期直接入场，默认做多，之后所有入场信号均以前一期的入场价格作为参照
    默认入场之后最多加仓1次
    '''
    while True:
        
        '''
        1、计算突破信号（开仓信号、加仓信号、平仓信号）
        '''
        df.loc[df['hprice']-2*df['atr_buy']>df['hprice'][0],'pos_buy'] = 1
        df.loc[df['hprice']-0.5*df['atr_buy']>df['hprice'][0],'pos_add'] = 1
        df.loc[df['lprice']+2*df['atr_sell']<df['hprice'][0],'pos_sell'] = 1
        '''
        2、计算初次加仓或平仓信号发出的时间，若平仓信号早于加仓信号发出则不记录加仓，
        只记录平仓，反之则两者都记录，同时还必须记录开仓时间
        '''
        sig_buy = df['pos_buy'].first_valid_index()
        if sig_buy == None:
            sig_buy = df['date'][-1]
        sig_add = df['pos_add'].first_valid_index()
        '''
        (1)、计算大趋势条件，当前一天的最高价减去开仓价大于bigfloat*atr时触发该条件，此后
        若价格自该最高价向下波动一个atr时就触发平仓
        '''
        df.loc[df['hprice'].shift()-big_float*df['atr_buy']>df['hprice'][sig_buy],'bigfloat'] = 1
        sig_bigfl = df['bigfloat'].first_valid_index()
        df['bigfloat'] = df['bigfloat'].fillna(method = 'ffill')
        edit = True
        if sig_bigfl == None:
            df['pos_sell'] = df['pos_sell']
        else:
            '''
            这里的一个基本想法是，大趋势条件与减仓条件相乘，第一个非0数的index则代表了
            大趋势平仓的时机，将它与原本平仓条件相加，再取第一个非零数就是加入大趋势条件的
            平仓时机。
            '''
            df.loc[df['lprice']+1*df['atr_sell']<df['hprice'].shift()[sig_bigfl],'pos_sell_float'] = 1
            df['pos_sell_float'] = df['pos_sell_float']*df['bigfloat']
            df['pos_sell_float'] = df['pos_sell_float'].fillna(0,inplace = True)
            df['pos_sell'] = df['pos_sell'].fillna(0,inplace = True)
            df['pos_sell'] = df['pos_sell_float']+df['pos_sell']
            c = df['pos_sell']
            c[c==0] = np.nan
        sig_sell = df['pos_sell'].first_valid_index()
        '''
        (2)、若没有加仓信号，即加仓信号为nan，则默认加仓信号发出于最后一期，此时必然不会记录
        加仓，若没有平仓信号，即平仓信号为nan,意味着此次持仓期没有平仓，此时默认在最后一期平仓
        ，这不会影响我们对总获利的计算。
        '''
        if sig_add == None:
            sig_add = df['date'][-1]
        df['pos_buy'].fillna(method = 'ffill',inplace = True)
        df['pos_buy'][0] = np.nan
        df_sell_time.loc[sig_sell] = 1
        df_buy_time.loc[sig_buy] = 1
        if sig_sell == None:
            sig_sell = df['date'][-1]
        if sig_sell<sig_add:
            print("直接平仓,不加仓。")
            df.dropna(axis=0,subset = ["pos_buy"],inplace = True) 
        if sig_sell>sig_add:
            print("先加仓，后平仓。")
            df_add_time.loc[sig_add] = 1
        '''
        3、删去之前已经分析过的时期，比较开仓信号与平仓信号哪个在先，如果开仓信号在先
        说明正常开仓，删去本期开仓信号后drop至下一期开仓，记录开加平仓信号，反之则说明
        没有正常开仓，因此不删本期开仓，drop本期开仓之前的期数（包含不需要的平仓信号）
        本期不记录交易信号，循环上述信号记录过程，直至不再开仓，或者不再平仓。
        '''
        if sig_sell>=sig_buy:
            df.dropna(axis=0,subset = ["pos_sell"],inplace = True)
        if sig_sell<sig_buy:
            df.dropna(axis=0,subset = ["pos_buy"],inplace = True)
        sig_buy_h = df['pos_buy'].first_valid_index()
        sig_buy = df['pos_buy'].first_valid_index()
        if sig_buy != None:
           df_buy_time.loc[sig_buy] = 1
        if len(df['hprice'])<=1 or df['pos_sell'].isnull().any() == False:
            break
        df.drop(columns = ['pos_buy','pos_add','pos_sell'], inplace=True)
    '''
    四、效果回测
    '''
    df['buy'] = df_buy_time
    df['add'] = df_add_time
    df['sell'] = df_sell_time
    df['pp'] = df_buy_time+df_add_time+df_sell_time
    c = c + df['pp'].sum()
    df['position_buy'] = df_position_buy
    df['position_add'] = df_position_add
    df['hprice'] = df_hprice
    df['lprice'] = df_lprice
    df['pcprice'] = df_pcprice
    df['date'] = df_date
    df['cprice'] = df_cprice
    df['buy'] = df['buy']*df['position_buy']
    df['buyadd'] = df['buy'] + df['add']
    c = df['buy']
    c[c==0]=np.nan
    '''
    1、得到实时仓位的方法：用开仓信号进行切割，将全期分为若干持仓期，每一持仓期都存在一次开仓
    和一次平仓，可能存在加仓，存在加仓的话则只在该持仓期内进行填充，这通过将加仓与开仓加总后分别
    填充，然后drop开仓信号得到加仓信号
    '''
    df['buyfill'] = df['buy'].fillna(method = 'ffill')
    df['sellbuy'] = -df['sell']*df['buyfill']
    c = df['buyadd']
    c[c==0] = np.nan
    df['buyadd'] = df['buyadd'].fillna(method = 'ffill')
    c = df['buyadd']
    c[c!=1] = 0
    df['add'] = df['add']*df['position_add']
    c = df['add']
    c[c==0]=np.nan
    df['addfill'] = df['add'].fillna(method = 'ffill')
    df['addfill'] = df['addfill']*df['buyadd']
    df['addfill'] = df['addfill'].fillna(0)
    df['selladd'] = -df['sell']*df['addfill']
    df['add'] = df['add'].fillna(0)
    df['buy'] = df['buy'].fillna(0)
    '''
    2、计算总价值，将总价值分为市场价值和现金价值分别计算，计算市场价值时，先计算
    标的在每一时间总的仓位数量，再乘以当时的市场价格，再将每一只标的累加；计算现金价值时，
    主要是计算在各个时间点的对各只标的的支出，再做一个累加，得到总的支出流水
    '''
    df['trade'] = df['buy']+df['sellbuy']+df['selladd']+df['add']
    df['totalpos'] = df['trade'].cumsum()
    df_e['marketprice'] = df['totalpos']*df['cprice']
    df_e['marketprice'].fillna(0,inplace = True)
    df['pcprice'].fillna(0)
    zeros = [0 for index in range(1944)]
    df_e['zeros'] = zeros
    df_e['D'] = df_e['zeros'] - df['trade']*df['cprice']
    df_e['D'].fillna(0,inplace = True)
    df_e['buying_cost'] = df_e['D']+df_e['buying_cost']
    df_e['total_marketprice'] = df_e['marketprice'] + df_e['total_marketprice']

df['total_buyingcost'] = df_e['buying_cost'].cumsum()
df['cash_account'] = df['total_buyingcost']+asset
df['total_value'] = df['cash_account'] + df_e['total_marketprice']
df['total_value'].plot()
r = df['total_value'].pct_change()
r_mean = r.mean()
r_std = r.std()
ss = r_mean/r_std
if edit == True:
    print('在平仓信号经过大趋势修正之后：\n')
else:
    print('在平仓信号未经大趋势修正的情况下：\n')
print('参数a={},b={}的日线收益率均值与标准差的比值为{}'.format(a,b,ss))

