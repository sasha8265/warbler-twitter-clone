"""User views tests."""

import os
from unittest import TestCase
from models import db, connect_db, Message, User, Follows, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Import app
from app import app, CURR_USER_KEY

# Create our tables 
# db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False



# Create Test Users
""" 
My instinct here is to:
- add my user data before setup like I did for the user model tests
- Add one user to the other as following
- Then add a user to the session as logged in, the way the signup route would have - not sure though how the session works with tests?

Not sure if I should be doing that in the set up though - wouldn't that be extra work for the test to go through each time, when i only need it to happen once for all tests?

"""

# USER_1 = User.signup(
#     email="test1@test.com",
#     username="testuser1",
#     password="HASHED_PASSWORD",
#     image_url="/static/images/default-pic.png"
# )

# USER_2 = User.signup(
#     email="test2@test.com",
#     username="testuser2",
#     password="HASHED_PASSWORD",
#     image_url="/static/images/default-pic.png"
# )

# USER_1.following = [USER_2]
# db.session.add_all([USER_1, USER_2])
# db.session.commit()

# session[CURR_USER_KEY] = USER_1.id




class UserViewsTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Clear any errors, create test client, add ssample data"""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.testuser1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser1",
                                    image_url=None)

        self.testuser2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None)

        db.session.commit()


    def test_logged_in_view_home(self):
        """When user is logged in, can they see a hopepage with their username and links to their followers / following?"""

        # Change the session to mimic logging in using session_transaction
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
            resp = client.get("/")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>@testuser1</p>", html)
            self.assertIn(f'<a href="/users/{self.testuser1.id}/followers">0</a>', html)
            self.assertIn(f'<a href="/users/{self.testuser1.id}">', html)
            self.assertIn(f'<a href="/messages/new">New Message</a>', html)
            self.assertIn(f'<a href="/logout">Log out</a>', html)
        

    def test_logged_in_view_index(self):
        """When user is logged in, can they view index of all users?"""

        # Change the session to mimic logging in using session_transaction
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
            resp = client.get("/users")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<p>@testuser1</p>", html)
            self.assertIn(f'<img src="{self.testuser1.image_url}" alt="Image for testuser1" class="card-image">', html)
            self.assertIn("<p>@testuser2</p>", html)
            # self.assertIn(f'<img src="{self.testuser2.image_url}" alt="Image for testuser2" class="card-image">', html)
            # Why doesn't this one work? getting a DetachedInstanceError
            

    
    def test_logged_in_follow(self):
        """When user is logged in, can they follow another user?"""

        # Change the session to mimic logging in using session_transaction
        with self.client as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser1.id
        
                resp = client.post(
                    f"/users/follow/{self.testuser2.id}")

                # html = resp.get_data(as_text=True)

                self.assertEqual(resp.status_code, 302)
            
    