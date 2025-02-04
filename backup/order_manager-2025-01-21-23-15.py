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


# In[4]:


def calculate_lot_size(SL_size):
    account_info = mt5.account_info()
    account_size = account_info.balance
    
    risk_amount = round(account_size,5) * 0.0025
    
    lot_size = (risk_amount) / (SL_size * 10)
    lot_size = round(lot_size,2)
    
    return lot_size


# ### BUY LIMIT ORDER 

# In[64]:


def place_buy_limit_order(symbol,limit_price, sl_price, tp_price, buy_tp):
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
    
    # Prepare the request 1 (0.8 of the positions)
    request1 = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": round(lot_size * 0.8,2),
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": limit_price,
        "sl": sl_price,
        "tp": tp_price,
        "deviation": 50,
        "magic": 123456,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
  
    # Send the 1st trade request
    result1 = mt5.order_send(request1)
    
    if result1.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Buy limit order placed successfully! Order ID: {result1.order}")
    else:
        print(f"Failed to place buy limit order. Retcode: {result1.retcode}")
# ---------------------------------------------------------  
    # Prepare the request 1 (0.2 of the positions)
    request2 = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": round(lot_size * 0.2,2),
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": limit_price,
        "sl": sl_price,
        "tp": buy_tp,
        "deviation": 50,
        "magic": 123456,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN,
    }
    
    # Send the 2nd trade request
    result2 = mt5.order_send(request2)

    if result2.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"Buy limit order placed successfully! Order ID: {result2.order}")
    else:
        print(f"Failed to place buy limit order. Retcode: {result2.retcode}")
    return


# ### BUY STOP ORDER

# In[60]:


def place_buy_stop_order(symbol,stop_price, sl_price, tp_price, buy_tp):
    
    SL_size = round(stop_price - sl_price,5) * 10000
    lot_size = calculate_lot_size(SL_size)     # Trade volume (lot size)
    
    # Ensure the symbol is available
    if not mt5.symbol_select(symbol, True):
        print(f"Failed to select symbol: {symbol}")
        mt5.shutdown()
        quit()
    
    # Prepare the request (80% of the volume)
    request1 = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": round(lot_size * 0.8,2),
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
    result1 = mt5.order_send(request1)
    if result1 is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result1.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Buy stop order placed successfully! Order ID: {result1.order}")
        else:
            print(f"Order failed, retcode: {result1.retcode}")
            print("Error details:", result1)
    #-------------------------------------------------

    # Prepare the request (20% of the volume)
    request2 = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": round(lot_size * 0.2,2),
        "type": mt5.ORDER_TYPE_BUY_STOP,  # Buy stop order
        "price": stop_price,  # The price at which the order will trigger (must be above current market price)
        "sl": sl_price,        # Stop Loss level
        "tp": buy_tp,        # Take Profit level
        "deviation": 50,       # Max price deviation (not used in pending orders)
        "magic": 123456,       # Unique identifier for your trades
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Return unused portion
    }

    # Send the trade request
    result2 = mt5.order_send(request2)
    
    # Check the result
    if result2 is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result2.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Buy stop order placed successfully! Order ID: {result2.order}")
        else:
            print(f"Order failed, retcode: {result2.retcode}")
            print("Error details:", result2)
    return


# ### SELL LIMIT ORDER

# In[56]:


def place_sell_limit_order(symbol,limit_price, sl_price, tp_price, sell_tp):

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
    
    # Prepare the request (0.8 of the volume)
    request1 = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": round(lot_size * 0.8,2),
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
    result1 = mt5.order_send(request1)

    if result1 is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result1.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Sell limit order placed successfully! Order ID: {result1.order}")
        else:
            print(f"Order failed, retcode: {result1.retcode}")
            print("Error details:", result1)
    #---------------------------------
    # Prepare the request (0.2 of the volume)
    request2 = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": round(lot_size * 0.2,2),
        "type": mt5.ORDER_TYPE_SELL_LIMIT,  # Sell limit order
        "price": limit_price,  # The price at which the order will trigger
        "sl": sl_price,        # Stop Loss level
        "tp": sell_tp,        # Take Profit level
        "deviation": 50,       # Max price deviation (not used in pending orders)
        "magic": 123456,       # Unique identifier for your trades,
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Return unused portion
    }
    
    # Send the trade request
    result2 = mt5.order_send(request2)
    
    if result2 is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result2.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Sell limit order placed successfully! Order ID: {result2.order}")
        else:
            print(f"Order failed, retcode: {result2.retcode}")
            print("Error details:", result2)
    return


