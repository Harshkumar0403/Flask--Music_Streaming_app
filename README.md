# Flask--Music_Streaming_app
 The Flask music streaming application employs the Flask framework and SQLAlchemy for backend development, featuring user authentication, distinct user roles, and secure database operations. Utilizing Flask-WTF for form handling, the project incorporates a robust MVC structure. Frontend elements are designed with Jinja templating.
The application supports RESTful APIs, incorporates rigorous security measures, and undergoes testing with Flask-Testing. Deployment is achieved through Docker for containerization, ensuring scalability and consistency. The project highlights Git for version control, promoting collaborative development and efficient management of features.
**Technology used**
• Flask: for basic backend Implementation.
• Flask_sqlalchemy: for implementing Database.
• datetime: for storing the date for the deadline.
• Some inbuilt libraries like jinja2, render_template, redirect, and url_for displaying HTML content.
• flash: to show an alert
• Flask_Login: for implementing the login functionality
• werkzeug.security: for hashing the password
• Flask-Restful: to create Api

**API USED**
There are three API:
1. *UserAPI*-
• It is linked to two endpoints:
• /api/user – With this endpoint, we can get all users in database, creating user.
• /api/user/<int:id> – With this endpoint, we can get user with input id, updating user with
respective id, deleting user with respective id
API USED

2. *AlbumAPI*-
• It is linked to three endpoints:
•/api/album/<int:album_id> – With this endpoint, we can get all album with respective id from

database.

•/api/album/<int:user_id>/album/<int:album_id> – With this endpoint, we can get album with
respective id under respective user, delete album with respective id under
respective user, update album with respective id under respective user.
•/api/album/<int:user_id>/album – With this endpoint, we can create album under respective user

3. *SongAPI*-
• It is linked to three endpoints:
•/api/album/song/<int:album_id> – With this endpoint, we can get all songs with respective id

from database.

•/api/album/song/<int:album_id>/album/<int:song_id>/song – With this endpoint, we can get songs

with respective id under respective album.

•/api/album/song/<int:song_id>/song – With this endpoint, we can get song under respective id.
