from flask import Flask, request, render_template, redirect, flash, Response, json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
import datetime
import random
import string

app = Flask(__name__)
app.secret_key = "bruh"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///auth_db.db'
CORS(app)
db = SQLAlchemy(app)

CLIENT_ID = "react"
CLIENT_SECRET = "my secret"


class AuthCodes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(100), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        callback_url = request.args.get('callback')
        if callback_url is None:
            flash("Please specify a callback URL in the form of a URL query parameter ?callback=", "error")
            return redirect("/login")

        username = request.form['username']
        password = request.form['password']

        resp = requests.post("https://resource-smartstudy.herokuapp.com/validate", json={"username": username, "password": password})
        if resp.status_code == 403:
            flash(resp.json()["message"], "error")
            return redirect("/login?callback=" + callback_url)

        auth_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

        if AuthCodes.query.filter_by(username=username).first() is not None:
            auth_obj = AuthCodes.query.filter_by(username=username).first()
            auth_obj.code = auth_code
        else:
            auth_obj = AuthCodes(code=auth_code, username=username)
            db.session.add(auth_obj)

        db.session.commit()

        return redirect(callback_url + "?auth_code=" + auth_code)


@app.route('/get_access_token', methods=['POST'])
def get_token():
    args = request.get_json()
    client_id = args["ClientID"]
    client_secret = args["ClientSecret"]
    auth_code = args["AuthCode"]

    if client_id == CLIENT_ID and client_secret == CLIENT_SECRET:
        auth_obj = AuthCodes.query.filter_by(code=auth_code).first()
        if auth_obj is None:
            return Response(
                json.dumps({"message": "Invalid authorization code"}),
                status=403
            )

        access_token = jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                "iat": datetime.datetime.utcnow(),
                "sub": "access",
                "username": auth_obj.username
            },
            "secret_key",
            algorithm="HS256"
        )

        refresh_token = jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=10000),
                "iat": datetime.datetime.utcnow(),
                "sub": "refresh",
                "username": auth_obj.username
            },
            "secret_key",
            algorithm="HS256"
        )

        id_token = jwt.encode(
            {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=10000),
                "iat": datetime.datetime.utcnow(),
                "sub": "id",
                "username": auth_obj.username
            },
            "secret_key",
            algorithm="HS256"
        )

        return Response(
            json.dumps({"access_token": access_token,
                        "refresh_token": refresh_token,
                        "id_token": id_token}),
            status=200
        )
    else:
        return Response(
            json.dumps({"message": "Invalid client credentials"}),
            status=403
        )


@app.route("/refresh_access_token", methods=['POST'])
def refresh():
    args = request.get_json()
    client_id = args["ClientID"]
    client_secret = args["ClientSecret"]
    refresh_tok = args["RefreshToken"]

    if client_id == CLIENT_ID and client_secret == CLIENT_SECRET:
        try:
            payload = jwt.decode(refresh_tok, "secret_key", algorithms=["HS256"])
            if payload['sub'] == "refresh":
                username = payload['username']

                access_token = jwt.encode(
                    {
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5),
                        "iat": datetime.datetime.utcnow(),
                        "sub": "access",
                        "username": username
                    },
                    "secret_key",
                    algorithm="HS256"
                )

                refresh_token = jwt.encode(
                    {
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=10000),
                        "iat": datetime.datetime.utcnow(),
                        "sub": "refresh",
                        "username": username
                    },
                    "secret_key",
                    algorithm="HS256"
                )

                id_token = jwt.encode(
                    {
                        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=10000),
                        "iat": datetime.datetime.utcnow(),
                        "sub": "id",
                        "username": username
                    },
                    "secret_key",
                    algorithm="HS256"
                )

                return Response(
                    json.dumps({"access_token": access_token,
                                "refresh_token": refresh_token,
                                "id_token": id_token}),
                    status=200
                )
            else:
                return Response(
                    json.dumps({"message": "Incorrect token"}),
                    status=403
                )
        except:
            return Response(
                json.dumps({"message": "Invalid token"}),
                status=403
            )
    else:
        return Response(
            json.dumps({"message": "Invalid client credentials"}),
            status=403
        )


if __name__ == "__main__":
    app.run(port=5001)