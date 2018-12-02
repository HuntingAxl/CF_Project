from pandas import DataFrame, Series, concat, read_csv, datetime
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers.recurrent import LSTM
from math import sqrt
import matplotlib.pyplot as plt
import numpy
from numpy import concatenate
import os
import os.path as path

def int2date(date):
	dd = date%100
	date//=100
	mm = date%100
	yyyy = date//100
	month = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
	return str(dd)+'-'+month[mm]+'-'+str(yyyy)

def timeseries_to_supervised(data, lag=1):
    df = DataFrame(data)
    columns = [df.shift(i) for i in range(1, lag+1)]
    columns.append(df)
    return concat(columns, axis=1)
 
def difference(dataset, interval=1):
    diff = []
    for i in range(interval, len(dataset)):
    	value = dataset[i] - dataset[i - interval]
    	diff.append(value)
    series = Series(diff)
    return series
 
def inverse_difference(history, yhat, interval=1):
	return yhat + history[-interval]
 
def scale(train, test):
	scaler = MinMaxScaler(feature_range=(-1, 1))

	train = train.reshape(train.shape[0], train.shape[1])
	test = test.reshape(test.shape[0], test.shape[1])
	
	scaler = scaler.fit(train)
	train_scaled = scaler.transform(train)
	test_scaled = scaler.transform(test)

	return scaler, train_scaled, test_scaled
 
def invert_scale(scaler, X, yhat):
	new_row = [x for x in X] + [yhat]
	array = numpy.array(new_row)
	array = array.reshape(1, len(array))
	inverted = scaler.inverse_transform(array)
	return inverted[0, -1]
 

def fit_lstm(train, batch_size, nb_epoch, neurons, timesteps,dropout_factor=0.2):
	X, y = train[:, 0:-1], train[:, -1]
	X = X.reshape(X.shape[0], timesteps, 1)
	model = Sequential()
	model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]),  return_sequences=True))
	model.add(Dropout(dropout_factor))
	model.add(LSTM(neurons, batch_input_shape=(batch_size, X.shape[1], X.shape[2]), return_sequences=False))
	model.add(Dropout(dropout_factor))
	model.add(Dense(neurons))
	model.compile(loss='mean_squared_error', optimizer='adam')
	model.fit(X, y, epochs=nb_epoch, batch_size=batch_size, verbose=2, shuffle=False)
	return model
 

def forecast_lstm(model, batch_size, X):
	X = X.reshape(1, len(X), 1)
	yhat = model.predict(X, batch_size=batch_size)
	return yhat[0,0]
 

def experiment(repeats, series, timesteps, dates, filename, training_split=0.5):
	actual_data = series.values
	raw_values = series.values
	diff_values = difference(raw_values, 1)

	supervised = timeseries_to_supervised(diff_values, timesteps)
	supervised_values = supervised.values[timesteps:,:]

	stop_index = int(training_split*len(supervised_values))
	train, test = supervised_values[0:stop_index, :], supervised_values[stop_index:, :]

	scaler, train_scaled, test_scaled = scale(train, test)

	for r in range(repeats):
		nb_epoch = 3
		lstm_model = fit_lstm(train_scaled, 1, nb_epoch, 1, timesteps)

		predictions = list()
		for i in range(len(test_scaled)):

			X, y = test_scaled[i, 0:-1], test_scaled[i, -1]
			yhat = forecast_lstm(lstm_model, 1, X)
			yhat = invert_scale(scaler, X, yhat)
			yhat = inverse_difference(raw_values, yhat, len(test_scaled)+1-i)
			predictions.append(yhat)
		truth = raw_values[-len(predictions):]
		rmse = sqrt(mean_squared_error(truth, predictions))
		mae = mean_absolute_error(truth,predictions)
		dates = dates[-len(predictions):]
		# print(predictions,truth,sep='\n')
		plt.plot(dates,truth)
		plt.plot(dates,predictions)
		plt.xlabel('Dates')
		plt.ylabel('NAV')
		plt.title(filename)
		plt.savefig(filename)
		plt.close('all')
	return rmse, mae
 
def run():
	Folder_name = 'Final'
	files_list = os.listdir(Folder_name)
	results = []
	for filename in files_list:
		filename='Aditya Birla Sun Life Mutual Fund'
		file_path = path.join('Final',filename)
		series = read_csv(file_path, header=None, index_col=0, squeeze=True)
		# file_path = 'shampoo-sales.csv'
		# series = read_csv(file_path, header=0, parse_dates=[0], index_col=0, squeeze=True, date_parser=parser)
		repeats = 1

		timesteps = 7
		print('Training and Prediction - ',filename)
		dates = [ int2date(date) for date in series.index]
		rmse, mae = experiment(repeats, series, timesteps, dates, filename)
		print(filename+' RMSE : ',rmse)
		print(filename+' MAE : ',mae)
		results.append([rmse,mae])
	results = DataFrame(results)
	results.to_csv(path.join('Results.csv'), index=False)
 
if __name__ == '__main__':
	run()