"""User model tests."""

import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app
from app import app


# Create our tables (we do this here, so we only create the tables once for all tests --- in each test, we'll delete the data and create fresh new clean test data
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



class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Clear any errors, clear tables, create test client"""

        db.session.rollback()
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()



    def test_user_model(self):
        """Does basic model work?"""

        u = User(**USER_1_DATA)

        db.session.add(u)
        db.session.commit()

        # User should have no messages, no followers, no followings, and no likes
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)

        # User should have the default header and profile image urls
        self.assertEqual(u.header_image_url, "/static/images/warbler-hero.jpg")
        self.assertEqual(u.image_url, "/static/images/default-pic.png")

        # User __repr__ should follow set format
        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")



    def test_is_following(self):
        """Does is_following and followed_by work between users?"""

        u1 = User(**USER_1_DATA)
        u2 = User(**USER_2_DATA)

        u1.following = [u2]

        db.session.add_all([u1, u2])
        db.session.commit()

        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(len(u1.following), 1)
        self.assertTrue(u1.is_following(u2))
        self.assertTrue(u2.is_followed_by(u1))
        self.assertIn(u2, u1.following) 
        self.assertIn(u1, u2.followers)

        self.assertNotIn(u1, u2.following)
        self.assertNotIn(u2, u1.followers)
        self.assertFalse(u2.is_following(u1))
        self.assertFalse(u1.is_followed_by(u2))


    
    def test_user_signup(self):
        """Does User.signup successfully create a new user given valid credentials"""

        u = User.signup(
            email="signup_test@test.com",
            username="signup_test_user",
            password="HASHED_PASSWORD",
            image_url="/static/images/default-pic.png"
            )

        db.session.commit()

        self.assertIsInstance(u, User)

        # User should be in database with no followers, no follows, no messages, and no likes
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        self.assertEqual(len(u.likes), 0)

        # User should have the default header and profile image urls
        self.assertEqual(u.header_image_url, "/static/images/warbler-hero.jpg")
        self.assertEqual(u.image_url, "/static/images/default-pic.png")

        # User __repr__ should follow set format
        self.assertEqual(repr(u), f"<User #{u.id}: {u.username}, {u.email}>")



    def test_duplicate_username_signup(self):
        """Does User.signup prevent a user from registering with a username that already exists"""

        u1 = User(**USER_1_DATA)
        db.session.add(u1)
        db.session.commit()

        with self.assertRaises(IntegrityError):
            duplicate_u = User.signup("testuser1", "duplicate@test.com", "HASHED_PASSWORD", "")
            db.session.commit()



    def test_signup_missing_fields(self):
            """Does User.signup prevent a user from registering without completing required fields?"""

            with self.assertRaises(TypeError):
                u = User.signup(
                    username="failed_user",
                    password="HASHED_PASSWORD", 
                    image_url="/static/images/default-pic.png"
                    )



    def test_user_login(self):
        """Does authenticate work with valid credentials?"""

        u = User.signup("test_auth", "test_auth@test.com", "test_password", "")
        db.session.commit()

        login_user = User.authenticate("test_auth", "test_password")

        self.assertEqual(login_user.username, "test_auth")
        self.assertEqual(login_user.email, "test_auth@test.com")




    def test_user_login_fail(self):
        """Does User.login prevent logging in with incorrect password?"""

        u = User.signup("test_auth", "test_auth@test.com", "test_password", "")
        db.session.commit()

        fail_login = User.authenticate("test_auth", "wrong_password")

        self.assertFalse(fail_login)



































        # with self.client:

        #     user = self.client.post(
        #         '/signup',
        #         data=dict(
        #             username="testuser",
        #             password="HASHED_PASSWORD",
        #             image_url=None
        #         ), follow_redirects=True
        #     )
        
        #     resp = self.client.post(
        #         '/login',
        #         data=dict(
        #             username="testuser",
        #             password="WRONG_HASHED_PASSWORD"
        #         ), follow_redirects=True
        #     )

        #     self.assertIn(b'Welcome back.', resp.data)