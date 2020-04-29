from flask import Flask, redirect, render_template, session, request, flash
import re
import googlemaps
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate


app = Flask(__name__)
app.secret_key = 'keep it secret keep it safe'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///real_estate_proj.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
EMAIL_Check = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
pass_check = re.compile(r'^[a-zA-Z0-9.+_-]+$')
gmaps = googlemaps.Client(key='AIzaSyCflXWHpLx4rriSS-1KmHgabloxJYHRPqg')


# comments_table = db.Table('comments',
#               db.Column('comment_id', db.Integer, db.ForeignKey('comments.id', ondelete='cascade'), primary_key=True),
#               db.Column('user_id', db.Integer, db.ForeignKey('owners.id', ondelete='cascade'), primary_key=True), 
#               db.Column('property_id', db.Integer, db.ForeignKey('properties.id', ondelete='cascade'), primary_key=True))




class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    admin = db.Column(db.Boolean())
    password = db.Column(db.String(45))
    all_properties = db.relationship('Property', back_populates = 'owners_property', cascade = 'all, delete, delete-orphan')
    all_comments_by_this_owner = db.relationship('Comment', back_populates='owner_comments', cascade = 'all, delete, delete-orphan')
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Property(db.Model):
    __tablename__= 'properties'
    id = db.Column(db.Integer, primary_key = True)
    address = db.Column(db.String(45))
    city = db.Column(db.String(45))
    zip_code = db.Column(db.Integer)
    units = db.Column(db.Integer)
    income = db.Column(db.Integer)
    offer = db.Column(db.Integer)
    expenses = db.Column(db.Integer)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id',ondelete='cascade'), nullable=False)
    owners_property = db.relationship('Owner', foreign_keys = [owner_id])
    all_comments_for_this_property = db.relationship('Comment', back_populates='property_comments', cascade = 'all, delete, delete-orphan')
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())


