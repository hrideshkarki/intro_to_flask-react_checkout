from . import api
from ..models import Post
from ..apiauthhelper import token_auth
from flask import request


@api.get('/posts')
def getPostsAPI(): 
    posts = Post.query.all()
    return {
        'status':'ok',
        'results': len(posts),
        'posts': [p.to_dict() for p in posts]
    }

@api.get('/posts/<int:post_id>')
def getPostAPI( post_id):
    post = Post.query.get(post_id)
    if post:
        return {
            'status':'ok',
            'results': 1,
            'post': post.to_dict()
        }
    else:
        return {
            'status': 'not ok',
            'message': 'The post you are looking for does not exist'
        }, 404

@api.post('/posts/create')
@token_auth.login_required
def createPostAPI():
    data = request.json
    
    title = data['title']
    img_url = data['img_url']
    caption = data['caption']

    post = Post(title, img_url, caption, token_auth.current_user().id)

    post.saveToDB()

            
    return {
        'status': 'ok',
        'message': 'Succesfully created a post.',
        'post': post.to_dict()
    }, 201

@api.post('/posts/update/<int:post_id>')
@token_auth.login_required
def updatePostAPI(post_id):
    post = Post.query.get(post_id)
    if post:
        if post.user_id == token_auth.current_user().id:
            data = request.json
    
            title = data['title']
            img_url = data['img_url']
            caption = data['caption']
                
                    
                    
            post.title = title
            post.img_url = img_url
            post.caption = caption

            post.saveChangesToDB()
            return {
                'status': 'ok',
                'message': 'Succesfully updated your post!',
                'post': post.to_dict()
            }
                   
            
        else:
            return {
                'status': 'not ok',
                'message': "You cannot update another user's post."
            }

    else:
        return {
                'status': 'not ok',
                'message': 'The post you are trying to update does not exist'
            }
    
@api.delete('/posts/delete/<int:post_id>')
@token_auth.login_required
def deletePostAPI(post_id):
    post = Post.query.get(post_id)
    if post:
        if post.user_id == token_auth.current_user().id:
            post.deleteFromDB()
            return {
                'status': 'ok',
                'message': 'Successfully deleted the post.'
            }
        else:
            return {
                'status': 'not ok',
                'message': 'You cannot delete another Users post.'
            }, 400
    else:
        return {
                'status': 'not ok',
                'message': 'The posts you are trying to delete does not exist.'
            }, 404

