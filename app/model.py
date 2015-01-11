#!flask/bin/python
from app import db

friends = db.Table('friends',
db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
   id = db.Column(db.Integer, primary_key = True)
   name = db.Column(db.String(50), index=True, unique= True)
   email = db.Column(db.String(50),index=True, unique= True)
   age = db.Column(db.Integer(30), index=True, unique= True)
   bestfriend_id = db.Column(db.Integer, db.ForeignKey('user.id'))

   is_bestfriend = db.relationship( 'User', remote_side=id, lazy='dynamic', post_update=True)

   is_friend = db.relationship('User', #defining the relationship, User is left side entity
        secondary = friends, #indecates association table
        primaryjoin = (friends.c.user_id == id), #condition linking the left side entity
        secondaryjoin = (friends.c.friend_id == id),#cond if link right.s ent. with assoc table
        backref = db.backref('friends', lazy = 'dynamic'),#how accessed from right
        lazy = 'dynamic'
    ) 
    

   
   def __init__(self, name, email, age ):
	   self.name = name
	   self.email = email
	   self.age = age
	      
   def is_authenticated(self):
	    return True

   def is_active(self):
	    return True

   def is_anonymous(self):
	     return False

   def get_id(self):
	     return unicode(self.id)

   def __repr__(self):
	     return '<User %r>' %(self.name)

   @staticmethod
   def make_unique_name(name):
        if User.query.filter_by(name=name).first() is None:
            return name
        version = 2
        while True:
            new_name = name + str(version)
            if User.query.filter_by(name=new_name).first() is None:
                break
            version += 1
        return new_name


   def are_friends(self, user): #is-following
         return self.is_friend.filter(friends.c.friend_id == user.id).count() > 0

   #funcitons for friend management
   def be_friend(self, user): #follow
         if not self.are_friends(user):
                self.is_friend.append(user)
                user.is_friend.append(self)
                return self
    #funcitons for unfriend management
   def unfriend(self, user):
         if self.are_friends(user):
                 self.is_friend.remove(user)
                 user.is_friend.remove(self)
         return self
    #funcitons for bestfriend management
   def are_bestfriends(self, user):
         return self.is_bestfriend == user
  
    #best friends management
   def be_bestfriend(self, user):
         if not self.are_bestfriends(user):
                  self.is_bestfriend = [user]
                  user.is_bestfriend = [self]
                  return self
 