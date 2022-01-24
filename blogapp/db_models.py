from __future__ import annotations
from blogapp import db, form_constraints as fc

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

    posts = db.relationship("Posts", backref="author", lazy="dynamic")
    # This was so damn difficult to understand.
    users_followed = db.relationship(
        "Users",  # Same class by nature of being self-referential.
        secondary=followers,  # Configures association table for the relationship.
        primaryjoin=(followers.c.follower_id == id),  # Link follower user with association table.
        secondaryjoin=(followers.c.followed_id == id),  # Link followed user with association table.
        backref=db.backref("followers", lazy="dynamic"),
        lazy="dynamic"  # Dynamic to run when specifically requested.
    )

    def __repr__(self):
        return f"<User #{self.id} | {self.username}>"
    
    def get_hash(self):
        return self.hash
    
    def is_following(self, user: Users) -> bool:
        """Return True if User is following the user in the given parameter"""
        # The query returns a 1 if user is found to be followed by User.
        return self.users_followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    def get_date(self):
        return self.date_posted


class PostLikes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    liker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

