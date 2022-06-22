#!/usr/bin/env python

from glob import glob
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import yfinanceScraper 
import ticker_manager
import model
import matplotlib.pyplot as plt
import pandas as pd
import vix_trigger_only

st.set_page_config(layout="wide")
st.image('images/header.png')
st.markdown(""" # Welcome to the VIX buy or sell trigger

The purpose of this program is to provide you, the stock trader, with a 'report' on the VIX index for 
possible buy & sell triggers based on the Larry Connors 'CVR' reversal indicators.

This particular implementation examines the recent 15-period VIX daily high & low values 
and applies the following rules:

- When the VIX index makes a NEW 15 day low AND closes ABOVE its open, it signals a sell
- When the VIX index makes a NEW 15 high low AND closes BELOW its open, it signals a buy



It makes use of the yahoo stock quotes python library to scrape the necessary data from Yahoo Finance. 
The program will also provide you with a chart of the VIX index from the time period as an interactive candleplot.
Volume is included in the chart, but as a random number just to show more info on the chart.
"""
)
# Number of days of historical data to fetch (not counting today)
days_back = st.sidebar.slider('Number of days in graph and data', 15, 365, 60)
stepsize = st.sidebar.slider('Size of time window used for 1 lag prediction', 15,100, 15)

vix_or_no = st.sidebar.checkbox("Do you want to see the vix_trigger prediction")
if vix_or_no:
    #vix_trigger_only.main_vix(days_back)

    scraper = yfinanceScraper.Scraper(n_days=days_back)
    print(scraper.historic_data)
    # Get the recommendation
    st.json(scraper.recommendation(api=True))

data_dict = {}
st.sidebar.write("What Tickers do you want to use?")

#data_dict = gather_tickers()
def get_ticker_name(ticker):
    return ticker.name
data_dict = {ticker: yfinanceScraper.Scraper(ticker=ticker.value, n_days=days_back) for ticker in ticker_manager.Ticker}

ticker_form = st.sidebar.form("ticker_form")
data_list = ticker_form.multiselect(
     "Which ticker would you use as data for the prediction or candleplots",
     data_dict.keys(), format_func=get_ticker_name,default=list(data_dict.keys())[0])
 

st.write("""The program will Furthermore give you an idea of the trend with a prediction of a singular ticker out
            Out of the current selection, and you can also choose what kind of tickers you want to use to help
            with the prediciton""")



options = ticker_form.multiselect(
     "Which ticker would you like to display and predict? (Can only predict one ticker at a time)",
     data_dict.keys(), format_func=get_ticker_name, default=list(data_dict.keys())[0])


submitted = ticker_form.form_submit_button("Submit")
#st.sidebar.write('You selected:', options)
@st.cache(allow_output_mutation=True)
def create_candleplot(scraper):
    df = scraper.historic_data
    
    fig = make_subplots(rows=2, cols=1, row_heights=[1, 0.2], vertical_spacing=0)

    fig.add_trace(go.Candlestick(x=df['datetime'],
                                         open=df['open'],
                                         high=df['high'],
                                         low=df['low'],
                                         close=df['close'],
                                increasing_line_color='#0384fc', decreasing_line_color='#e8482c', name=scraper.name), row=1, col=1)

    fig.add_trace(go.Scatter(x=df['datetime'], y=np.random.randint(20, 40, len(df)), marker_color='#fae823', name='VO', hovertemplate=[]), row=2, col=1)

    fig.update_layout({'plot_bgcolor': "#21201f", 'paper_bgcolor': "#21201f", 'legend_orientation': "h"},
                    legend=dict(y=1, x=0),
                    font=dict(color='#dedddc'), dragmode='pan', hovermode='x unified',
                    margin=dict(b=21, t=1, l=1, r=40))

    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=True,
                    showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid')

    fig.update_xaxes(showgrid=False, zeroline=False, rangeslider_visible=False, showticklabels=True,
                    showspikes=True, spikemode='across', spikesnap='cursor', showline=False, spikedash='solid')

    fig.update_layout(hoverdistance=1)

    fig.update_traces(xaxis='x')  
                                  
    return fig

# create a streamlit box for candleplot
def async_streamlit_candleplot(ticker, data):
    """
    Creates a streamlit box for the candleplot
    Parameters:
    data (list): All price data for the VIX index 15 days back
    """
    st.subheader(f"{ticker.name} Candlestick Chart")
    fig = create_candleplot(data)
    st.plotly_chart(fig)




viz_candleplot, use_machine_learning_to = st.columns([1,1])



def create_all_plots():
    """
    Creates all the plots for the VIX index and others
    Returns a streamlit text of the plots
    """
    # Create a candlestick plot of the VIX index
    for ticker in options:
        
        async_streamlit_candleplot(ticker, data_dict[ticker])

viz_candles = viz_candleplot.button("Generate candleplots")
if viz_candles: create_all_plots()

use_machine_learning_to_pred = use_machine_learning_to.button("Train model and get prediction graph")
if use_machine_learning_to_pred: 
    if len(options) < 2:

        predictorname = options[0].name
        df = None
        for ticker in data_list:
            data =data_dict[ticker].historic_data
            data.columns = [ticker.name + "."+ x for x in data.columns]
            if df is None:
                df = data
                #print(df)
            else:
                df = pd.concat((df, data), axis=1)


        df = df.fillna(0)
        df = df.set_index(predictorname+"."+"datetime")
        for col in df.columns:
            if "datetime" in col:
                df.drop(col, axis=1, inplace=True)

        predictor_col_ind = 0
        for col in df.columns:
            if col != predictorname+"."+"close":
                predictor_col_ind += 1
            else:
                break


        df = df[df.index != 0]

        train_data, test_data, total_data = df[0:int(len(df)*0.7)], df[int(len(df)*0.7):], df

        X_train, y_train, sc, sc_target = model.preproccess(train_data, predictor_col_ind, steps=stepsize)
        inputs = total_data.iloc[len(total_data) - len(test_data) - stepsize:]
        print(inputs.shape)
        with st.spinner('Training model'):
            lstm = model.model_build_and_fit(X_train, y_train)

        


        X_test = model.preproccess_inference(inputs, steps=stepsize, sc=sc)

        predicted_stock_price = lstm.predict(X_test)
        mse = lstm.evaluate(X_train, y_train)
        st.success(f"LSTM trained and predicted {options} with MSE: {mse}")
        predicted_stock_price = sc_target.inverse_transform(predicted_stock_price)

        # Visualising the resasdultsa
        fig = plt.figure()
        plt.plot(df.iloc[int(len(df)*0.7):].index,test_data.iloc[:, predictor_col_ind].values, color = 'red', label = 'Real')
        plt.plot(df.iloc[int(len(df)*0.7):].index,predicted_stock_price, color = 'blue', label = 'Predicted')
        
        plt.title(f'{predictorname} Stock Price Prediction')
        plt.xlabel('Time')
        plt.ylabel(f'{predictorname} Stock Price')
        plt.xlim(df.iloc[int(len(df)*0.7):].index.min(), df.iloc[int(len(df)*0.7):].index.max())
        plt.autoscale(enable=True)
        plt.xticks(rotation=45, fontsize=10)
        #plt.xticks(np.arange(0,int(len(df)*0.3),6))
        plt.legend()
        # display matplotlib plot with streamlit
        st.pyplot(fig)
    else:
        st.error("Can only Predict one ticker at a time (will have to retrain)")
