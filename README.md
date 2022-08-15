# StableBaselines_AlgoTrade

## Overview 
This app uses the StableBaselines3 library to train and run live traiding using the alpaca environment. The app additionall uses the Alpha Vantage API and Yahoo Finance API to download historic and live data 

## Configure
Before running the app you must an 'alpaca_keys.json' file in the /app directory to store your alpaca credentials. the file should have the following format.
```
{
 "BASE_URL" :"https://paper-api.alpaca.markets"
 ,"ALPACA_API_KEY": "[your alpaca api key]"
,"ALPACA_SECRET_KEY" :"[your alpaca api secret key]"
,"ALPHA_V":"[your alpha vantage key]"}
```
save this file 

## Executing the application
To execute the application you can install the required libraries in the app/requirements.txt file and running
```
python start_ppo.py
```
using python 3.8 or greater.

Alternatively you can run using the docker file by building the image
```
docker build . 
docker run
```
