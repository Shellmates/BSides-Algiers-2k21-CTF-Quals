#!/usr/bin/python3
from flask import Flask, Response, redirect, request, jsonify, render_template
from string import ascii_lowercase, digits
from random import choice
from dbmanager import DBManager
from datetime import datetime, timedelta
import os

app = Flask(__name__)
dbmgr = DBManager(os.getenv("DB_FILE"))

charset = digits + ascii_lowercase
random = lambda: "".join(choice(charset) for _ in range(8))


@app.route("/", methods=["GET", "POST"])
def root():
    return render_template("index.html")


@app.route("/paste/new", methods=["POST"])
def create_paste():
    data = request.get_json()

    if not data or not "title" in data or not "text" in data:
        return jsonify({"success": False, "reason": "missing title/text"}), 400

    paste_id = random()
    dbmgr.add_paste(paste_id, data["title"], data["text"])

    return jsonify({"success": True, "url": f"/paste/{paste_id}"})


@app.route("/paste/<paste_id>", methods=["GET"])
def fetch_paste(paste_id):
    paste = dbmgr.get_paste(paste_id)

    if paste is None:
        return jsonify({"success": False, "reason": "no such paste"}), 404

    title, text = paste[1:]

    return jsonify({"success": True, "title": title, "text": text})


@app.route("/paste/<paste_id>/<field>", methods=["GET"])
def fetch_field(paste_id, field):
    if dbmgr.paste_exists(paste_id):
        try:
            value = dbmgr.get_paste_field(paste_id, field)
            return f"{value}\n"
        except:
            return jsonify({"success": False, "reason": "no such info"}), 404
    else:
        return jsonify({"success": False, "reason": "no such paste"}), 404


@app.route("/paste/<paste_id>", methods=["DELETE"])
def delete_paste(paste_id):
    if paste_id == "sp05m8vu":
        return jsonify({"success": False, "reason": "Don't be stupid."})

    dbmgr.delete_paste(paste_id)

    return jsonify({"success": True})
