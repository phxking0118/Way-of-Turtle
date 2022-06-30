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
        df['tr'][i] = max(df['hprice'][i]-df['lprice'][i],
                          abs(df['hprice'][i]-df['pcprice'][i]),
                          abs(df['lprice'][i]-df['pcprice'][i]))
    df['atr_buy'] = df['tr'].rolling(b).mean()
    df['atr_sell'] = df['tr'].rolling(a).mean()
    df['position_buy'] = R_b*asset/(df['atr_buy']*trade_multi)
    df['high_long'] = df['hprice'].rolling(b).max()
    df['low_short'] = df['lprice'].rolling(a).min()
    df['high_short'] = df['hprice'].rolling(a).max()
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
    '''
    三、模拟交易：
    默认做多，默认入场之后最多加仓1次
    '''
    while True:
        
        '''
        1、计算突破信号（开仓信号、加仓信号、平仓信号）
        '''
        df.loc[df['hprice']-2*df['atr_buy']>df['high_long'].shift(),'drop_indc'] = 1
        df.loc[df['lprice']+2*df['atr_sell']<df['low_short'].shift(),'pos_sell'] = 1
        '''
        删去开仓前的每一期，因为之前的各期对计算没有帮助，并且如此操作
        可以确保每一轮以开仓为开始
        '''
        df['pos_buy'] = df['drop_indc']
        df['drop_indc'].fillna(method = 'ffill', inplace = True)
        df.dropna(axis=0,subset = ["drop_indc"],inplace = True)
        if len(df['hprice']) <=0:
            break
        '''
        计算第一次开仓的时机,若全程不开仓，则记为最后一期开仓，这样
        方便后面的比较，并且不影响最后总资产的计算结果
        '''
        sig_buy = df['pos_buy'].first_valid_index()
        if sig_buy == None:
            sig_buy = df['date'][-1]
            
        '''加仓信号'''
        df.loc[df['hprice']-0.5*df['atr_buy']>df['hprice'][sig_buy],'pos_add'] = 1
        sig_add = df['pos_add'].first_valid_index()
        if sig_add == None:
            sig_add = df['date'][-1]
        
        # '''*修正平仓条件开始-------------------------------------------
        # (若检验big float条件的意义可以注释此部分，不影响总体运行）'''
        # '''
        # (1)、计算大趋势条件，当前一天的最高价减去开仓价大于bigfloat*atr时触发该条件，此后
        # 若价格自该最高价向下波动一个atr时就触发平仓
        # '''
        # edit = True
        # df.loc[df['hprice'].shift()-big_float*df['atr_buy']>df['hprice'][sig_buy],'bigfloat'] = 1
        # sig_bigfl = df['bigfloat'].first_valid_index()
        # df['bigfloat'] = df['bigfloat'].fillna(method = 'ffill')
        # #修正平仓条件
        # if sig_bigfl == None:
        #     df['pos_sell'] = df['pos_sell']
        # else:
        #     '''
        #     这里的一个基本想法是，大趋势条件与减仓条件相乘，第一个非0数的index则代表了
        #     大趋势平仓的时机，将它与原本平仓条件相加，再取第一个非零数就是加入大趋势条件的
        #     平仓时机。
        #     '''
        #     df.loc[df['lprice']+1*df['atr_sell']<df['high_short'].shift(),'pos_sell_float'] = 1
        #     df['pos_sell_float'] = df['pos_sell_float']*df['bigfloat']
        #     df['pos_sell_float'] = df['pos_sell_float'].fillna(0,inplace = True)
        #     df['pos_sell'] = df['pos_sell'].fillna(0,inplace = True)
        #     df['pos_sell'] = df['pos_sell_float']+df['pos_sell']
        #     c = df['pos_sell']
        #     c[c==0] = np.nan
        # '''*修正平仓条件结束-------------------------'''
            
        '''平仓信号'''
        sig_sell = df['pos_sell'].first_valid_index()
        if sig_sell == None:
            sig_sell = df['date'][-1]
            
        '''
        2、记录信号：若平仓信号早于加仓信号发出则不记录加仓，
        只记录平仓，反之则两者都记录，同时还必须记录开仓时间
        '''
        if sig_sell<=sig_add:
            print("直接平仓,不加仓。")
            df_sell_time.loc[sig_sell] = 1
        if sig_sell>sig_add:
            print("先加仓，后平仓。")
            df_sell_time.loc[sig_sell] = 1
            df_add_time.loc[sig_add] = 1
        df_buy_time.loc[sig_buy] = 1
            
        '''
        3、删去之前已经分析过的时期，重新循环，直至时期已经全部被分析或者不再平仓
        （剩余的pos_sell全不为nan)，停止循环，获得该标的全期的开加平仓时机
        '''
        df['pos_sell'].fillna(method = 'ffill', inplace = True)
        df.dropna(axis=0,subset = ["pos_sell"],inplace = True)
        if len(df['hprice'])<=1 or df['pos_sell'].isnull().any() == False:
            '''
            因为若df未被完全drop，后期赋值会在残存的df上赋值，所以若df未被完全drop,
            还应加入条件，保证df长度为0
            '''
            c = df['hprice']
            c[c!=np.nan] = np.nan
            df.dropna(axis=0,subset = ["hprice"],inplace = True)
            break
        df.drop(columns = ['pos_buy','pos_add','pos_sell'], inplace=True)
    '''
    四、效果回测
    '''
    df['buy'] = df_buy_time
    df['add'] = df_add_time
    df['sell'] = df_sell_time
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
std = df['total_value'].std()
R = df['total_value'][-1]-df['total_value'][0]
R_rate = R/df['total_value'][0]
s = R/std
r = df['total_value'].pct_change()
r_mean = r.mean()
r_std = r.std()
ss = r_mean/r_std
if edit == True:
    print('在平仓信号经过大趋势修正之后：\n')
else:
    print('在平仓信号未经大趋势修正的情况下：\n')
print('参数a={},b={}的日线收益率均值与标准差的比值为{}'.format(a,b,ss))
