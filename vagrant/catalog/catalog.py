from datetime import datetime
from werkzeug import url_decode

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask.ext.social import Social
from flask.ext.social.datastore import SQLAlchemyConnectionDatastore
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_marshmallow import Marshmallow



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catalog.sqlite3'
app.config['SOCIAL_TWITTER'] = {
    'consumer_key': 'cXFSbW3fBlriA9lp9Ohf9pMdy',
    'consumer_secret': 'WBONBFSMz1k09GsaHTXwyK6FlCXFplm5r9UBXolPCGuA9X0gJ6'
}
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_POST_LOGIN_VIEW'] = 'index'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.secret_key = 'super secret key'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class MethodRewriteMiddleware(object):
    """
    Override post method to allow delete method for flask-social
    """

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if 'METHOD_OVERRIDE' in environ.get('QUERY_STRING', ''):
            args = url_decode(environ['QUERY_STRING'])
            method = args.get('__METHOD_OVERRIDE__')
            if method:
                method = method.encode('ascii', 'replace')
                environ['REQUEST_METHOD'] = method
        return self.app(environ, start_response)


app.wsgi_app = MethodRewriteMiddleware(app.wsgi_app)
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    """
    Role model required by flask-security
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    """
    User Model to store user information
    """
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.username

    def get_id(self):
        return self.id


class Category(db.Model):
    """
    Category Model. Grouping for items.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('categories', lazy='dynamic'))

    def __init__(self, title, description, user):
        self.title = title
        self.description = description
        self.user = user

    def __repr__(self):
        return '<Category %r>' % self.title


class Item(db.Model):
    """
    Item Model. Store title and description and grouped by Category.
    """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.Text)
    created = db.Column(db.DateTime)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
        backref=db.backref('items', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('items', lazy='dynamic'))

    def __init__(self, title, description, category, user, created=None):
        self.title = title
        self.description = description
        self.category = category
        if created is None:
            created = datetime.utcnow()
        self.created = created
        self.user = user

    def __repr__(self):
        return '<Item %r>' % self.title


class ItemSchema(ma.ModelSchema):
    class Meta:
        model = Item


class CategorySchema(ma.ModelSchema):
    class Meta:
        model = Category
    items = ma.Nested(ItemSchema, many=True, exclude=('user',))



class Connection(db.Model):
    """
    Used by flask-social to store provider and token information
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
        backref=db.backref('connections', lazy='dynamic'))
    provider_id = db.Column(db.String(255))
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    display_name = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))
    rank = db.Column(db.Integer)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
social = Social(app, SQLAlchemyConnectionDatastore(db, Connection))


# Index View. Shows Welcome page.
@app.route('/')
def index():
    return render_template('index.html', categories=Category.query.all())


# User Profile view. Allows user to connect account to social authentication.
# In this case, twitter.
@app.route('/profile')
@login_required
def profile():
    return render_template(
        'profile.html', twitter_conn=social.twitter.get_connection())


# View to create category. Login required.
@app.route('/categories/create/', methods=['GET', 'POST'])
@login_required
def category_create():
    ctx = {'categories': Category.query.all()}
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Check if title and description were filled
        if title and description:
            category = Category(title=title, description=description,
                                user=current_user)
            db.session.add(category)
            db.session.commit()
            return redirect('/categories/%s' % category.id)
        else:
            ctx.update({'error': 'Please make sure all fields are filled.'})
    return render_template('category_form.html', **ctx)


# View to view category details. Login not required.
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


# View to update category details.
# Login required and only accessible by user who created category.
@app.route('/categories/<int:category_id>/update', methods=['GET', 'POST'])
@login_required
def category_update(category_id):
    category = Category.query.filter_by(id=category_id).first()
    ctx = {
        'category': category,
        'categories': Category.query.all(),
    }
    if category and category.user == current_user:
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


# View to delete category.
# Login required and only accessible by user who created category.
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
@login_required
def category_delete(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category and category.user == current_user:
        ctx = {
            'category': category,
            'categories': Category.query.all(),
        }
        if request.method == 'POST':
            db.session.delete(category)
            db.session.commit()
            return redirect('/')
        return render_template('category_delete.html', **ctx)
    return abort(404)


# View to create items.
# Login required and only accessible by user who created category.
@app.route('/categories/<int:category_id>/add', methods=['GET', 'POST'])
@login_required
def item_create(category_id):
    category = Category.query.filter_by(id=category_id).first()
    if category and category.user == current_user:
        ctx = {
            'category': category,
            'categories': Category.query.all(),
        }
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            if title and description:
                item = Item(title=title, description=description,
                            category=category, user=current_user)
                db.session.add(item)
                db.session.commit()
                return redirect('/categories/%s' % category_id)
            else:
                ctx.update({'error': "Please ensure all fields are filled."})
        return render_template('item_form.html', **ctx)
    return abort(404)


# View to view item details. Login not required.
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


# View to update item.
# Login required and only accessible by user who created item.
@app.route('/categories/<int:category_id>/<int:item_id>/update', methods=['GET', 'POST'])
@login_required
def item_update(category_id, item_id):
    category = Category.query.filter_by(id=category_id).first()
    item = Item.query.filter_by(id=item_id).first()
    if category and item and item.user == current_user:
        ctx = {
            'category': category,
            'categories': Category.query.all(),
            'item': item
        }
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            if title and description:
                item.title = title
                item.description = description
                db.session.commit()
                return redirect('/categories/%s/%s' % (category_id, item_id))
            else:
                ctx.update({'error': "Please ensure all fields are filled."})
        return render_template('item_form.html', **ctx)
    return abort(404)


# View to delete item.
# Login required and only accessible by user who created item.
@app.route('/categories/<int:category_id>/<int:item_id>/delete', methods=['GET', 'POST'])
@login_required
def item_delete(category_id, item_id):
    category = Category.query.filter_by(id=category_id).first()
    item = Item.query.filter_by(id=item_id).first()
    if category and item and item.user == current_user:
        ctx = {
            'category': category,
            'categories': Category.query.all(),
            'item': item
        }
        if request.method == 'POST':
            db.session.delete(item)
            db.session.commit()
            return redirect('/categories/%s' % category_id)
        return render_template('item_delete.html', **ctx)
    return abort(404)


@app.route('/api/catalog.json')
def catalog_api():
    categories = Category.query.all()
    categories_schema = CategorySchema(many=True, exclude=('user',))
    result = categories_schema.dump(categories)
    return jsonify(result.data)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
