import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore")
plt.style.use('fivethirtyeight')
import pandas as pd

import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

import ticker_manager


def preproccess(training_set, predictor_col_ind, steps=15, sc=None):
    # Feature 
    if sc == None:
        sc = MinMaxScaler(feature_range = (0, 1))
        sc_target = MinMaxScaler(feature_range = (0, 1))
        #print(training_set.iloc[:,predictor_col_ind])
        sc_target.fit(training_set.values[:,predictor_col_ind].reshape(-1, 1))
        training_set_scaled = sc.fit_transform(training_set)
    else:
        training_set_scaled = sc.transform(training_set)
    # Creating a data structure with 60 time-steps and 1 output
    X_train = []
    y_train = []
    for i in range(steps, len(training_set)):
        X_train.append(training_set_scaled[i-steps:i,:])
        
        y_train.append(training_set_scaled[i,predictor_col_ind])
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2]))

    return X_train, y_train, sc, sc_target

def preproccess_inference(test_data, steps=15, sc=None):
    # Feature 
    if sc == None:
        sc = MinMaxScaler(feature_range = (0, 1))
        training_set_scaled = sc.fit_transform(test_data)
    else:
        training_set_scaled = sc.fit_transform(test_data)
    # Creating a data structure with 60 time-steps and 1 output
    X_train = []
    for i in range(steps, len(test_data)):
        X_train.append(training_set_scaled[i-steps:i,:])
    X_train = np.array(X_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], X_train.shape[2]))

    return X_train,

#@st.experimental_memo
def model_build_and_fit(X_train, y_train):
    model = Sequential()
    #Adding the first LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    # Adding a second LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 50, return_sequences = True))
    model.add(Dropout(0.2))
    # Adding a third LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 50, return_sequences = True))
    model.add(Dropout(0.2))
    # Adding a fourth LSTM layer and some Dropout regularisation
    model.add(LSTM(units = 50))
    model.add(Dropout(0.2))
    # Adding the output layer
    model.add(Dense(units = 1))

    # Compiling the RNN
    model.compile(optimizer = 'adam', loss = 'mean_squared_error')

    # Fitting the RNN to the Training set
    model.fit(X_train, y_train, epochs = 100, batch_size = 32)
    return model


    

if __name__ == '__main__':
    import yfinanceScraper
    stepsize = 30
    number_of_days = 800
    
    """SCRAPER_TSLA = yfinanceScraper.Scraper(ticker="TSLA", n_days=number_of_days)
    SCRAPER_VIX = yfinanceScraper.Scraper(ticker="^VIX", n_days=number_of_days)
    SCRAPER_GME = yfinanceScraper.Scraper(ticker="GME", n_days=number_of_days)
    SCRAPER_SP500 = yfinanceScraper.Scraper(ticker="^GSPC", n_days=number_of_days)
    SCRAPER_AAPL = yfinanceScraper.Scraper(ticker="AAPL", n_days=number_of_days)"""

    df = None
    for ticker in ticker_manager.Ticker:
        data = yfinanceScraper.Scraper(ticker=ticker.value, n_days=number_of_days).historic_data
        data.columns = [ticker.name + "."+ x for x in data.columns]
        if df is None:
            df = data
            #print(df)
        else:
            df = pd.concat((df, data), axis=1)
        #print(df)

    
    print(df)
    
    
    #
    #df = SCRAPER_VIX.historic_data
    #dfd
    #print(df)

    
    #plt.figure()
    #lag_plot(SCRAPER_TSLA.historic_data['Open'], lag=3)
    #plt.title('TESLA Stock - Autocorrelation plot with lag = 3')
    #plt.show()
    
    
    """train_data, test_data = df[0:int(len(df)*0.7)], df[int(len(df)*0.7):]
    print(test_data)
    predictions = SARIMA_UNIVARIATE(train_data, train_data)
    print(len(predictions), len(test_data))
    plot_data(predictions, test_data, 'VIX')"""


    """
        def join_data(list_of_df):
        df = pd.concat(list_of_df, 
                    axis=1)                   
        return df


    def SARIMA_UNIVARIATE(train_data, test_df):
        # Fit an ARIMA model to the data on closing prices
        
        training_data = train_data['close'].values
        test_data = test_df['close'].values
        dates = test_df["datetime"]
        #print(dates)
        history = [x for x in training_data]
        model_predictions = []
        N_test_observations = len(test_data)
        for time_point in range(N_test_observations):
            model = ARIMA(history, order=(4,1,0))
            model_fit = model.fit()
            output = model_fit.forecast()
            yhat = output[0]
            model_predictions.append(yhat)
            true_test_value = test_data[time_point]
            history.append(true_test_value)
        MSE_error = mean_squared_error(test_data, model_predictions)
        print('Testing Mean Squared Error is {}'.format(MSE_error))

        #model_predictions = np.asarray(model_predictions).reshape((-1,len(model_predictions)))

        print(len(dates))
        print(len(model_predictions))
        predictions = pd.DataFrame(data=dates)
        predictions["pred"] = model_predictions
        return predictions

    def plot_data(predictions, real_data, title):
        plt.plot(predictions.datetime, predictions.pred, color='blue', marker='o', linestyle='dashed',label='Predicted Price')
        plt.plot(real_data.datetime, real_data.close, color='red', label='Actual Price')
        #plt.xlim(min(real_data.datetime), max(real_data.datetime) + datetime.timedelta(days=1))
        plt.title(f'{title} Prices Prediction')
        plt.xlabel('Date')
        plt.ylabel('Prices')
        plt.xticks(predictions.datetime)
        plt.legend()
        plt.show()
    """