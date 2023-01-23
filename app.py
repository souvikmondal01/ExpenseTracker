import os
import json
import pytz
from uuid import uuid1, uuid4
from flask import Flask, request, jsonify
from datetime import datetime, date
import pandas as pd

db = {}
db_filename = "db.json"

if os.path.exists(db_filename):
    f = open(db_filename, "r")
    db = json.load(f)
else:
    access_key = str(uuid1())
    secret_key = str(uuid4())
    item_type = ["Food", "Shoping", "Medical", "Education", "Bills", "Others"]
    db = {
        "access_key": access_key,
        "secret_key": secret_key,
        "item_type": item_type,
        "email_list": [],
        "users": []
    }
    f = open(db_filename, "w+")
    json.dump(db, f, indent=4)

app = Flask(__name__)


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    user_dict = {
        "name": name,
        "username": username,
        "email": email,
        "password": password,
        "purchases": {}
    }

    email_list = []
    for e in db["users"]:
        email_list.append(e["email"])

    if email not in email_list:
        email_list.append(email)
        db["email_list"] = email_list
        db["users"].append(user_dict)
        f = open(db_filename, "w+")
        json.dump(db, f, indent=4)
        return "User added successfully"
    else:
        return "User already exists"


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    for user in db["users"]:
        if user["email"] == email and user["password"] == password:
            user_index = db["users"].index(user)

            response = {
                "message": "Logged in successfully",
                "user_index": user_index
            }
            return response
        else:
            continue
    return "Wrong email or password"


@app.route("/add_purchase", methods=["POST"])
def add_purchase():
    user_index = int(request.form["user_index"])
    item_name = request.form["item_name"]
    item_type = request.form["item_type"]
    item_price = request.form["item_price"]

    curr_date = str(date.today())
    curr_time = str(datetime.now(pytz.timezone("Asia/Kolkata")))

    item_dict = {
        "item_name": item_name,
        "item_type": item_type,
        "item_price": item_price,
        "purchase_time": curr_time

    }
    if len(db["users"][user_index]["purchases"]) == 0:
        db["users"][user_index]["purchases"][curr_date] = []
        db["users"][user_index]["purchases"][curr_date].append(item_dict)
        f = open(db_filename, "r+")
        json.dump(db, f, indent=4)
        return "Item added successfully"
    else:
        db["users"][user_index]["purchases"][curr_date].append(item_dict)
        f = open(db_filename, "r+")
        json.dump(db, f, indent=4)
        return "Item added successfully"


@app.route("/get_all_purchases_for_today", methods=["GET"])
def get_all_purchases_for_today():
    user_index = int(request.args["user_index"])
    curr_date = str(date.today())
    purchases_dates = list(db["users"][user_index]["purchases"].keys())
    if curr_date in purchases_dates:
        purchases_today = db["users"][user_index]["purchases"][curr_date]
        return jsonify(purchases_for_today=purchases_today)
    else:
        return jsonify(msg="Data not found")


@app.route("/get_purchases", methods=["GET"])
def get_purchases():
    data = request.json
    user_index = data["user_index"]
    start_date = data["start_date"]
    end_date = data["end_date"]

    dates = pd.date_range(start_date, end_date)
    date_in_DB = list(db["users"][user_index]['purchases'].keys())
    purchase_dict = {}
    for dt in date_in_DB:
        if dt in dates:
            purchase_dict[dt] = db["users"][user_index]['purchases'][dt]
        else:
            continue
    return purchase_dict


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)
