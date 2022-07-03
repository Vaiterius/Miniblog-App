from __future__ import annotations
from blogapp import db, fc

from datetime import datetime

# A self-referential association table to link users and their followers.
followers = db.Table(
    "followers",
    db.Column("followed_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("follower_id", db.Integer, db.ForeignKey("users.id"))
)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(fc["max_username_length"]), unique=True, nullable=False)
    first_name = db.Column(db.String(fc["max_name_length"]), nullable=False)
    last_name = db.Column(db.String(fc["max_name_length"]), nullable=False)
    hash = db.Column(db.String(), nullable=False)
    about_me = db.Column(db.String(fc["max_bio_length"]))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Posts", backref="author", lazy="dynamic")

    # This was so damn difficult to understand.
    users_followed = db.relationship(
        "Users",  # Same class by nature of being self-referential.
        secondary=followers,  # Configures association table for the relationship.
        primaryjoin=(followers.c.follower_id == id),  # Link follower user with association table.
        secondaryjoin=(followers.c.followed_id == id),  # Link followed user with association table.
        backref=db.backref("user_followers", lazy="dynamic"),
        lazy="dynamic"  # Dynamic to run when specifically requested.
    )

    def __repr__(self):
        return f"<User #{self.id} | {self.username}>"
    
    def get_hash(self):
        return self.hash
    
    def get_avatar(self, size: int=64):
        return f"https://ui-avatars.com/api/?name={self.first_name}+{self.last_name}&background=random&size={size}"
    
    def is_following(self, user: Users) -> bool:
        """Return True if User is following the user in the given parameter"""
        # The query returns a 1 if user is found to be followed by User.
        return self.users_followed.filter(
            followers.c.followed_id == user.id).count() > 0
    
    def own_posts(self, is_descending=False):
        """Return user's own posts"""
        if is_descending:
            return Posts.query.filter_by(author_id=self.id).order_by(Posts.date_posted.desc())
        return Posts.query.filter_by(author_id=self.id)
    
    def followed_posts(self, is_descending=False):
        """Return posts of users followed by session user combined with own posts"""
        followed_posts =  Posts.query.join(  # Join tables of user's posts and user's followers.
            followers, followers.c.followed_id == Posts.id
        ).filter(  # Filter table to posts whose user is being followed by session user.
            followers.c.follower_id == self.id)
        own_posts = self.own_posts()

        if is_descending:
            return followed_posts.union(own_posts).order_by(Posts.date_posted.desc()) # Recent posts are up top first.
        return followed_posts.union(own_posts)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(fc["max_title_length"]), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(fc["max_desc_length"]))
    date_posted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def get_posts(is_descending=False):
        """Return all posts with optional descending order"""
        if is_descending:
            return Posts.query.order_by(Posts.date_posted.desc())
        return Posts.query.all()


class PostLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    liker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

