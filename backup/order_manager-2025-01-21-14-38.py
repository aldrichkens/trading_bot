#!/usr/bin/env python
# coding: utf-8

# In[1]:


import MetaTrader5 as mt5


# In[2]:

def log_in_to_mt5():
    if not mt5.initialize(login=89500879, server="MetaQuotes-Demo", password="6kF-FhYd"):
        print("Initialization failed")
        print(mt5.last_error())
        quit()
    
    print("Connected to MT5 successfully")


# In[3]:


def calculate_lot_size(SL_size):
    account_info = mt5.account_info()
    account_size = account_info.balance
    
    risk_amount = round(account_size,5) * 0.0025
    
    lot_size = (risk_amount) / (SL_size * 10)
    lot_size = round(lot_size,2)
    
    return lot_size


# ### BUY LIMIT ORDER 

# In[ ]:


def place_buy_limit_order(symbol,limit_price, sl_price, tp_price):
    SL_size = round(limit_price - sl_price,5) * 10000
    lot_size = calculate_lot_size(SL_size)     # Trade volume (lot size)
    
    # Ensure the symbol is available
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol: {symbol}")
        mt5.shutdown()
        quit()
    
    # Validate SL and TP distances
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        mt5.shutdown()
        quit()
    
    # Prepare the request
    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": limit_price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 50,
        "magic": 123456,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    
    # Send the trade request
    result = mt5.order_send(request)

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Buy limit order placed successfully!")
    else:
        print(f"Failed to place buy limit order. Retcode: {result.retcode}")
    
    return result


# ### BUY STOP ORDER

# In[ ]:


def place_buy_stop_order(symbol,stop_price, sl_price, tp_price):
    
    SL_size = round(stop_price - sl_price,5) * 10000
    lot_size = calculate_lot_size(SL_size)     # Trade volume (lot size)
    
    # Ensure the symbol is available
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol: {symbol}")
        mt5.shutdown()
        quit()
    
    # Prepare the request
    request = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY_STOP,  # Buy stop order
        "price": stop_price,  # The price at which the order will trigger (must be above current market price)
        "sl": sl_price,        # Stop Loss level
        "tp": tp_price,        # Take Profit level
        "deviation": 50,       # Max price deviation (not used in pending orders)
        "magic": 123456,       # Unique identifier for your trades
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Return unused portion
    }

    # Send the trade request
    result = mt5.order_send(request)
    # Check the result
    if result is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Buy stop order placed successfully! Order ID: {result.order}")
        else:
            print(f"Order failed, retcode: {result.retcode}")
            print("Error details:", result)
    return result


# ### SELL LIMIT ORDER

# In[ ]:


def place_sell_limit_order(symbol,limit_price, sl_price, tp_price):

    SL_size = round(sl_price - limit_price,5) * 10000
    lot_size = calculate_lot_size(SL_size)     # Trade volume (lot size)
    
    # Ensure the symbol is available
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol: {symbol}")
        mt5.shutdown()
        quit()
    
    # Validate SL and TP distances
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        mt5.shutdown()
        quit()
    
    # Prepare the request
    request = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,  # Sell limit order
        "price": limit_price,  # The price at which the order will trigger
        "sl": sl_price,        # Stop Loss level
        "tp": tp_price,        # Take Profit level
        "deviation": 50,       # Max price deviation (not used in pending orders)
        "magic": 123456,       # Unique identifier for your trades,
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Return unused portion
    }
    
    # Send the trade request
    result = mt5.order_send(request)
    if result is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Sell limit order placed successfully! Order ID: {result.order}")
        else:
            print(f"Order failed, retcode: {result.retcode}")
            print("Error details:", result)
    return


# ### SELL STOP ORDER

# In[ ]:


def place_sell_stop_order(symbol,stop_price, sl_price, tp_price):
    
    SL_size = round(sl_price - stop_price,5) * 10000
    lot_size = calculate_lot_size(SL_size)     # Trade volume (lot size)

    # Ensure the symbol is available
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol: {symbol}")
        mt5.shutdown()
        quit()
    
    # Validate SL and TP distances
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Symbol {symbol} not found")
        mt5.shutdown()
        quit()
    
    # Prepare the request
    request = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_SELL_STOP,  # Sell stop order
        "price": stop_price,  # The price at which the order will trigger (must be below current market price)
        "sl": sl_price,        # Stop Loss level
        "tp": tp_price,        # Take Profit level
        "deviation": 50,       # Max price deviation (not used in pending orders)
        "magic": 123456,       # Unique identifier for your trades
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Return unused portion
    }
    
    
    # Send the trade request
    result = mt5.order_send(request)
    # Check the result
    if result is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Sell limit order placed successfully! Order ID: {result.order}")
        else:
            print(f"Order failed, retcode: {result.retcode}")
            print("Error details:", result)
    return result


# ### MOVING THE STOP LOSS  FOR AN ONGOING TRADE (FOR BOTH BUYS AND SELLS)

# In[12]:


def trail_stop_loss(symbol, new_stop_loss):
    # Retrieve all open positions
    positions = mt5.positions_get()
    
    if positions is None or len(positions) == 0:
        print("No active positions found.")
        mt5.shutdown()
        quit()
    
    # Filter positions by the provided symbol
    for position in positions:
        if position.symbol == symbol:  # Match the specific symbol
            # Prepare the modification request to update the Stop Loss
            request = {
                "action": mt5.TRADE_ACTION_SLTP,  # Specify action for Stop Loss / Take Profit modification
                "symbol": position.symbol,        # Symbol of the position
                "sl": new_stop_loss,              # New Stop Loss price provided by your logic
                "tp": position.tp,                # Keep the existing Take Profit
                "position": position.ticket,      # Position ID of the trade to modify
                "deviation": 50,                  # Max price deviation allowed
                "magic": position.magic,          # Unique identifier for your trades
                "comment": "Trailing Stop Adjust",# Comment for the trade modification
            }
            
            # Send the modification request
            result = mt5.order_send(request)
            # Check the result of the request
            if result is None:
                print("Failed to modify stop loss. Error:", mt5.last_error())
            else:
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    print(f"Stop loss modified successfully!")
                else:
                    print(f"Failed to modify stop loss, retcode: {result.retcode}")
                    print("Error details:", result)
            return
    
    print(f"No active positions found for symbol: {symbol}")
    return None


# ### DELETING AN ORDER (BUY LIMIT, BUY ORDER, SELL LIMIT, SELL ORDER)

# In[14]:


def delete_order(symbol):
    # Retrieve all pending orders
    orders = mt5.orders_get()
    
    if orders is None or len(orders) == 0:
        print("No pending orders found.")
    else:
        for order in orders:
            if order.symbol == symbol:  # Match the specific symbol
                # Prepare the modification request to update the Stop Loss
                for order in orders:
                    # Prepare the request to delete the pending order
                    request = {
                        "action": mt5.TRADE_ACTION_REMOVE,  # Action to delete the order
                        "order": order.ticket,             # Ticket ID of the pending order
                        "symbol": order.symbol,            # Symbol of the order
                        "magic": order.magic,              # Unique identifier for your trades
                        "comment": "Deleting pending order",  # Comment for the deletion
                    }
            else:
                print(f"No pending orders for {symbol}!")
                return None
                
            # Send the request to delete the order
            result = mt5.order_send(request)
            
            # Check the result of the operation
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Trade order deleted successfully.")
            else:
                print(f"Failed to delete order!")
            return result

