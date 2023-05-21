from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from secrets import token_hex

db = SQLAlchemy()

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id'), nullable=False),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'), nullable=False)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), nullable = False, unique = True)
    email = db.Column(db.String(100), nullable = False, unique = True)
    password = db.Column(db.String, nullable = False)
    date_created = db.Column(db.DateTime, nullable = False, default=datetime.utcnow())
    post = db.relationship('Post', backref = 'author', lazy = True)
    cart = db.relationship('Product', secondary='cart', backref = 'shoppers', lazy = True)
    liked_posts = db.relationship('Post', secondary='like', lazy = True)
    followed = db.relationship(
        'User',
        secondary=followers,
        lazy = 'dynamic',
        backref=db.backref('followers', lazy = 'dynamic'),
        primaryjoin = (followers.c.follower_id == id),
        secondaryjoin = (followers.c.followed_id == id)
        )
    apitoken = db.Column(db.String, unique=True)
    


    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.apitoken = token_hex(16)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'apitoken': self.apitoken
        }

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
        
    def follow(self, user):
        self.followed.append(user)
        db.session.commit()
    def unfollow(self, user):
        self.followed.remove(user)
        db.session.commit()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable = False)
    img_url = db.Column(db.String, nullable = False)
    caption = db.Column(db.String(500))
    date_created = db.Column(db.DateTime, nullable = False, default=datetime.utcnow())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    likers = db.relationship('User', secondary='like')
    likers_2 = db.relationship('User', secondary = 'like_2')

    def __init__(self, title, img_url, caption, user_id):
        self.title = title
        self.img_url = img_url
        self.caption = caption
        self.user_id = user_id

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()

    def saveChangesToDB(self):
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'caption': self.caption,
            'img_url': self.img_url,
            'author': self.author.username,
            'likes': len(self.likers),
            'date_created': self.date_created,
        }

likes = db.Table('like_2',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), nullable = False),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), nullable = False))

class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable = False)

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id
    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()
# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
#     post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable = False)
#     message = db.Column(db.String(300), nullable = False)






# Like.query.all() # we would never start from the Like Model class so having it inherit from db.Model is a bit unnecessary
# Comment.query.get()

# user = User.query.get(1) # returns to us the "Sho" user
# user.like.all() # returns to us all the things that User 1 has liked

# post = Post.query.get(1) # return to us a post object with ID 1
# post.likers.all() # return to us all the people that liked post 1


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable = False)
    img_url = db.Column(db.String, nullable = False)
    description = db.Column(db.String(500))
    price = db.Column(db.Numeric(10,2))

    def __init__(self, product_name, img_url, description, price):
        self.product_name = product_name
        self.img_url = img_url
        self.description = description
        self.price = price

    def saveToDB(self):
        db.session.add(self)
        db.session.commit()

    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()

    def saveChangesToDB(self):
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product_name,
            'description': self.description,
            'img_url': self.img_url,
            'price': self.price,
        }
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable = False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable = False)

    def __init__(self, user_id, product_id):
        self.user_id = user_id
        self.product_id = product_id
    def saveToDB(self):
        db.session.add(self)
        db.session.commit()
    def deleteFromDB(self):
        db.session.delete(self)
        db.session.commit()