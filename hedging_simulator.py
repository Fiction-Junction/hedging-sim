# -*- coding: utf-8 -*-
"""Hedging Simulator.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1uqaPBvX5jVRRqoM7jxyVt7nyI6SdLkg7

Hedging Simulator

Portfolio Replication of a Call Option via Delta Hedging
"""

# Commented out IPython magic to ensure Python compatibility.
# # saves app into .py file that Colab can run on Streamlit
# %%writefile delta_hedging_app.py
# 
# import numpy as np
# from scipy.stats import norm
# import matplotlib.pyplot as plt
# import yfinance as yf
# import streamlit as st
# 
# # st header
# st.set_page_config(page_title="Hedging Simulator")
# st.title("Portfolio Replication of Options via Delta Hedging")
# 
# st.markdown("""
# Replicates the prices of options through **delta hedging** and compares it to those
# obtained from the **Black-Scholes formula** over historical stock data.
# """)
# 
# # st inputs
# ticker = st.text_input("Stock Ticker (e.g. AAPL)", value="AAPL")
# opt_type = st.selectbox("Option Type", ["call", "put"])
# pos = st.selectbox("Position", ["long", "short"])
# K = st.number_input("Strike Price (K)", value=100.0)
# T_mat = st.number_input("Time to Maturity (in days)", value=10)
# r = st.number_input("Risk-Free Rate (r)", value=0.05)
# sigma = st.number_input("Volatility (σ)", value=0.2)
# start_date = st.date_input("Start date for historical stock prices")
# end_date = st.date_input("End date for historical stock prices")
# 
# # calc helper function for bs price and greeks
# def calc(opt_type, pos, S, K, T_mat, r, sigma): # T_mat in days
#     d1 = (np.log(S/K) + (r + (sigma ** 2) / 2) * T_mat) / (sigma * np.sqrt(T_mat))
#     d2 = d1 - sigma * np.sqrt(T_mat)
# 
#     def helper(output, *subtype):
#         if output == "bs price": # black-scholes price
#             if opt_type == "call":
#                 return S * norm.cdf(d1) - K * np.exp(-r * T_mat) * norm.cdf(d2)
#             if opt_type == "put":
#                 return K * np.exp(-r * T_mat) * norm.cdf(-d2) - S * norm.cdf(-d1)
# 
#         if output == "greek": # greeks
#             if subtype[0] == "delta": # delta
#                 if opt_type == "call":
#                     return norm.cdf(d1)
#                 if opt_type == "put":
#                     return -norm.cdf(-d1)
# 
#             if subtype[0] == "gamma": # gamma
#                 return norm.pdf(d1) / (S * sigma * np.sqrt(T_mat)) # output is the same regardless of option type
#     return helper
# 
# # hedging
# def hedge(opt_type, pos, K, T_mat, r, sigma, stock_prices): # T_mat in days
# 
#     trading_days = 365 - 2*52 - 10 # avg 251 trading days per year after subtracting 104 weekends & ~10 holidays
#     dt = 1/trading_days # differential for ease of calculation
#     data_days = len(stock_prices) # no of days from historical data
# 
#     if data_days < T_mat:
#         print("Insufficient data to simulate time to maturity of the option")
#         return
# 
#     # lists to store and compare the replicated and actual prices
#     replicated_prices = []
#     bs_opt_prices = []
#     delta = []
# 
#     # 0th cycle
#     S0 = stock_prices[0]
#     parameters = calc(opt_type, pos, S0, K, T_mat * dt, r, sigma) # T_mat in days
#     bs_opt_prices.append(parameters('bs price'))
#     delta.append(parameters('greek', 'delta'))
# 
#     if (pos == 'long' and opt_type == 'call') or (pos == 'short' and opt_type == 'put'): # long call / short put
#         cash = -bs_opt_prices[0] + delta[0] * S0
#         underlying = -delta[0] * S0
# 
#     if (pos == 'short' and opt_type == 'call') or (pos == 'long' and opt_type == 'put'): # short call / long put
#         cash = bs_opt_prices[0] - delta[0] * S0
#         underlying = delta[0] * S0
# 
#     replicated_prices.append(cash + underlying) # end of 0th cycle: X(0) approx C(0)
# 
#     t_mat = T_mat # reassignment to new variable so that T_mat can be freed up
# 
#     for t in range(1, T_mat):
#         t_mat -= 1 # reducing time to maturity by one day
#         S_t = stock_prices[t] # assigning current stock price from historical data
#         underlying = delta[t - 1] * S_t
#         cash *= np.exp(r * dt) # cash accumulates interest
# 
#         parameters = calc(opt_type, pos, S_t, K, t_mat * dt, r, sigma) # T_mat in days
#         bs_opt_prices.append(parameters('bs price'))
#         delta.append(parameters('greek', 'delta'))
# 
#         cash -= (delta[t] - delta[t - 1]) * S_t
#         underlying = delta[t] * S_t
# 
#         replicated_prices.append(cash + underlying) # end of t'th cycle: X(t) approx C(t)
# 
#     return replicated_prices, bs_opt_prices
# 
# if st.button("Simulate"):
#     if ticker and K and T_mat and r and sigma and start_date < end_date:
#         try:
#             data = yf.download(ticker, start=start_date, end=end_date)
# 
#             if data.empty: # data does not exist for whatever reason
#                 st.error("No data available for the specified date range.")
#                 st.stop()
# 
#             stock_prices = data['Adj Close'].values # assign data to stock_prices
# 
#             if len(stock_prices) >= 10:
#                 replicated_prices, bs_opt_prices = hedge(opt_type, pos, K, T_mat, r, sigma, stock_prices)
#                 st.write("Replicated Prices:", replicated_prices)
#                 st.write("Black-Scholes Prices:", bs_opt_prices)
#             else:
#                 st.error("Insufficient data to simulate time to maturity of the option")
#         except Exception as e:
#             st.error(f"Error: {e}")
#     else:
#         st.error("Please fill in all the required fields. The start date also has to be before the end date.")
# 
