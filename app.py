from flask import Flask, redirect, render_template, session, request, flash
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


class Owner(db.Model):
    __tablename__ = 'owners'
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    all_properties = db.relationship('Property', back_populates = 'owners_property', cascade = 'all, delete, delete-orphan')
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
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id',ondelete='cascade'), nullable=False)
    owners_property = db.relationship('Owner', foreign_keys = [owner_id])
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
    this_owner = Owner.query.get(request.form['email'])  # check if email exists
    if this_owner:   
        if bcrypt.check_password_hash(this_owner['password'], request.form['password']):
            session['id'] = this_owner['id']
            session['first_name'] = this_owner['first_name']
            print(session['first_name'])
            return redirect('/offerpage')
    else:
        flash('Please register!')
    return redirect('/')

@app.route('/register')
def register():
    new_owner = Owner(first_name = request.form['first_name'], last_name=request.form['last_name'], email=request.form['email'], password=request.form['password'])
    db.session.add(new_owner)
    db.session.commit()
    flash('Thank you for registering, please log in!')
    return redirect('/')

@app.route('/offerpage')
def offer_page():
    if 'id' not in session:
        flash('Please Login!')
        return redirect('/')

# @app.route('/updatepassword')

# @app.route('/addbook', methods=['POST'])
# def addbook():
#     new_book = Books(title = request.form['title'], description=request.form['description'])
#     db.session.add(new_book)
#     db.session.commit()
#     return redirect('/')


# @app.route('/books/<books_id>')
# def book_id(books_id):
#     this_book = Books.query.get(int(books_id))
#     potential_authors = Authors.query.all()
#     return render_template('bookid.html',this_book = this_book,possible_authors = potential_authors)

# @app.route('/authors')
# def authors_page():
#     all_authors = Authors.query.all()
#     return render_template('authors.html',Authors = all_authors)

# @app.route('/addauthor', methods=['POST'])
# def addauthor():
#     new_author = Authors(first_name = request.form['first_name'], last_name = request.form['last_name'],notes = request.form['notes'])
#     db.session.add(new_author)
#     db.session.commit()
#     return redirect('/authors')

# @app.route('/authors/<authors_id>')
# def author_id(authors_id):
#     this_author = Authors.query.get(int(authors_id))
#     return render_template('authorid.html',this_author = this_author)

# @app.route('/authors_books', methods=['POST'])
# def authors_books():
#     this_book = Books.query.get(request.form['book_id'])
#     this_author = Authors.query.get(request.form['author_id']) 
#     this_author.books_this_author_wrote.append(this_book)
#     db.session.commit()
#     return redirect('/')

if __name__=="__main__":
    app.run(debug=True)