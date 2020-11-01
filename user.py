#import pymongo

class User(object):
	def __init__(self, document):
		try:
			self.username = document["username"]
			self.password = document["password"]
			self.email = document["email"]
			self.phone = document["phone"]
			self.firstName = document["firstName"]
			self.lastName = document["lastName"]
			self.isAdmin = False
			print(self.username, self.password)
		except:
			pass
		#return self.user

	"""
	def createNewUser(self):
		user = {
			"email": "",
			"username": "",
			"password":, "",
			"firstName": "",
			"lastName": "",
			"phone": "",
			"isAdmin": False,
		}
		try:
			newUser = users.insert_one(user)
			return {"success": True}
		except Exception as e:
			print(e)
			if 'duplicate key error' in e:
				return {"success": False, "error": "Username already exists."}
			else:
				return return {"success": False, "error": "Unknown error saving new user."}
	def checkUserExists(self):
		#exists = users.find_one({"username": "dannfy"})
		#if exists != None:
		#	return False
		#else:
		#	return True
		#
	def comparePasswords(self):
		#user = users.find_one({"username": "dannfy"})
		#if user != None:
		#	return False
		#else:
		#	return True
		#
		#
	def updateUser(self):
		###
		#
		#
	"""
"""
myclient = pymongo.MongoClient("mongodb+srv://daniel:Z47c6cI1SfOvWElZ@schoolserver.coq5b.mongodb.net/schoolServer?retryWrites=true&w=majority", ssl=True)
mydb = myclient["schoolServer"]
users = mydb['users']
i = users.find_one({"username": "dannfy"})
print(i)"""