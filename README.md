# Flask Blog API

A RESTful API for a simple blog platform built using Flask and MongoDB. It supports user registration, login, posting articles with image uploads, following users, likes, comments, and personalized feeds.


## 🚀 Features

- **User Authentication**
  - Register and login securely using Flask-Login and Bcrypt.
- **Post Management**
  - Create, read, and delete blog posts.
  - Upload images using Cloudinary.
- **Social Features**
  - Follow/unfollow users.
  - Like and unlike posts.
  - Comment on posts.
  - Get feed from followed users.
- **Password Validation**
  - Enforces strong password policy (upper, lower, digit, special char).


## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB (via Flask-PyMongo)
- **Authentication**: Flask-Login & Flask-Bcrypt
- **Image Upload**: Cloudinary
- **Environment Variables**: python-dotenv



## 📦 Installation

### 1. Clone the Repository


git clone https://github.com/UkohEmmanuel1/Blog_api.git
cd Blog_api
2. Create a Virtual Environment

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Create .env File
Create a .env file in the project root and add your credentials:

env
SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_connection_string
CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
▶️ Running the Application

python server.py
By default, the app will run on:


http://127.0.0.1:5000
🔌 API Endpoints
🔐 Auth
Method	Endpoint	Description
POST	/auth/register	Register a new user
POST	/auth/login	Login existing user
POST	/auth/logout	Logout authenticated user

👤 Users
Method	Endpoint	Description
POST	/follow/<user_id>	Follow a user

📝 Posts
Method	Endpoint	Description
POST	/posts	Create a new post (with image)
GET	/posts	Retrieve all posts
GET	/posts/<post_id>	Retrieve a single post by ID
DELETE	/posts/<post_id>	Delete a post (author only)

📰 Feed
Method	Endpoint	Description
GET	/feed	Get posts from followed users

💬 Comments
Method	Endpoint	Description
POST	/comments/<post_id>	Add a comment
GET	/comments/<post_id>	Retrieve comments

❤️ Likes
Method	Endpoint	Description
POST	/likes/<post_id>	Like or unlike a post (toggle)

🔐 Password Policy
To enhance security, passwords must include:

At least 8 characters

At least 1 uppercase letter

At least 1 lowercase letter

At least 1 digit

At least 1 special character

📝 License
This project is licensed under the MIT License. See the LICENSE file for more information.

🙋‍♂️ Contact
For any inquiries, reach out via emmanuelukoh08@gmail.com.



Let me know if you'd like me to generate a `requirements.txt` file too, or convert this into an actual downloadable `.md` file.
