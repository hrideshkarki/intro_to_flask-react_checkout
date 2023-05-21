import os
basedir = os.path.abspath(os.path.dirname(__file__))
from config import Config

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')




import unittest
from app import create_app, db
from app.models import User, Post
from werkzeug.security import check_password_hash
import json

# When testing out API routes, typically looking for 3 things:
    # 1. Status Code
    # 2. Content Type
    # 3. Actual Data

class UserModelCaseTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(self)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.app = None
        self.app_context = None

    def test_1_index_response(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

    def test_2_password_hashing(self):
        user = User(username='sho', email='sho@sho.com', password='1234')
        self.assertNotEqual(user.password, '1234')
        self.assertTrue(check_password_hash(user.password, '1234'))

    def test_3_test_follow(self):
        u1 = User(username='sho', email='sho@sho.com', password='1234')
        u2 = User(username='sarah', email='sar@sar.com', password='1234')
        u3 = User(username='rachel', email='rach@w.com', password='1234')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertEqual(u1.followed.all(), [])
        self.assertEqual(u2.followed.all(), [])
        self.assertEqual(u1.followers.all(), [])
        self.assertEqual(u2.followers.all(), [])

        u1.follow(u2)
        self.assertTrue(u1 in u2.followers.all())
        self.assertEqual(len(u2.followers.all()), 1)
        self.assertEqual(u1.followed.first().username, 'sarah')
        self.assertEqual(u2.followers.count(), 1)
        self.assertEqual(u2.followers.first().username, 'sho')

        u1.unfollow(u2)
        self.assertTrue(u1 not in u2.followers.all())
        self.assertEqual(len(u2.followers.all()), 0)
        self.assertEqual(u2.followers.count(), 0)
        self.assertEqual(u1.followed.count(), 0)

    def test_4_get_all_posts(self):
        user = User(username='sho', email='sho@sho.com', password='1234')
        db.session.add(user)
        db.session.commit()
        p1 = Post(title='title_1', img_url='img_1', caption='caption_1', user_id=user.id)
        p2 = Post(title='title_2', img_url='img_2', caption='caption_2', user_id=user.id)
        p3 = Post(title='title_3', img_url='img_3', caption='caption_3', user_id=user.id)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.commit()

        response = self.client.get('/api/posts')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'ok')
        self.assertEqual(response.json['results'], 3)
        self.assertEqual(response.json['posts'][0]['author'], 'sho')
        
    def test_5_create_post_fail_authentication(self):
        response = self.client.post('/api/posts/create')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'not ok')
        self.assertEqual(response.json['message'], 'Please include the header Authorization with Token Auth using a Bearer Token')

    def test_6_create_post_fail_not_enough_info(self):
        user = User(username='sho', email='sho@sho.com', password='1234')
        db.session.add(user)
        db.session.commit()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {user.apitoken}'
        }

        response = self.client.post('/api/posts/create', data={}, headers = headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'not ok')
        self.assertEqual(response.json['message'], 'Not enough info provided to create a post.')

    def test_7_create_post_success(self):
        user = User(username='sho', email='sho@sho.com', password='1234')
        db.session.add(user)
        db.session.commit()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {user.apitoken}'
        }
        data = {
            'title': 'My Title',
            'img_url': 'placeholder.com/150',
            'caption': 'blah blah blah'
        }

        response = self.client.post('/api/posts/create', data=json.dumps(data), headers = headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'ok')
        self.assertEqual(response.json['message'], 'Successfully created a post.')
        self.assertEqual(response.json['post']['author'], 'sho')

    def test_7_delete_post_success(self):
        user = User(username='sho', email='sho@sho.com', password='1234')
        db.session.add(user)
        db.session.commit()
        post = Post(title='My Title', img_url='placeholder.com/150', caption='blah blah blah', user_id=user.id)
        db.session.add(post)
        db.session.commit()
        headers = {
            'Authorization': f'Bearer {user.apitoken}'
        }
        response = self.client.delete(f'/api/posts/delete/{post.id}',  headers = headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'application/json')
        self.assertEqual(response.json['status'], 'ok')
        self.assertEqual(response.json['message'], 'Successfully deleted the post.')



if __name__ == '__main__':
    unittest.main(verbosity=2)