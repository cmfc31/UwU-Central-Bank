import os
import telebot
import time
import pymongo
from datetime import datetime
from bson.objectid import ObjectId

# Define a new client
MONGO_CONNSTRING = os.environ['MONGO_CONNSTRING']
client = pymongo.MongoClient(MONGO_CONNSTRING)

# Get the database (database name by default is "test")
db = client.mon_db

API_KEY = os.environ['API_KEY']
bot = telebot.TeleBot(API_KEY)

# Check if bot's being used in allowed groups/chats
def check_allowed_chatid(message):
	if(message.chat != None):
		chats = db.chat
		c_list = list(chats.find({}))
		if(any(message.chat.id == x['id'] for x in c_list)):
			return True
		else:
			return False
	else:
		return False
	

# Lock user balance
@bot.message_handler(commands=['lock_balance'], func=check_allowed_chatid)
def lock_balance(message):
	admin_list = bot.get_chat_administrators(message.chat.id)

	# Check if user is an creator of the group chat
	if(any(x.user.id == message.from_user.id and x.status == 'creator' for x in admin_list)):
		if (message.reply_to_message != None):
			users = db.user
			user = users.find_one({'id': message.reply_to_message.from_user.id})
			sent_message = None
			# Check if user is already registered in the db
			if(user != None):			
				if(user['locked']):
					sent_message = bot.reply_to(message, 'User is already locked!')
				else:	
					users.update_one({'id': user['id']}, 
						{'$set' : {'locked': True}})
					sent_message = bot.reply_to(message, 'User balance has been locked. 🔒')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
			else:						
				sent_message = bot.reply_to(
						message,
						'User not registered yet, they need to send a pic, video or document to the group first!'
				)
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try replying with /lock_balance to another member.')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		sent_message = bot.reply_to(
				message, 'Only Mariana can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Lock user balance
@bot.message_handler(commands=['unlock_balance'], func=check_allowed_chatid)
def unlock_balance(message):
	admin_list = bot.get_chat_administrators(message.chat.id)

	# Check if user is an creator of the group chat
	if(any(x.user.id == message.from_user.id and x.status == 'creator' for x in admin_list)):
		if (message.reply_to_message != None):
			users = db.user
			user = users.find_one({'id': message.reply_to_message.from_user.id})
			sent_message = None
			# Check if user is already registered in the db
			if(user != None):
				if(not user['locked']):
					sent_message = bot.reply_to(message, 'User is already unlocked!')
				else:	
					users.update_one({'id': user['id']}, 
						{'$set' : {'locked': False}})
					sent_message = bot.reply_to(message, 'User balance has been unlocked. 🔓')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
			else:						
				sent_message = bot.reply_to(
						message,
						'User not registered yet, they need to send a pic, video or document to the group first!'
				)
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try replying with /unlock_balance to another member.')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		sent_message = bot.reply_to(
				message, 'Only Mariana can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Add balance to user
@bot.message_handler(commands=['add_balance'], func=check_allowed_chatid)
def add_balance(message):
	admin_list = bot.get_chat_administrators(message.chat.id)

	# Check if user is an creator of the group chat
	if(any(x.user.id == message.from_user.id and x.status == 'creator' for x in admin_list)):
		if (len(message.text.split(' ')) >= 2 and message.reply_to_message != None):			
			second_word = message.text.split(' ')[1]
			try:
				users = db.user
				user = users.find_one({'id': message.reply_to_message.from_user.id})
				amount = int(second_word)
				sent_message = None
				# Check if user is already registered in the db
				if(user != None):
					# Check if user has enough balance
					if (amount > 0 and user['locked'] == False):
						# Increase balance to user
						users.update_one({'id': user['id']}, 
							{'$set' : {'balance': user['balance'] + amount}})

						usrname = ''
						if (message.reply_to_message.from_user.username != None):
							usrname = f" @{message.reply_to_message.from_user.username}"

						# Succeed message
						sent_message = bot.reply_to(
								message,
								f"Good news{usrname}, your balance has been increased by {amount}! uwu"
						)
					else:				
						sent_message = bot.reply_to(
								message,
								"Amount must be higher than zero or user balance is locked."
						)
					time.sleep(5)
					try:
						bot.delete_message(sent_message.chat.id, sent_message.message_id)
						bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
				else:						
					sent_message = bot.reply_to(
							message,
							'User not registered yet, they need to send a pic, video or document to the group first!'
					)
					time.sleep(5)
					try:
						bot.delete_message(sent_message.chat.id, sent_message.message_id)
						bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
			except ValueError:
				# Handle the exception
				sent_message = bot.reply_to(
						message, 'Please enter an integer for the amount.')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try replying with /add_balance [amount] to another member.')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		sent_message = bot.reply_to(
				message, 'Only Mariana can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Remove balance to user
