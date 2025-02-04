#!/usr/bin/env python
# coding: utf-8

# In[18]:


import nest_asyncio
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler
from datetime import datetime, timedelta, timezone, date


# In[25]:


with open("parameters.txt", "r") as file:
    exec(file.read())


# In[20]:


decision = None


# In[28]:


async def alarm_and_decide():
    global decision
    # Apply the patch for nested asyncio event loops
    nest_asyncio.apply()
    
    user_input = None  # Variable to store the decision
    
    app = Application.builder().token(chatbot_token).build()  # Replace with your actual bot token
    
    # Create the buttons for "Yes" and "No"
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='yes')],
        [InlineKeyboardButton("No", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message with buttons
    await app.bot.send_message(chat_id=chat_id, text=f"🚨 {symbol} entry signal detected! 🚨 \n {datetime.now().strftime("%Y-%m-%d %I:%M %p")}\n   Take the trade?", reply_markup=reply_markup)
    
    async def handle_callback_query(update, context):
        global decision
        decision = update.callback_query.data  # Store the decision ("yes" or "no")
        
        # Acknowledge the callback
        await update.callback_query.answer()
    
        # Stop the polling loop immediately
        asyncio.get_event_loop().stop()  # Stop the event loop after the callback
        message_id = update.callback_query.message.message_id
        await context.bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        await context.bot.send_message(chat_id=chat_id, text=f"Your decision: {decision}")
    app.add_handler(CallbackQueryHandler(handle_callback_query))
    
    try:
        await app.run_polling()
    except (RuntimeError, RuntimeWarning) as RTE_RTW:
        pass



