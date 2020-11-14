import os 
from flask import Flask, flash, render_template, redirect, request, session, url_for 
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"]=os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"]=os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Get the Recipes from DB
@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = list(mongo.db.recipes.find())
    return render_template ("recipes.html", recipes=recipes)

#Registration functionality
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        #check the passwords 
        if request.form.get("password") == request.form.get("confirmpassword"):
            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get("password"))
            }
            mongo.db.users.insert_one(register)
        # put the new user into 'session' cookie
            session["user"] = request.form.get("username").lower()
            flash("Registration Successful!")
            return redirect(url_for("login"))
        else:
            flash("Passwords do not match! Please try again")
            return redirect(url_for("register"))
    return render_template("register.html")

#Log in functionality
@app.route("/login", methods=["GET","POST"]) 
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one({"username": request.form.get("username").lower()})

        if existing_user:
            #check password hashed 
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")))
                return redirect(url_for("get_recipes", username=session["user"]))

            else:
                flash("Invalid Username and/or Password")
                return redirect(url_for("login"))
                
        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")   


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")   
    return redirect(url_for("login"))


@app.route("/add_recipe", methods=["GET","POST"])
def add_recipe():
    if request.method =="POST":
        recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_name" : request.form.get("recipe_name"),
            "cuisine" : request.form.get("cuisine"),
            "cooking_time" : request.form.get("cooking_time"),
            "ingredients" : request.form.get("ingredients"),
            "recipe_description": request.form.get("recipe_description"),
            "cooking_method": request.form.get("cooking_method"),
            "uploaded_by": session["user"],
            "udloaded_at": request.form.get("udloaded_at")
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe succesfully added!")
        return redirect(url_for("get_recipes"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


@app.route("/edit_recipe/<recipe_id>", methods=["GET","POST"])
def edit_recipe(recipe_id):
    if request.method =="POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_name" : request.form.get("recipe_name"),
            "cuisine" : request.form.get("cuisine"),
            "cooking_time" : request.form.get("cooking_time"),
            "ingredients" : request.form.get("ingredients"),
            "recipe_description": request.form.get("recipe_description"),
            "cooking_method": request.form.get("cooking_method"),
            "uploaded_by": session["user"],
            "udloaded_at": request.form.get("udloaded_at")
        }
        mongo.db.recipes.update({"_id":ObjectId(recipe_id)}, submit)
        flash("Recipe succesfully updated!")

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html", recipe=recipe , categories=categories)


@app.route("/delete_recipe/<recipe_id>")
def delete_recipe(recipe_id):
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe succesfully deleted!")
    return redirect(url_for("get_recipes"))

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)

