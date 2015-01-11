#!flask/bin/python
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from config import MONKEYS_PAGE
from .form import LoginForm
from .model import User
from sqlalchemy import func


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/user/<int:page>', methods = ['GET', 'POST'])
def user(page=1, sort='normal'):
    user = g.user
    #condition to sort base on ascending
    if request.args.get('sort') =='asc':
            sortBy = 'asc'
            monkey = User.query.order_by(User.name.asc()).paginate(page, MONKEYS_PAGE, False)

    elif request.args.get('sort')== 'friendnum':
    	     sortBy =  'friendnum'
    	     #friends are users as well, so need alias
    	     friend = db.aliased(User)
    	     #construct subquery for use in final query
    	     sub = db.session.query(
    	      	     User.id, db.func.count(friend.id).label('fn')).\
    	             join(friend, User.friends).group_by(User.id).subquery()

    	     monkey = User.query.join(sub, sub.c.id == User.id).\
                       order_by(sub.c.fn.desc()).paginate(page, MONKEYS_PAGE, False)

     #condition to sort base on bestfriend name                  
    elif request.args.get('sort') == 'bf':
           sortBy = 'bf'
           friend = db.aliased(User)
           sub = db.session.query(
                   User.name, friend.name.label('fn')).\
                   join(friend, User.is_bestfriend).group_by(User.name).subquery()

           monkey = User.query.join(sub, sub.c.name == User.name).\
                        order_by(sub.c.fn.asc()).paginate(page, MONKEYS_PAGE, False)
    #condition to sort base on normal  
    else:
    	     sortBy = 'normal'
    	     monkey = User.query.paginate(page, MONKEYS_PAGE, False)
        
    return render_template('Users.html',
    	    user = user,
            title ='Home',
            monkey = monkey,
            sortBy = sortBy
            )

@app.route('/login', methods = ['GET', 'POST'])
def login():
       form = LoginForm()
       #checks if the user is authernticated
       #or not, if yes it skips authentfic.
       if current_user is not None and current_user.is_authenticated():
              return redirect(url_for('user'))
    #does not allow user to use get method
       if request.method == 'GET':
              return render_template('login.html',
                       form = form,
                       title = 'Login')

    #taking the user submitted data and checking if it exists in the database
       user_in_db = User.query.filter_by(name=form.name.data.lower()).first()

    #if the username is not wrong
       if user_in_db is not None and user_in_db != False:
               if form.email.data !=  user_in_db.email:
                       flash('Email is incorrect')
                       return redirect(url_for('login'))
               login_user(user_in_db)
               return redirect(url_for('user',page=1,sortby='normal'))
       else:
            flash('Username does not exists')
            return render_template('login.html',
                   form = form,
                   title = 'Login')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/new', methods=['GET', 'POST'])
def new():
  form = LoginForm(request.form)
  if request.method == 'POST':
     if form.validate()== True:
      contact = User(form.name.data,
                 form.email.data,
                 form.age.data
                          )
      db.session.add(contact)
      db.session.commit()
      return redirect(url_for('user',page=1,sortby='normal'))
      
     else: #If the form does not have all fields that are required 
            flash('All fields are required.')
  return render_template('new.html', form=form)
     

#Edit monkey information
@app.route('/edit/<int:id>', methods=['POST'])
def edit(id=None):
  user = User.query.get_or_404(id)
  form = LoginForm(obj=user)
  if request.method=='POST':
      if form.validate_on_submit()== True:
         form.populate_obj(user)
         db.session.commit()
         flash('changes done.')
         return redirect(url_for('user',page=1,sortby='normal'))

      else: #If the form does not have all fields that are required 
            return render_template('edit.html', form=form, id=id )

# delete the monkey 
@app.route('/delete/<int:id>')
@login_required
def delete(id):
  user = User.query.get_or_404(id)
  if g.user.id == user.id:
  	       flash('You are not allow to delete yourself.')
  	       
  else:
      db.session.delete(user)
      db.session.commit()
      flash('delete done.')
  return redirect(url_for('user',id=id, page=1,sortby='normal'))

# show profileof each monkey
@app.route('/profile/<int:id>')
def profile(id):
  user= User.query.get(id)
  return render_template('profile.html', id=id, user= user)


# freinds
@app.route('/friend/<name>')
@login_required
def friend(name):
    user = User.query.filter_by(name = name).first()
    if user is None:
        flash('User %s not found.' % name)
        return redirect(url_for('user'))
    if user == g.user:
        flash('You can\'t Friend yourself!')
        return redirect(url_for('user',page=1,sortby='normal'))
    u = g.user.be_friend(user)
    if u is None:
        flash('You have been Friend with ' + name + '.')
        return redirect(url_for('user',page=1,sortby='normal'))

    db.session.add(u)
    db.session.commit()
    flash('You are now Friend with ' + name + '!')
    return redirect(url_for('user', page=1,sortby='normal'))

#unfriend
@app.route('/unfriend/<name>')
@login_required
def unfriend(name):
    user = User.query.filter_by(name = name).first()
    if user is None:
        flash('User %s not found.' % name)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unFriend yourself!')
        return redirect(url_for('user', page=1,sortby='normal'))
    u = g.user.unfriend(user)
    if u is None:
        flash('Cannot unFriend ' + name + '.')
        return redirect(url_for('user', page=1,sortby='normal'))
    
    db.session.add(u)
    db.session.commit()
    flash('You are not Friend with ' + name + '!')
    return redirect(url_for('user', page=1,sortby='normal'))

#best_freinds
@app.route('/bestFriend/<name>')
@login_required
def bestFriend(name):
    user = User.query.filter_by(name = name).first()
    if user is None:
        flash('User %s not found.' % name)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t Best Friend yourself!')
        return redirect(url_for('user', page=1,sortby='normal'))
    u = g.user.be_bestfriend(user)
    if u is None:
        flash('Cannot be best Friend ' + name + '.')
        return redirect(url_for('user', page=1,sortby='normal'))
    db.session.add(u)
    db.session.commit()
    flash('You are now BestFriend with ' + name + '!')
    return redirect(url_for('user', page=1,sortby='normal'))

            

      
      
      
      


