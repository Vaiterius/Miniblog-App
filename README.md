# Bruhlog - A mini blogging application

## Follow bloggers, like articles, comment your thoughts—share with the world!

## Visit the website here: https://flask-bruhlog.herokuapp.com/

## For the CS50x 2022 final project. Video demo: https://youtu.be/grkiV1PqBM4


## Description
A social networking website where users can upload and share whatever is worth posting
through blogs.

Powered by Python's [Flask](https://flask.palletsprojects.com/en/2.2.x/) framework and SQL. Deployed on the [Heroku](https://www.heroku.com/) cloud platform.


## Features
- User account creation and log in system
- Commenting system
- Following system
- Liking system
- Upload image files from local
- Editing and deleting posts

## How It Works
The website has a development environment with its own SQLite database locally on my computer as
well as a production copy deployed on the Heroku service platform, but uses PostgreSQL instead.

Data coming in from the client via AJAX or otherwise are passed through Flask POST routes where it is
(hopefully) cleansed and inserted into the relational database.

In order for the following/follower system to work, the tables are related through many-to-many
relationships using an association table from [SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/), an ORM. Other tables such as user posts
employ a one-to-many relationship, since a user can have many posts.

Some JavaScript magic was at work so when a user hits like on a post, the page does not have to refresh
to update the DOM, but instead sends an AJAX request so it updates dynamically.

The code also integrates with AWS s3 services using the SDK [boto3](https://aws.amazon.com/sdk-for-python/) library. Images uploaded
for a blog post are stored in s3 buckets and subsequently edited or deleted as needed.


## Challenges
Hours and hours upon hours of bugfixing and reading documentation/tutorials. Also it was frustrating at
times trying to implement features on your own without straight up following a tutorial verbatim, but they
were valuable learning experiences.

Combining the [TinyMCE WYSIWYG editor](https://www.tiny.cloud/) with the s3 bucket by far was the most time-consuming process, but it
eventually worked out in the end.

I'm not the greatest frontend UI designer so tinkering with the CSS and Javascript took quite a while
compared to how much I worked in the Flask and SQL backend.


## Reflections
This was my biggest project so far (more to come) and I've learned a ton about how web development works
especially in backend technologies. CS50x gave me just enough foundation in Flask and SQL to jumpstart
my own working website and allowed me to expand my skillset outside of the course's curriculum.

There were some features such as categorizing and tagging posts that due to potential scope creep I had to
remove and set aside for maybe as "future" updates. They were nice to have but weren't necessary for a fully-functioning
blogging website in my opinion, especially since this is just an intro to computer science course.

I started this project last year but because of motivation issues and a general lack of time due to school,
it prevented me from finishing this project as fast as I wanted it to. But I sat down one day, decided to finally
push through it and get the course over with, and finished it.

If I had to redo everything I did and make a brand new website (and I currently am), I would make sure to employ
better *web design principles*, write *cleaner and more concise code*, use more *flask extensions* than reinvent the wheel, make
*wireframes/prototypes* and also *database schema* for the pre-production phase, and *set clear goals* for the website to
prevent scope creep.

If it weren't for the course I would not have been the programmer I am today and I am grateful for that.


## Thanks
This project would not have existed without the knowledge and education provided by
[CS50x](https://cs50.harvard.edu/x/2022/),
[Michael Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world),
[Tech With Tim](https://www.youtube.com/playlist?list=PLzMcBGfZo4-nK0Pyubp7yIG0RdXp6zklu),
and more.


### This was CS50x!