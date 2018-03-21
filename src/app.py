from flask import Flask, render_template, request, session, make_response

from src.common.database import Database
from src.models.blog import Blog
from src.models.post import Post
from src.models.user import User

app = Flask(__name__)
app.secret_key="ada aja"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.before_first_request
def initialize_database():
    Database.initialize()

@app.route('/auth/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']

    if User.login_valid(email,password):
        User.login(email)
    else:
        session['email'] = None

    return render_template('profile.html', email=session['email'])

@app.route('/auth/logout', methods=['GET'])
def logout_user():
    User.logout()
    return render_template('home.html')


@app.route('/auth/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['email']

    User.register(email, password)
    return render_template('profile.html', email=session['email'])

@app.route('/blogs/<string:user_id>')
@app.route('/blogs')
def user_blogs(user_id=None):
    if user_id is not None:
        user = User.get_by_id(user_id)
    else:
        user = User.get_by_email(session['email'])

    user_blogs = user.get_blogs()

    return render_template('user_blogs.html', user_blogs=user_blogs, email=user.email)

@app.route('/posts/<string:blog_id>')
def blog_posts(blog_id):
    print("blog_id {}".format(blog_id))
    blog = Blog.from_mongo(blog_id)
    posts = blog.get_posts()

    return render_template('posts.html', posts=posts, blog_title=blog.title,
                           blog_id=blog._id)


@app.route('/blogs/new', methods=['POST','GET'])
def create_new_blog():
    if request.method == 'GET':
        return render_template('new_blog.html')
    else:
        title = request.form['title']
        description = request.form['description']
        user = User.get_by_email(session['email'])
        new_blog = Blog(user.email, title, description, user._id)
        new_blog.save_to_mongo()
        return make_response(user_blogs(user._id))

@app.route('/posts/new/<string:blog_id>', methods=['POST','GET'])
def create_new_post(blog_id):
    if request.method == 'GET':
        return render_template('new_post.html', blog_id=blog_id)
    else:
        title = request.form['title']
        content = request.form['content']
        user = User.get_by_email(session['email'])
        new_post = Post(blog_id, content, title, user.email)
        new_post.save_to_mongo()
        return make_response(blog_posts(blog_id))

if __name__ == '__main__':
    app.run(port=4000)