from flask import Flask, render_template, request, redirect, url_for  # For flask implementation
from pymongo import MongoClient  # Database connector
from bson.objectid import ObjectId  # For ObjectId to work
from bson.errors import InvalidId  # For catching InvalidId exception for ObjectId
import os

# Environment variables for MongoDB connection
mongodb_host = os.environ.get('MONGO_HOST', 'mongodb-service')  # Ensure this matches the MongoDB service name
mongodb_port = int(os.environ.get('MONGO_PORT', '27017'))
client = MongoClient(mongodb_host, mongodb_port)  # Configure the connection to the database
db = client.camp2016  # Select the database
todos = db.todo  # Select the collection

app = Flask(__name__)
title = "TODO with Flask"
heading = "ToDo Reminder"

def redirect_url():
    return request.args.get('next') or request.referrer or url_for('index')

@app.route("/list")
def lists():
    # Display all tasks
    todos_l = todos.find()
    a1 = "active"
    return render_template('index.html', a1=a1, todos=todos_l, t=title, h=heading)

@app.route("/")
@app.route("/uncompleted")
def tasks():
    # Display uncompleted tasks
    todos_l = todos.find({"done": "no"})
    a2 = "active"
    return render_template('index.html', a2=a2, todos=todos_l, t=title, h=heading)

@app.route("/completed")
def completed():
    # Display completed tasks
    todos_l = todos.find({"done": "yes"})
    a3 = "active"
    return render_template('index.html', a3=a3, todos=todos_l, t=title, h=heading)

@app.route("/done")
def done():
    # Toggle task completion status
    id = request.values.get("_id")
    task = todos.find({"_id": ObjectId(id)})
    if task[0]["done"] == "yes":
        todos.update_one({"_id": ObjectId(id)}, {"$set": {"done": "no"}})
    else:
        todos.update_one({"_id": ObjectId(id)}, {"$set": {"done": "yes"}})
    redir = redirect_url()  # Redirect to the previous URL
    return redirect(redir)

@app.route("/action", methods=['POST'])
def action():
    # Add a task
    name = request.values.get("name")
    desc = request.values.get("desc")
    date = request.values.get("date")
    pr = request.values.get("pr")
    todos.insert_one({"name": name, "desc": desc, "date": date, "pr": pr, "done": "no"})
    return redirect("/list")

@app.route("/remove")
def remove():
    # Delete a task
    key = request.values.get("_id")
    todos.delete_one({"_id": ObjectId(key)})
    return redirect("/")

@app.route("/update")
def update():
    # Render the update page
    id = request.values.get("_id")
    task = todos.find({"_id": ObjectId(id)})
    return render_template('update.html', tasks=task, h=heading, t=title)

@app.route("/action3", methods=['POST'])
def action3():
    # Update a task
    name = request.values.get("name")
    desc = request.values.get("desc")
    date = request.values.get("date")
    pr = request.values.get("pr")
    id = request.values.get("_id")
    todos.update_one({"_id": ObjectId(id)}, {'$set': {"name": name, "desc": desc, "date": date, "pr": pr}})
    return redirect("/")

@app.route("/search", methods=['GET'])
def search():
    # Search for a task
    key = request.values.get("key")
    refer = request.values.get("refer")
    try:
        if refer == "id":
            todos_l = todos.find({refer: ObjectId(key)})
            if not todos_l:
                return render_template('index.html', todos=todos_l, t=title, h=heading, error="No such ObjectId found")
        else:
            todos_l = todos.find({refer: key})
    except InvalidId:
        return render_template('index.html', todos=[], t=title, h=heading, error="Invalid ObjectId format given")
    
    return render_template('searchlist.html', todos=todos_l, t=title, h=heading)

@app.route("/about")
def about():
    return render_template('credits.html', t=title, h=heading)

@app.route("/ready")
def ready():
    return 'OK', 200

@app.route("/health")
def health():
    return "Error", 500

@app.route('/healthz')
def healthz():
    return 'OK', 200

if __name__ == "__main__":
    env = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5055))
    debug = False if env == 'production' else True
    app.run(host='0.0.0.0', port=port, debug=debug)
