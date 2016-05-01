import os
import tornado.web
from helpers import consoleHelper
from helpers import requestHelper
from helpers import userHelper
from constants import exceptions
import glob

MODULE_NAME = "get_replay"
class handler(tornado.web.RequestHandler):
	"""
	Handler for osu-getreplay.php
	"""
	def get(self):
		try:
			# Check arguments
			if requestHelper.checkArguments(self.request.arguments, ["c", "u", "h"]) == False:
				raise exceptions.invalidArgumentsException(MODULE_NAME)

			# Get arguments
			username = self.get_argument("u")
			password = self.get_argument("h")
			replayID = self.get_argument("c")

			# Login check
			userID = userHelper.getID(username)
			if userID == 0:
				raise exceptions.loginFailedException(MODULE_NAME, userID)
			if userHelper.checkLogin(userID, password) == False:
				raise exceptions.loginFailedException(MODULE_NAME, username)

			# Get user ID
			replayData = glob.db.fetch("SELECT scores.*, users.id AS uid FROM scores LEFT JOIN users ON scores.username = users.username WHERE scores.id = ?", [replayID])

			# Increment 'replays watched by others' if needed
			if replayData != None:
				if username != replayData["username"]:
					userHelper.incrementReplaysWatched(replayData["uid"], replayData["play_mode"])

			# Serve replay
			consoleHelper.printGetReplayMessage("Serving replay_{}.osr".format(replayID))
			fileName = ".data/replays/replay_{}.osr".format(replayID)
			if os.path.isfile(fileName):
				with open(fileName, "rb") as f:
					fileContent = f.read()
				self.write(fileContent)
			else:
				self.write("")
		except exceptions.invalidArgumentsException:
			pass
		except exceptions.loginFailedException:
			pass