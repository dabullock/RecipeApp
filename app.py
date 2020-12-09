import os
from dotenv import load_dotenv
import pymongo
import datetime
from bson.objectid import ObjectId
from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
import bcrypt
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

## necessary for python-dotenv ##
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

mongo = 'mongodb+srv://daniel:Z47c6cI1SfOvWElZ@schoolserver.coq5b.mongodb.net/schoolServer?retryWrites=true&w=majority'#os.getenv('MONGO')
print(mongo)
client = pymongo.MongoClient(mongo)

db = client['schoolServer'] # Mongo collection
users = db['users'] # Mongo document
roles = db['roles'] # Mongo document
categories = db['categories'] # Mongo document
recipes = db['recipes'] # Mongo document

login = LoginManager()
login.init_app(app)
login.login_view = 'login'

@login.user_loader
def load_user(username):
    u = users.find_one({"email": username})
    if not u:
        return None
    return User(username=u['email'], role=u['role'], id=u['_id'], first_name=u['first_name'], last_name=u['last_name'])

class User:
    def __init__(self, id, username, role, first_name, last_name):
        self._id = id
        self.username = username
        self.role = role
        self.first_name = first_name
        self.last_name = last_name

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

'''
    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)
'''

### custom wrap to determine role access  ### 
def roles_required(*role_names):
    def decorator(original_route):
        @wraps(original_route)
        def decorated_route(*args, **kwargs):
            if not current_user.is_authenticated:
                print('The user is not authenticated.')
                return redirect(url_for('login'))
            
            print(current_user.role)
            print(role_names)
            if not current_user.role in role_names:
                print('The user does not have this role.')
                flash('Account access not permitted here', category='warning')
                return redirect(url_for('login'))
            else:
                print('The user is in this role.')
                return original_route(*args, **kwargs)
        return decorated_route
    return decorator


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return 'self register for an account'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        print(request.form['username'])
        user = users.find_one({"email": request.form['username']})
        print(user)
        if user and user['password'] == request.form['password']:
            user_obj = User(username=user['email'], role=user['role'], id=user['_id'], first_name=user['first_name'], last_name=user['last_name'])
            login_user(user_obj)
            next_page = request.args.get('next')

            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
                return redirect(next_page)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("index"))

        flash("Wrong username or password!", category='error')
    return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash('You have successfully logged out.', 'success')
    return redirect(url_for('login'))