# ### SELL STOP ORDER

# In[68]:


def place_sell_stop_order(symbol,stop_price, sl_price, tp_price, sell_tp):
    
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
    
    # Prepare the request (80% of the volume)
    request1 = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": round(lot_size * 0.8 ,2),
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
    result1 = mt5.order_send(request1)

    if result1 is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result1.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Sell limit order placed successfully! Order ID: {result1.order}")
        else:
            print(f"Order failed, retcode: {result1.retcode}")
            print("Error details:", result1)
    #------------------------------------------------------
    # Prepare the request (20% of the volume)
    request2 = {
        "action": mt5.TRADE_ACTION_PENDING,  # Pending order
        "symbol": symbol,
        "volume": round(lot_size * 0.2 ,2),
        "type": mt5.ORDER_TYPE_SELL_STOP,  # Sell stop order
        "price": stop_price,  # The price at which the order will trigger (must be below current market price)
        "sl": sl_price,        # Stop Loss level
        "tp": sell_tp,        # Take Profit level
        "deviation": 50,       # Max price deviation (not used in pending orders)
        "magic": 123456,       # Unique identifier for your trades
        "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
        "type_filling": mt5.ORDER_FILLING_RETURN,  # Return unused portion
    }
    
    
    # Send the trade request
    result2 = mt5.order_send(request2)
    # Check the result
    if result2 is None:
        print("Failed to send order. Error:", mt5.last_error())
    else:
        if result2.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"Sell limit order placed successfully! Order ID: {result2.order}")
        else:
            print(f"Order failed, retcode: {result2.retcode}")
            print("Error details:", result2)
    return


# ### MOVING THE STOP LOSS  FOR AN ONGOING TRADE (FOR BOTH BUYS AND SELLS)

# In[76]:


def trail_stop_loss(symbol, new_stop_loss):
    """
    Adjusts the stop loss for all open positions of the given symbol, grouping them by symbol.
    """
    # Retrieve all open positions
    positions = mt5.positions_get()

    if positions is None or len(positions) == 0:
        print("No active positions found.")
        mt5.shutdown()
        return

    # Filter positions by the provided symbol
    positions_by_symbol = [position for position in positions if position.symbol == symbol]

    if len(positions_by_symbol) == 0:
        print(f"No active positions found for symbol: {symbol}")
        return

    # Iterate over all positions for the given symbol and adjust stop loss
    for position in positions_by_symbol:
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
            print(f"Failed to modify stop loss for position {position.ticket}. Error:", mt5.last_error())
        else:
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"Stop loss modified successfully for position {position.ticket}. New SL: {new_stop_loss}")
            else:
                print(f"Failed to modify stop loss for position {position.ticket}, retcode: {result.retcode}")
                print("Error details:", result)

    print(f"Stop loss adjustment completed for all positions of symbol: {symbol}")


# ### DELETING AN ORDER (BUY LIMIT, BUY ORDER, SELL LIMIT, SELL ORDER)

# In[74]:


def delete_order(symbol):
    # Retrieve all pending orders
    orders = mt5.orders_get()
    
    if orders is None or len(orders) == 0:
        print("No active orders or failed to retrieve orders.")
        return
    else:
        # Group orders by entry price
        orders_by_price = {}
        for order in orders:
            entry_price = order.price_open  # Entry price of the order
            if entry_price not in orders_by_price:
                orders_by_price[entry_price] = []
            orders_by_price[entry_price].append(order)
        # Delete orders with the same entry price
        for price, orders_list in orders_by_price.items():
            if len(orders_list) > 1:  # Only act on duplicate entry prices
                print(f"Deleting orders with the same entry price ({price}):")
                for order in orders_list:
                    delete_request = {
                        "action": mt5.TRADE_ACTION_REMOVE,
                        "order": order.ticket,  # Order ID to delete
                        "magic": order.magic,   # Magic number
                        "symbol": order.symbol  # Symbol of the order
                    }
                    # Send the delete request
                    result = mt5.order_send(delete_request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        print(f"Order {order.ticket} deleted successfully.")
                    else:
                        print(f"Failed to delete order {order.ticket}. Retcode: {result.retcode}")
    # Send the request to delete the order
    return 