@bot.message_handler(commands=['remove_balance'], func=check_allowed_chatid)
def remove_balance(message):
	admin_list = bot.get_chat_administrators(message.chat.id)

	# Check if user is a creator of the group chat
	if(any(x.user.id == message.from_user.id and x.status == 'creator' for x in admin_list)):
		if (len(message.text.split(' ')) >= 2 and message.reply_to_message != None):			
			second_word = message.text.split(' ')[1]
			try:
				users = db.user
				user = users.find_one({'id': message.reply_to_message.from_user.id})
				amount = int(second_word)
				sent_message = None
				# Check if user is already registered in the db
				if(user != None):
					# Check if user has enough balance
					if (amount > 0 and user['locked'] == False):
						# Increase balance to user
						res_bal = user['balance'] - amount
						if(res_bal < 0):
							res_bal = 0

						users.update_one({'id': user['id']}, 
							{'$set' : {'balance': res_bal}})

						usrname = ''
						if (message.reply_to_message.from_user.username != None):
							usrname = f" @{message.reply_to_message.from_user.username}"

						# Succeed message
						sent_message = bot.reply_to(
								message,
								f"Bad news{usrname}, your balance has been decreased by {amount}! 😳"
						)
					else:				
						sent_message = bot.reply_to(
								message,
								"Amount must be higher than zero or user balance is locked."
						)
					time.sleep(5)
					try:
						bot.delete_message(sent_message.chat.id, sent_message.message_id)
						bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
				else:						
					sent_message = bot.reply_to(
							message,
							'User not registered yet, they need to send a pic, video or document to the group first!'
					)
					time.sleep(5)
					try:
						bot.delete_message(sent_message.chat.id, sent_message.message_id)
						bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
			except ValueError:
				# Handle the exception
				sent_message = bot.reply_to(
						message, 'Please enter an integer for the amount.')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try replying with /remove_balance [amount] to another member.')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		sent_message = bot.reply_to(
				message, 'Only Mariana can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Allow chat id to use the bot