@app.route('/my-account/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('user', 'contributor', 'admin')
def my_account(user_id):
    edit_account = users.find_one({'_id': ObjectId(user_id)})
    if edit_account:
        return render_template('my-account.html', user=edit_account)
    flash('User not found.', 'warning')
    return redirect(url_for('index'))

@app.route('/update-myaccount/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('user', 'contributor', 'admin')
def update_myaccount(user_id):
    if request.method == 'POST':
        form = request.form

        password = request.form['password']

        users.update({'_id': ObjectId(user_id)},
            {
            'first_name': form['first_name'],
            'last_name': form['last_name'],
            'email': form['email'],
            'password': password,
            'role': form['role'],
            'date_added': form['date_added'],
            'date_modified': datetime.datetime.now()
            })
        update_account = users.find_one({'_id': ObjectId(user_id)})
        flash(update_account['email'] + ' has been modified.', 'success')
        return redirect(url_for('index'))
    return redirect(url_for('index'))


##########  Admin functionality -- User management ##########

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_users():
    return render_template('users.html', all_roles=roles.find(), all_users=users.find())


@app.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_add_user():
    if request.method == 'POST':
        form = request.form
        
        password = request.form['password']
        
        email = users.find_one({"email": request.form['email']})
        if email:
            flash('This email is already registered.', 'warning')
            return 'This email has already been registered.'
        new_user = {
            'first_name': form['first_name'],
            'last_name': form['last_name'],
            'email': form['email'],
            'password': password,
            'role': form['role'],
            'date_added': datetime.datetime.now(),
            'date_modified': datetime.datetime.now()
        }
        users.insert_one(new_user)
        flash(new_user['email'] + ' user has been added.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('users.html', all_roles=roles.find(), all_users=users.find())

@app.route('/admin/delete-user/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_delete_user(user_id):
    delete_user = users.find_one({'_id': ObjectId(user_id)})
    if delete_user:
        users.delete_one(delete_user)
        flash(delete_user['email'] + ' has been deleted.', 'warning')
        return redirect(url_for('admin_users'))
    flash('User not found.', 'warning')
    return redirect(url_for('admin_users'))

@app.route('/admin/edit-user/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_edit_user(user_id):
    edit_user = users.find_one({'_id': ObjectId(user_id)})
    if edit_user:
        return render_template('edit-user.html', user=edit_user, all_roles=roles.find())
    flash('User not found.', 'warning')
    return redirect(url_for('admin_users'))

@app.route('/admin/update-user/<user_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def admin_update_user(user_id):
    if request.method == 'POST':
        form = request.form

        password = request.form['password']

        users.update({'_id': ObjectId(user_id)},
            {
            'first_name': form['first_name'],
            'last_name': form['last_name'],
            'email': form['email'],
            'password': password,
            'role': form['role'],
            'date_added': form['date_added'],
            'date_modified': datetime.datetime.now()
            })
        update_user = users.find_one({'_id': ObjectId(user_id)})
        flash(update_user['email'] + ' has been added.', 'success')
        return redirect(url_for('admin_users'))
    return render_template('users.html', all_roles=roles.find(), all_users=users.find())

##########  Recipes ##########

# VIEW ALL RECIPES LIST
@app.route('/recipes/all', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor', 'user')
def fetch_all_recipes():
    return render_template('all-recipes.html', all_users=recipes.find())

# VIEW INDIVIDUAL RECIPE DETAILS
@app.route('/recipes/view-recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor', 'user')
def view_recipe(recipe_id):
    view_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    if view_recipe:
        return render_template('view-recipe.html', recipe=view_recipe, all_roles=roles.find(), all_categories=categories.find(), user_email=session['_user_id'])
    flash('Recipe not found.', 'warning')
    return redirect(url_for('fetch_all_recipes'))

# VIEW ALL RECIPES w/ admin features
@app.route('/recipes/manage', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor')
def recipe_manager():
    return render_template('recipes.html', all_roles=roles.find(), all_users=recipes.find())

# GIVE NEW RECIPE FORM
@app.route('/recipes/new-recipe', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor')
def new_recipe():
    if request.method == 'GET':
        return render_template('new-recipe.html', firstName=current_user.first_name, lastName=current_user.last_name, all_categories=categories.find())
    if request.method == 'POST':
        return 'This should add a recipe'
    #view_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    #if view_recipe:
       # return render_template('view-recipe.html', firstName=current_user.first_name, lastName=current_user.last_name, all_categories=categories.find())
    #flash('Recipe not found.', 'warning')
    #return redirect(url_for('fetch_all_recipes'))

@app.route('/recipes/add-recipe', methods=['POST'])
@login_required
@roles_required('admin', 'contributor')
def add_recipe():
    if request.method == 'POST':
        form = request.form
        recipe_data = {
            'recipe_name': form['recipe_name'],
            'category': form['category'],
            'ingredients': form['ingredients'],
            'preparation': form['preparation'],
            'notes': form['notes'],
            'first_name': form['author_first'],
            'last_name': form['author_last'],
            'date_added': datetime.datetime.now(),
            'date_modified': datetime.datetime.now()
        }
        recipes.insert_one(recipe_data)
        flash('Saved New Recipe: {}'.format(form['recipe_name']), 'success')
        return redirect(url_for('recipe_manager'))
    else:
        return render_template('new-recipe.html', firstName=current_user.first_name, lastName=current_user.last_name, all_categories=categories.find())


# DELETE RECIPE
@app.route('/recipes/delete-recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor')
def delete_recipe(recipe_id):
    delete_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    if delete_recipe:
        recipes.delete_one(delete_recipe)
        flash(delete_recipe['recipe_name'] + ' has been deleted.', 'warning')
        return redirect(url_for('recipe_manager'))
    flash('Recipe not found.', 'warning')
    return redirect(url_for('recipe_manager'))

# LOAD EDIT TEMPLATE
@app.route('/recipes/edit-recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor')
def edit_recipe(recipe_id):
    edit_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
    if edit_recipe:
        return render_template('edit-recipe.html', recipe=edit_recipe, all_roles=roles.find(),all_categories=categories.find(), user_email=session['_user_id'])
    flash('Recipe not found.', 'warning')
    return redirect(url_for('recipe_manager'))

# UPDATE RECIPE
@app.route('/recipes/update-recipe/<recipe_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'contributor')
def update_recipe(recipe_id):
    if request.method == 'POST':
        form = request.form
        if current_user.first_name == form['author_first'] and current_user.last_name == form['author_last']:
            try:
                recipes.update({'_id': ObjectId(recipe_id)},
                    {
                    'recipe_name': form['recipe_name'],
                    'category': form['category'],
                    'ingredients': form['ingredients'],
                    'preparation': form['preparation'],
                    'notes': form['notes'],
                    'first_name': form['author_first'],
                    'last_name': form['author_last'],
                    'date_added': form['date_added'],
                    'date_modified': datetime.datetime.now()
                    })
                update_recipe = recipes.find_one({'_id': ObjectId(recipe_id)})
            except Exception as e:
                print(e)
            flash('Updated Recipe', 'success')
            return redirect(url_for('recipe_manager'))
        else:
            flash('Cannot update recipes you did not post', 'warning')
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))
    return render_template('recipes.html', all_roles=roles.find(), all_users=recipes.find())


@app.route('/recipes/search', methods=['POST'])
@login_required
@roles_required('admin', 'contributor', 'user')
def serch_recipe():
    if request.method == 'POST':
        form = request.form
        allRecipes = recipes.find()
        search_data = form['search_string']
        #search_terms = search_data.split(' ')
        if search_data == '':
            flash('Please enter search keywords', 'warning')
            return redirect(url_for('index'))
        results = list()
        for recipe in allRecipes:
            if search_data.lower() in recipe['recipe_name'].lower():
                results.append(recipe)
        if len(results) == 0:
            flash('No recipes matching search', 'warning')
            return redirect(url_for('index'))
        return 'Search feature not yet implemented, found %s results'%(len(results))
    else:
        return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True)
