import pyrebase

class Firebase:
	def __init__(self):
		super(Firebase, self).__init__()
		"""self.config = {
			"apiKey": "AIzaSyDvpw5qmZ-7ZXYQSEYuUCUp0TvI7CI0X9Q",
			"authDomain": "peakfinder-bbc2c.firebaseapp.com",
			"databaseURL": "https://peakfinder-bbc2c.firebaseio.com",
			"storageBucket": "peakfinder-bbc2c.appspot.com"
		}"""
		self.config = {
			"apiKey": "AIzaSyAqYqvCtbapAHNbRwns2g-apzkmgcw6rzg",
			"authDomain": "peakfinder-41efe.firebaseapp.com",
			"databaseURL": "https://peakfinder-41efe.firebaseio.com",
			"storageBucket": "peakfinder-41efe.appspot.com",
  		}
		self.firebase = pyrebase.initialize_app(self.config)

	def Auth(self):
		return self.firebase.auth()
		
	def RealTimeDB(self):
		return self.firebase.database()

	def Storage(self):
		return self.firebase.storage()