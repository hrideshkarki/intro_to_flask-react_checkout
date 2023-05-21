from flask import Blueprint, request
from ..models import Post, Likes, User
from ..apiauthhelper import basic_auth_required, token_auth_required, basic_auth, token_auth
from flask_cors import cross_origin
api = Blueprint('api', __name__)


@api.route('/api/posts')
def getPosts():
    posts = Post.query.order_by(Post.date_created.desc()).all()

    new_posts = []
    for p in posts:
        new_posts.append(p.to_dict())
    
    return {
        'status': 'ok',
        'totalResults': len(posts),
        'posts': [p.to_dict() for p in posts]
    }

@api.route('/api/posts/<int:post_id>')
def getPost(post_id):
    post = Post.query.get(post_id)
    if post:
        return {
            'status': 'ok',
            'totalResults': 1,
            'post': post.to_dict()
        }
    else:
        return {
            'status': 'not ok',
            'message': 'The post you are looking for does not exist.'
        }

@api.route('/api/like/<int:post_id>', methods=["GET"])
def likePost(user, post_id):
    like_instance = Likes(user.id, post_id)
    like_instance.saveToDB()    
    return {
        'status': 'ok',
        'msg': 'succefully liked post'
    }


@api.route('/api/posts/create', methods = ["POST"])
@token_auth_required
def createPost(user):
    data = request.json

    title = data['title']
    caption = data['caption']
    img_url = data['img_url']

    ## for now, accept the user_id parameter from the JSON body
    ### HOWEVER, this is not the correct way, we need to authenticate them somehow
    #### we will cover this in BASIC/TOKEN auth

    post = Post(title, img_url, caption, user.id)
    post.saveToDB()
    
    return {
        'status': 'ok',
        'message': 'Succesfullly created post!'
    }

@api.route('/api/posts/<int:post_id>/delete', methods=["GET"])
@token_auth_required
def deletePostAPI(user, post_id):
    print('passed token auth')
    post = Post.query.get(post_id)
    # user = token_auth.current_user()
    if user.id != post.author.id:
        return {
            'status': 'not ok',
            'message': 'You cannot delete another users posts'
        }
    print(post)
    post.deleteFromDB()
    return {
        'status': 'ok',
        'message': 'Succesfully deleted post!'
    }

@api.route('/api/posts/update/<post_id>', methods = ["POST"])
@token_auth_required
def updatePost(user, post_id):
    data = request.json

    title = data['title']
    caption = data['caption']
    img_url = data['img_url']

    ## for now, accept the user_id parameter from the JSON body
    ### HOWEVER, this is not the correct way, we need to authenticate them somehow
    #### we will cover this in BASIC/TOKEN auth

    post = Post.query.get(post_id)
    if user.id != post.author.id:
        return {
            'status': 'not ok',
            'message': 'You cannot update another users Post'
        }

    post.title = title
    post.caption = caption
    post.img_url = img_url
   
    post.saveChanges()
    
    return {
        'status': 'ok',
        'message': 'Succesfullly updated post!'
    }


################# AUTH ROUTES API  #############
@api.route('/api/signup', methods=["POST"])
def signUpPageAPI():
    data = request.json
   
       
    username = data['username']
    email = data['email']
    password = data['password']
    


    # add user to database
    user = User(username, email, password)

    user.saveToDB()

    return {
        'status': 'ok',
        'message': "Succesffuly created an account!"
    }

@api.route('/api/login', methods=["POST"])
@basic_auth.login_required
def getToken():
    user = basic_auth.current_user()
    return {
        'status': 'ok',
        'user': user.to_dict(),
    }
    
