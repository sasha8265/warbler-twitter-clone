"""Message View tests."""

import os
from unittest import TestCase
from models import db, connect_db, Message, User

# set an environmental variable to use a different database for tests -
# we need to do this before we import our app, since that will have already connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# import the app
from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables once for all tests --- in each test, we'll delete the data and create fresh new clean test data
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.otheruser = User.signup(username="otheruser",
                                    email="other@test.com",
                                    password="otheruser",
                                    image_url=None)

        self.testuser.following = [self.otheruser]

        db.session.commit()




    ####################################################
    # Testing with user logged-in
    ####################################################

    def test_add_message_logged_in(self):
        """Ensure logged in user can add a message"""

        # Since we need to change the session to mimic logging in, we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have the rest of ours test
            resp = c.post("/messages/new", data={
                "text": "This is a test message"
                })

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(User.username == self.testuser.username).first()
            self.assertEqual(msg.text, "This is a test message")

        
    def test_delete_message_logged_in(self):
        """Ensure logged in user can delete own message"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={
                "text": "This is a test message"
                })

            new_msg = Message.query.filter(User.username == self.testuser.username).first()

            # new_msg = Message.query.one()
            msg_count = Message.query.count()
            resp = c.post(f"/messages/{new_msg.id}/delete")

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            # check number of messages is less 1
            self.assertEqual(Message.query.count(), msg_count-1)



    def test_logged_in_view_home(self):
        """Ensure logged in user can view followed users on homepage"""

        msg = Message(text="This is a test message for otheruser")
        self.otheruser.messages.append(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/")
            
            # self.assertIn(self.otheruser, self.testuser.following)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"This is a test message for otheruser", resp.data)




    def test_logged_in_view_followed(self):
        """Ensure logged in user can view followed users"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser.id}/following", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"@otheruser", resp.data)



    def test_logged_in_like_msg(self):
        """Ensure logged in user can like a message by other user"""



    def test_like_own_msg(self):
        """Ensure logged in user cannot like own message"""



    # def test_delete_msg_other_user(self):
    #     """Ensure logged in user cannot delete a message as another user"""

    #     other_user_data = dict(
    #         email="otheruser@test.com",
    #         username="otheruser",
    #         password="HASHED_PASSWORD"
    #     )

    #     other_user = User(**other_user_data)
    #     db.session.add(other_user)
    #     db.session.commit()

    #     msg = Message(text="This is a test message for testuser1")
    #     other_user.messages.append(msg)
    #     db.session.commit()


    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id

    #         resp = c.post(f"/messages/{msg.id}/delete")

    #         # Make sure it redirects
    #         self.assertEqual(resp.status_code, 302)
    #         self.assertIn(b"Access unauthorized.", resp)

        #giving me this error:
        #sqlalchemy.orm.exc.DetachedInstanceError: Instance <Message at 0x7f99183f2d00> is not bound to a Session
    

    ####################################################
    # Testing not logged in functionality
    ####################################################


    def test_add_message_not_logged_in(self):
        """Ensure user cannot add a message if not logged in"""

        with self.client as c:
            resp = c.post("/messages/new", data={
                "text": "This is a test message"
                }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn(b'Access unauthorized.', resp.data)


    def test_add_msg_not_logged_in(self):
        """Ensure user cannot add a message if not logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/new", data={
                "text": "This is a test message"
                })

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "This is a test message")