@bot.message_handler(commands=['allow_chat'], func=check_allowed_chatid)
def allow_chat(message):
	admin_list = bot.get_chat_administrators(message.chat.id)

	# Check if user is an creator of the group chat
	if(any(x.user.id == message.from_user.id and x.status == 'creator' for x in admin_list)):
		if (len(message.text.split(' ')) >= 2):
			# Check if chat id is already added
			chats = db.chat
			c_list = list(chats.find({}))
			second_word = message.text.split(' ')[1]
			try:			
				chat_id = int(second_word)
				sent_message = None
				if (any(x['id'] == chat_id for x in c_list)):
					sent_message = bot.reply_to(
							message,
							'Chat id is already in the allowed chat list.' 
					)
				else:
					# Add chat id to db
					chats.insert_one({'id': chat_id})
					sent_message = bot.reply_to(
							message,
							'Chat id added correctly.' 
					)
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
			except ValueError:
				# Handle the exception
				sent_message = bot.reply_to(
						message, 'Please enter an integer for the chat id.')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)					
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:			
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try /allow_chat [chat_id]')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else: 
		sent_message = bot.reply_to(
				message, 'Only Mariana can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Remove chat id to use the bot
@bot.message_handler(commands=['remove_chat'], func=check_allowed_chatid)
def remove_chat(message):
	admin_list = bot.get_chat_administrators(message.chat.id)

	# Check if user is an creator of the group chat
	if(any(x.user.id == message.from_user.id and x.status == 'creator' for x in admin_list)):
		if (len(message.text.split(' ')) >= 2):
			# Check if chat id is already added
			chats = db.chat
			c_list = list(chats.find({}))
			second_word = message.text.split(' ')[1]
			try:			
				chat_id = int(second_word)
				sent_message = None
				if (any(x['id'] == chat_id for x in c_list)):
					chats.delete_one({'id': chat_id})
					sent_message = bot.reply_to(
							message,
							'Chat id removed.' 
					)
				else:				
					sent_message = bot.reply_to(
							message,
							'Chat id you entered is not in the allowed list.' 
					)
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
			except ValueError:
				# Handle the exception
				sent_message = bot.reply_to(
						message, 'Please enter an integer for the chat id.')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:			
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try /remove_chat [chat_id]')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else: 
		sent_message = bot.reply_to(
				message, 'Only Mariana can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Check current balance
@bot.message_handler(commands=['balance'], func=check_allowed_chatid)
def check_balance(message):
	users = db.user
	user = users.find_one({'id': message.from_user.id})
	sent_message = None
	if (user != None):
		status = ''
		if(user['locked']):
			status = 'locked 🔒'
		else:
			status = 'unlocked 🔓'
		sent_message = bot.reply_to(
				message, f"Your current balance is: {user['balance']} 💰, state: {status}")
	else:
		sent_message = bot.reply_to(
				message,
				'User not registered, try sending a pic, video or document to the group!'
		)
	time.sleep(5)
	try:
		bot.delete_message(sent_message.chat.id, sent_message.message_id)
		bot.delete_message(message.chat.id, message.message_id)
	except:
		pass

# Check top balances
@bot.message_handler(commands=['list_balances'], func=check_allowed_chatid)
def list_balances(message):
	# Check if user is an admin of the chat
	admin_list = bot.get_chat_administrators(message.chat.id)
	if(any(x.user.id == message.from_user.id for x in admin_list)):
		users = db.user
		u_list = list(users.find({}).limit(10).sort("balance",pymongo.DESCENDING))
		sent_message = None
		res = None
		cont = 0
		if (len(u_list) > 0):
			res = 'TOP RICHEST MEMBERS! 💸😳\n'
			for user in u_list:	
				cont += 1
				res = res + f"\n{cont}. {user['username']} — {user['balance']}"
			sent_message = bot.reply_to(message,res)
		else:
			sent_message = bot.reply_to(
					message,
					'There are no active members' 
			)
		time.sleep(10)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass
	else: 
		sent_message = bot.reply_to(
				message, 'Only Blessed Guardians can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Donate to member
@bot.message_handler(commands=['donate'], func=check_allowed_chatid)
def donate(message):
	if (len(message.text.split(' ')) >= 2 and message.reply_to_message != None):
		# If command is correctly written check if second word is a valid int	
		second_word = message.text.split(' ')[1]
		try:
			users = db.user
			user = users.find_one({'id': message.reply_to_message.from_user.id})
			donator = users.find_one({'id': message.from_user.id})
			amount = int(second_word)
			sent_message = None
			# Check if user is already registered in the db
			if(user != None and donator != None):
				# Check if user has enough balance
				if (donator['balance'] >= amount and amount > 0 and donator['locked'] == False and user['locked'] == False):
					# Remove donated amount from user who donated
					users.update_one({'id': donator['id']}, 
						{'$set' : {'balance': donator['balance'] - amount}})

					# Increase balance to user who received the donation
					users.update_one({'id': user['id']}, 
						{'$set' : {'balance': user['balance'] + amount}})

					usrname = ''
					if (message.reply_to_message.from_user.username != None):
						usrname = f" to @{message.reply_to_message.from_user.username}"

					# Succeed message
					sent_message = bot.reply_to(
							message,
							f"You succesfully donated {amount} blessed coin(s){usrname}, wholesome!🥺❤"
					)
				else:				
					sent_message = bot.reply_to(
							message,
							"You don't have enough balance to donate that amount, you entered a negative amount or donator/receiver has their balance locked."
					)
					time.sleep(10)
					try:
					  bot.delete_message(sent_message.chat.id, sent_message.message_id)
					  bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
			else:						
				sent_message = bot.reply_to(
						message,
						'Donator or receiver is not registered yet, they need to send a pic, video or document to the group first!'
				)
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		except ValueError:
			# Handle the exception
			sent_message = bot.reply_to(
					message, 'Please enter an integer for the amount.')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:			
		# In case no parameters
		sent_message = bot.reply_to(message, 'Try replying with /donate [amount] to another member.')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass
	
# List available bounties
@bot.message_handler(commands=['list_bounties'], func=check_allowed_chatid)
def list_bounties(message):
	bounties = db.bounty
	b_list = list(bounties.find({}))
	if (len(b_list) > 0):
		res = "*BOUNTY LIST!* 💰\n\nHowdy! Look at all those sweet rewards waiting for you. First member to solve a request correctly gets the price."

		for bty in list(b_list):
			res = res + f"\n\n*Bounty ID:* {bty['id']}\n*Reward:* {bty['quantity']}\n*Description:* {bty['description']}"

		res = res + "\n\n_SEE YOU BRAVE COWBOY..._ 🥰"
		sent_message = bot.reply_to(message, res, parse_mode="markdown")
		time.sleep(20)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass
	else:
		sent_message = bot.reply_to(message, f"There are no active bounties.")
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Return bounty
@bot.message_handler(commands=['return'], func=check_allowed_chatid)
def return_bounty(message):
	admin_list = bot.get_chat_administrators(message.chat.id)
	# Check if user is an admin in the group
	if(any(x.user.id == message.from_user.id for x in admin_list)):
		# Check parameters
		if (len(message.text.split(' ')) >= 2):
			bounties = db.bounty
			second_word = message.text.split(' ')[1]
			try:			
				bounty_id = int(second_word)
				sent_message = None
				bty = bounties.find_one({'id': bounty_id})
				if (bty != None):
					# Increase user balance with returned bounty_id
					users = db.user
					user = users.find_one({'id': message.from_user.id})
					users.update_one({'id': user['id']}, {'$set': { 'balance': user['balance'] + bty['quantity']}})

					# Remove bounty from table
					bounties.delete_one({'id': bty['id']})

					sent_message = bot.reply_to(
							message,
							f"*Bounty ID:* {bty['id']} returned. Good luck next time!",
							parse_mode="markdown"
					)
				else:
					# Bounty id not found
					sent_message = bot.reply_to(
							message,
							'Bounty ID not found.' 
					)
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
			except ValueError:
				# Handle the exception
				sent_message = bot.reply_to(
						message, 'Please enter an integer for the bounty ID.')
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)					
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:			
			# In case no parameters
			sent_message = bot.reply_to(message, 'Try with /return [Bounty ID]')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		sent_message = bot.reply_to(
		message, 'Only Blessed Guardians can execute this command!')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Give bounty reward to user
@bot.message_handler(commands=['thx'], func=check_allowed_chatid)
def give_bounty(message):
	if (message.reply_to_message != None):
		bounty_winner = message.reply_to_message.from_user.id

		# Check if user is already registered
		users = db.user
		bounties = db.bounty
		user = users.find_one({'id': bounty_winner})
		if (user != None):
			# Check if user is not rewarding to himself
			if(message.from_user.id != bounty_winner and user['locked'] == False):
				# Check if current user has bounties to give
				bty = bounties.find_one({'user_id': message.from_user.id})
				if (bty != None):
					# Increase user balance with bounty reward
					users.update_one({'id': bounty_winner}, {'$set': { 'balance': user['balance'] + bty['quantity']}})
					usrname = ''
					if (message.reply_to_message.from_user.username != None):
						usrname = f" @{message.reply_to_message.from_user.username}"

					# Remove bounty from table
					bounties.delete_one({'id': bty['id']})

					sent_message = bot.reply_to(
							message,
								f"Good job{usrname}!, you got the bounty and your balance has been increased by +{bty['quantity']} 🤑"
					)
				else:
					sent_message = bot.reply_to(message,'You have no bounties to give!')
					time.sleep(5)
					try:
						bot.delete_message(sent_message.chat.id, sent_message.message_id)
						bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
			else:
				sent_message = bot.reply_to(message,"You can't use /thx command with yourself or bounty winner has their balance locked.")
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		else:
			sent_message = bot.reply_to(
					message,
					'User not registered yet, they need to send a pic, video or document to the group first!'
			)
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		sent_message = bot.reply_to(
				message, f"Reply to a message of the user who solved the request with /thx")
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Set bounty for sauce
@bot.message_handler(commands=['bounty'], func=check_allowed_chatid)
def set_bounty(message):
	users = db.user
	bounties = db.bounty
	if (len(message.text.split(' ')) >= 3):
		first_word = message.text.split(' ')[0]
		second_word = message.text.split(' ')[1]
		try:
			quantity = int(second_word)
			description = message.text.replace(f"{first_word} {quantity} ", '')

			# Check if user has enough balance
			user = users.find_one({'id': message.from_user.id})
			if (user != None and user['balance'] >= quantity and quantity > 0 and user['locked'] == False):
				# Check if user has an active bounty
				active_bty = bounties.find_one({'user_id': user['id']})
				if(active_bty == None):
					# Insert bounty in table
					doc_id = bounties.insert_one({
							'user_id': user['id'],
							'quantity': quantity,
							'description': description
					})

					# Remove balance from user balance
					users.update_one({'id': user['id']}, 
						{'$set' : {'balance': user['balance'] - quantity}})

					# Consult generated auto-increment id
					last_bty = bounties.find_one({'_id': ObjectId(doc_id.inserted_id)})
					auto_id = last_bty['id']

					bot.reply_to(
						message,
						f"New bounty configured! 😳💰\n\n*Bounty ID:* {auto_id}\n*Reward:* {quantity}\n*Description:* {description}",
						parse_mode="markdown")
				else:
					sent_message = bot.reply_to(message, f"You already have an active bounty. Users can only have one active bounty at the time. ☝🤓")
					time.sleep(5)
					try:
						bot.delete_message(sent_message.chat.id, sent_message.message_id)
						bot.delete_message(message.chat.id, message.message_id)
					except:
						pass
			else:
				sent_message = bot.reply_to(
						message,
						f"You don't have enough balance to set this bounty, you entered a negative bounty or your balance is locked.")
				time.sleep(5)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
					bot.delete_message(message.chat.id, message.message_id)
				except:
					pass
		except ValueError:
			# Handle the exception
			sent_message = bot.reply_to(
					message, 'Please enter an integer for your bounty amount.')
			time.sleep(5)
			try:
				bot.delete_message(sent_message.chat.id, sent_message.message_id)
				bot.delete_message(message.chat.id, message.message_id)
			except:
				pass
	else:
		# In case no parameters
		sent_message = bot.reply_to(message, 'Try /bounty [amount] [description]')
		time.sleep(5)
		try:
			bot.delete_message(sent_message.chat.id, sent_message.message_id)
			bot.delete_message(message.chat.id, message.message_id)
		except:
			pass

# Weekly income, calculated since last awarded income
# On every new post, check if has passed more than 7 days since last awarded income
week_award = 10
last_media_group = None
last_user_id = None
@bot.message_handler(content_types=['photo', 'video', 'document'], func=check_allowed_chatid)
def check_weekly_income(message):
	global last_media_group
	global last_user_id

	# Ignore post from same mediagroup or multiple posts from same user id
	if (last_media_group == None or last_media_group != message.media_group_id
			and last_user_id != message.from_user.id):
		last_media_group = message.media_group_id
		last_user_id = message.from_user.id
		users = db.user
		user = users.find_one({"id": message.from_user.id})
		# Check if user already exist in db, if not add it
		if (user != None):
			# If exist check time since last awarded income
			days_since_last_reward = (datetime.utcnow() - datetime.strptime(
					user['last_reward'], '%Y-%m-%d %H:%M:%S')).days

			if (days_since_last_reward >= 7 and user['locked'] == False):
				sent_message = bot.reply_to(
						message,
						'Congrats! Your weekly reward is here, +10 blessed coins 😺.')
				users.update_one(
					{'id': user['id']},
					{ '$set' : {
							'balance':
							user['balance'] + 10,
							'last_reward':
							datetime.utcfromtimestamp(
									message.date).strftime('%Y-%m-%d %H:%M:%S')
					}})
				time.sleep(10)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
				except:
					pass
		else:
			# Check if they have a username before register
			if(message.from_user.username != None):
				# Add new user to db with first time reward
				users.insert_one({
						'id':
						message.from_user.id,
						'username':
						message.from_user.username,
						'last_reward':
						datetime.utcfromtimestamp(
								message.date).strftime('%Y-%m-%d %H:%M:%S'),
						'balance':
						week_award,
						'locked':
						False
				})
				sent_message = bot.reply_to(
						message,
						'Congrats on your first post! You have been awarded with +10 blessed coins 😺.'
				)
				time.sleep(10)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
				except:
					pass
			else:
				sent_message = bot.reply_to(
					message,
					'To register you need to set an @username first!'
				)
				time.sleep(10)
				try:
					bot.delete_message(sent_message.chat.id, sent_message.message_id)
				except:
					pass


bot.polling()
