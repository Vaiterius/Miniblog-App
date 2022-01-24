-- SQLite
SELECT * FROM posts;
SELECT * FROM users;
SELECT * FROM post_likes;

-- INSERT INTO post_likes (post_id, liker_id) VALUES (1, 1);
-- INSERT INTO post_likes (post_id, liker_id) VALUES (1, 6);
-- INSERT INTO post_likes (post_id, liker_id) VALUES (1, 7);
-- INSERT INTO post_likes (post_id, liker_id) VALUES (1, 8);

SELECT * FROM posts WHERE id = 1;
SELECT * FROM post_likes;

-- Get post ID and its total likes.
SELECT 
    posts.id AS post_id,
    COUNT(posts.id) AS likes
FROM
    posts JOIN post_likes
ON
    posts.id = post_likes.post_id;

-- Get post info and its likers.
SELECT
    posts.id AS post_id,
    users.username AS liker
FROM
    users JOIN posts JOIN post_likes
ON
    users.id = post_likes.liker_id
WHERE
    posts.id = 1;

DROP TABLE user_followers;
