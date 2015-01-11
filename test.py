#!flask/bin/python
import os
import unittest
from config import basedir
from app import app, db
from app.model import User

class TestCase(unittest.TestCase):
	def setUp(self):
		app.config['TESTING'] = True
		app.config['WTF_CSRF_ENABLED'] = False
		app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
		self.app = app.test_client()
		db.create_all()
		

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_make_unique_name(self):
		u = User(name = 'angela',
			email = 'angela@example.com',
			age = '26'
			)
			
		db.session.add(u)
		db.session.commit()
		name = User.make_unique_name('angela')
		assert name != 'angela'
		u = User(name = name,
			email = 'janet@example.com',
			age = '22'
			)
		db.session.add(u)
		db.session.commit()
		name2 = User.make_unique_name('angela')
		assert name2 != 'angela'
		assert name2 != name
      
if __name__ == '__main__':
	unittest.main()