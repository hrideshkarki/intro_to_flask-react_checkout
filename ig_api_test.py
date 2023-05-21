import unittest
import requests as r
from app.models import Post, User
from app import create_app, db
from test_config import Config

class FlaskTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()



    def test_get_single_post_api(self):
        
        res = r.get(self.base_url + '/posts/1')
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['results'], 1)


    def test_user(self):
        u = User('test_person', 'test_person@gmail.com', '1234')
        self.assertNotEqual(u.password, '1234')
        u.saveToDB()

    def test_follow_person(self):
        u1 = User('John', 'john@john.com', '1234')
        u2 = User('Jane', 'jane@jane.com', '1234')
        u3 = User('Sam', 'sam@sam.com', '1234')
        u4 = User('Smith', 'smith@smith.com', '1234')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add_all([u3,u4])
        
        u1.follow(u2)
        u3.follow(u2)
        u4.follow(u2)

        self.assertEqual(len(u2.followers.all()), 3)



if __name__ == '__main__':
    unittest.main(verbosity=2)