"""User model tests."""

import os
from re import U
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Likes, Follows

# set an environmental variable to use a different database for tests -
# we need to do this before we import our app, since that will have already connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# import the app
from app import app


# Create our tables (we do this here, so we only create the tables once for all tests --- in each test, we'll delete the data and create fresh new clean test data
db.drop_all()
db.create_all()



# Data to create test users
USER_1_DATA = dict(
    email="test1@test.com",
    username="testuser1",
    password="HASHED_PASSWORD"
)

USER_2_DATA = dict(
    email="test2@test.com",
    username="testuser2",
    password="HASHED_PASSWORD"
)

MSG_1 = {"text":"This is a test message for testuser1"}

MSG_2 = {"text":"This is a test message for testuser2"}


class MessageModelTestCase(TestCase):
    def setUp(self):
        """Clear errors, clear tables, add data, create test client"""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()


    def test_message_model(self):
        """Does the basic model work to add a message"""

        u = User(**USER_1_DATA)

        db.session.add(u)
        db.session.commit()

        msg = Message(text="This is a test message for testuser1")
        u.messages.append(msg)
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(u.messages), 1)

        # Message should have a user id that matches the user that posted it
        self.assertEqual(msg.user_id, u.id)

        # Message should have a timestamp
        self.assertTrue(msg.timestamp)

        # Message __repr__ should follow set format
        self.assertEqual(repr(msg), f"<Message #{msg.id}: user: {msg.user.username}, {msg.timestamp}>")


    def test_like_message(self):
        """Test if a user can like a message"""

        u1 = User(**USER_1_DATA)
        u2 = User(**USER_2_DATA)

        db.session.add_all([u1, u2])
        db.session.commit()

        msg = Message(text="This is a test message for testuser1")
        u1.messages.append(msg)

        u2.likes = [msg]

        db.session.add(msg)
        db.session.commit()

        # User1 should have no likes and 1 message
        # User 2 should have 1 like by User 1 and no mesages 
        self.assertEqual(len(u1.messages), 1)
        self.assertEqual(len(u2.messages), 0)

        self.assertEqual(len(u2.likes), 1)
        self.assertEqual(len(u1.likes), 0)
        self.assertIn(msg, u2.likes)


    def test_delete_message(self):
        """Test message can be deleted"""

        u = User(**USER_1_DATA)
        db.session.add(u)
        db.session.commit()

        msg = Message(text="This is a test message for testuser1")
        u.messages.append(msg)
        db.session.commit()

        db.session.delete(msg)
        db.session.commit()

        # User should have 0 messages and deleted message should not be in user's messages
        self.assertEqual(len(u.messages), 0)
        self.assertNotIn(msg, u.messages)