class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    comments = db.Column(db.String(255))
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id',ondelete='cascade'), nullable=False)
    # fix naming for property_comments
    property_comments = db.relationship('Property', foreign_keys = [property_id])
    owner_id =  db.Column(db.Integer, db.ForeignKey('owners.id',ondelete='cascade'), nullable=False)
    owner_comments = db.relationship('Owner', foreign_keys = [owner_id])
    created_at = db.Column(db.DateTime, server_default = func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

@app.route('/')
def login():
    return render_template('signin.html')

@app.route('/signIncheck', methods = ['POST'])
def signIncheck():
    if len(request.form['email'])<5:
        flash('Please enter a valid email')
    if len(request.form['password'])<5:
        flash('Please enter a valid password')

    this_owner = Owner.query.filter_by(email = request.form['email']).first() 
    print(this_owner.id)
    print(this_owner)
    print(this_owner.password)
    print(type(this_owner.admin))
    if this_owner.admin == True:
        if bcrypt.check_password_hash(this_owner.password, request.form['password']):
            session['id]'] = this_owner.id
            session['first_name'] = this_owner.first_name
            return redirect ('/adminpage')
    if not this_owner.admin:
        if bcrypt.check_password_hash(this_owner.password, request.form['password']):
            session['id'] = this_owner.id
            session['first_name'] = this_owner.first_name
            print(session['first_name'])
            return redirect('/offerpage')
    else:
        flash('Please register!')
    return redirect('/')

@app.route('/adminpage')
def adminpage():

    all_offers = Property.query.order_by(Property.address).all()

    return render_template('adminpage.html',all_offers=all_offers)

@app.route('/addowner')
def add_owner():
    return render_template('registration.html')

@app.route('/register', methods = ['POST'])
def register():
    valid = True
    if len(request.form['first_name']) <2:
        valid = False
        flash('Please enter a first name')
    if len(request.form['last_name']) <2:
        valid = False
        flash('Please enter a last name')
    if len(request.form['email']) <5:
        valid = False
        flash('Please enter a first name')
    elif not EMAIL_Check.match(request.form['email']):
        valid = False
        flash('Please enter a valid email')
        
    if len(request.form['password']) < 5:
        valid= False
        flash('Please enter a password with atleast 8 characters')
        
    elif not pass_check.match(request.form['password']):
        valid =False 
        flash ('Please enter a password with correct characters')
       
    if request.form['cpassword'] != request.form['password']:
        valid=False
        flash('Please match passwords')

    User_check = Owner.query.filter_by(email = request.form['email']).first() 
    if User_check: 
        valid = False
        flash('Email already exists please use a different email')

    if request.form['email'] == 'tymac@macreiproperties.com':
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        new_admin = Owner(first_name = request.form['first_name'], last_name=request.form['last_name'], email=request.form['email'], password=pw_hash, admin = True)
        db.session.add(new_admin)
        db.session.commit()
        flash('Thank you for registering, please log in!')
        return redirect('/')
        
    if valid ==True:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        new_owner = Owner(first_name = request.form['first_name'], last_name=request.form['last_name'], email=request.form['email'], password=pw_hash, admin = False)
        db.session.add(new_owner)
        db.session.commit()
        flash('Thank you for registering, please log in!')
        return redirect('/')
    return redirect('/addowner')

@app.route('/updatepassword')
def update_pass():
    return render_template('update_pass.html')

@app.route('/updatecheck', methods = ['POST'])
def update_pass_db():
    valid = True
    if not EMAIL_Check.match(request.form['email']):
        valid = False
        flash('Please enter a valid email')

    User_check = Owner.query.filter_by(email = request.form['email']).first()

    if not User_check: 
        valid = False
        flash('Email doesn"t exist please register')

    if len(request.form['password']) < 5:
        valid= False
        flash('Please enter a password with atleast 8 characters')
    
    elif not pass_check.match(request.form['password']):
        valid =False 
        flash ('Please enter a password with correct characters')
       
    if request.form['cpassword'] != request.form['password']:
        valid=False
        flash('Please match passwords')

    if request.form['email'] == 'tymac@macreiproperties.com':
        update_admin = Owner.query.filter_by(email = request.form['email']).first()
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        update_admin.password = pw_hash
        update_admin.admin = True
        db.session.commit()
        flash('Thanks for updating your admin password, please log in')
        return redirect('/')

    else:
        update_password = Owner.query.filter_by(email = request.form['email']).first()
        print(update_password)
        print(update_password.password)
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        update_password.password = pw_hash
        db.session.commit()
        flash('Thanks for updating your password, please log in!')
        return redirect('/')
    return redirect('/updatepassword')

    
@app.route('/offerpage')
def offer_page():
    if 'id' not in session:
        flash('Please Login!')
        return redirect('/')
    else:
        offers_for_user = Property.query.filter_by(owner_id=session['id']).all()
    return render_template('offerpage.html',offers = offers_for_user)
    
@app.route('/offercalc', methods = ['POST'])
def offercalc():
    valid = True
    if len(request.form['address'])<5:
        valid = False
        flash('Please enter a valid address')
    if len(request.form['city'])<2:
        valid = False
        flash('Please enter a city')
    if len(request.form['zip_code'])<5:
        valid = False
        flash('Please enter a zip code')
    if len(request.form['units'])<1:
        valid = False
        flash('Please enter no. of units')
    if len(request.form['income'])<3:
        valid = False
        flash('Please enter income')
    if len(request.form['expenses'])<3:
        valid = False
        flash('Please enter expenses')

    if valid == True:
        offer_price = int(request.form['income']) * 12
        print(offer_price)

        new_property = Property(address = str(request.form['address']), city = str(request.form['city']), zip_code = request.form['zip_code'], units = request.form['units'], income = request.form['income'], expenses = request.form['expenses'], offer = offer_price, owner_id = session['id'] ) 
        db.session.add(new_property)
        db.session.commit()
        return redirect('/offerpage')
    return redirect('/offerpage')


@app.route('/contact/<id>')
def contact(id):
    print('got here')
    this_property = Property.query.get(id)
    # state = 'CA'
    print(this_property.owner_id)
    # geocode_result = gmaps.geocode(this_property.address, this_property.city, state)
    this_property_comments = Comment.query.filter_by(property_id='id').all()
    return render_template("contact.html", this_property = this_property , comments = this_property_comments )

@app.route('/commentadd/<id>', methods=['POST'])
def commentsadd(id):
    # validation to make building owner or admin
    

    this_property = Property.query.get(id)
    
    admin_comment = Comment(comments = request.form['admin_comment'], property_id = 'id', admin = True )
    new_comment = Comment(comments = request.form['owner_comment'], property_id = 'id', owner_id = session['id'] )
    db.session.add(new_comment)
    db.session.commit()
    return redirect(f'/contact/{id}')
 
@app.route('/logout')
def logout():
    session.pop('id')
    return redirect('/')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__=="__main__":
    app.run(debug=True)