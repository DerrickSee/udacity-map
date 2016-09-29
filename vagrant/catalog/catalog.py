from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash, \
     check_password_hash


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.sqlite3'
app.secret_key = 'super secret key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    is_authenticated = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    is_anonymous = db.Column(db.Boolean, default=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def get_id(self):
        return self.id


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)

    def __init__(self, title, description):
        self.title = title
        self.description = description

    def __repr__(self):
        return '<Category %r>' % self.title


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title, description, category, created=None):
        self.title = title
        self.description = description
        self.category = category
        if created is None:
            created = datetime.utcnow()
        self.created = created

    def __repr__(self):
        return '<Item %r>' % self.title


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/')
def index():
    return render_template('index.html', categories=Category.query.all())


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        if User.query.filter_by(username=username).first():
            flash('User already exists. Please use another username.')
        elif username and password == password2:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('You have been registered successfully.')
        else:
            flash('Please make sure password is the same.')
        # permission to access the `next` url
        return redirect('/')
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
        # Login and validate the user.
        # user should be an instance of your `User` class
            login_user(user)
            flash('Logged in successfully.')
        else:
            flash('Login fail. Please make sure your username and password is correct.')

        # next = request.args.get('next')
        # next_is_valid should check if the user has valid
        # permission to access the `next` url
        return redirect('/')
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/categories/create/', methods=['GET', 'POST'])
def category_create():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        if title and description:
            category = Category(title=title, description=description)
            db.session.add(category)
            db.session.commit()
            return redirect('/categories/%s' % category.id)
    return render_template('category_form.html', categories=Category.query.all())


@app.route('/categories/<int:category_id>', methods=['GET',])
def category_detail(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category:
        ctx = {
            'categories': Category.query.all(),
            'category': category,
            'items': Item.query.filter_by(category_id=category_id),
        }
        return render_template('category_detail.html', **ctx)
    return abort(404)

@app.route('/categories/<int:category_id>/update', methods=['GET', 'POST'])
def category_update(category_id):
    category = Category.query.filter_by(id=category_id).first()
    ctx = {
        'category': category,
        'categories': Category.query.all(),
    }
    if category:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            if title and description:
                category.title = title
                category.description = description
                db.session.commit()
                return redirect('/categories/%s' % category_id)
            else:
                ctx.update({'error': "Please ensure all fields are filled."})
        return render_template('category_form.html', **ctx)
    return abort(404)


@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def category_delete(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category:
        ctx = {
            'category': category,
            'categories': Category.query.all(),
        }
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            if title and description:
                category.title = title
                category.description = description
                db.session.commit()
                return redirect('/categories/%s' % category_id)
            else:
                ctx.update({'error': "Please ensure all fields are filled."})
        return render_template('category_delete.html', **ctx)
    return abort(404)


@app.route('/categories/<int:category_id>/add', methods=['GET', 'POST'])
def item_create(category_id):
    category = Category.query.filter_by(id=category_id).first()
    ctx = {
        'category': category,
        'categories': Category.query.all(),
    }
    if category:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            if title and description:
                item = Item(title=title, description=description, category=category)
                db.session.add(item)
                db.session.commit()
                return redirect('/categories/%s' % category_id)
            else:
                ctx.update({'error': "Please ensure all fields are filled."})
        return render_template('item_form.html', **ctx)
    return abort(404)


@app.route('/categories/<int:category_id>/<int:item_id>', methods=['GET'])
def item_detail(category_id, item_id):
    category = Category.query.filter_by(id=category_id).first()
    item = Item.query.filter_by(id=item_id).first()
    if category and item:
        ctx = {
            'category': category,
            'categories': Category.query.all(),
            'item': item
        }
        return render_template('item_detail.html', **ctx)
    return abort(404)


@app.route('/categories/<int:category_id>/<int:item_id>/update', methods=['GET', 'POST'])
def item_update(category_id, item_id):
    category = Category.query.filter_by(id=category_id).first()
    item = Item.query.filter_by(id=item_id).first()
    ctx = {
        'category': category,
        'categories': Category.query.all(),
        'item': item
    }
    if category and item:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            if title:
                item.title = title
                item.description = description
                db.session.commit()
                return redirect('/categories/%s/%s' % (category_id, item_id))
            else:
                ctx.update({'error': "Please ensure all fields are filled."})
        return render_template('item_form.html', **ctx)
    return abort(404)


@app.route('/categories/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
def item_delete(category_id, item_id):
    category = Category.query.filter_by(id=category_id).first()
    item = Item.query.filter_by(id=item_id).first()
    ctx = {
        'category': category,
        'categories': Category.query.all(),
        'item': item
    }
    if category and item:
        if request.method == 'POST':
            db.session.delete(item)
            db.session.commit()
            return redirect('/categories/%s' % category_id)
        return render_template('item_delete.html', **ctx)
    return abort(404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
