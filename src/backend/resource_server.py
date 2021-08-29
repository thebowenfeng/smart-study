from flask import Flask, request, Response, json
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import functools
import time
from logistic_regression_sentencevote import SentenceVote
import requests
from bs4 import BeautifulSoup
import math
from collections import defaultdict
import hashlib
import datetime
import jwt
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
CORS(app)
db = SQLAlchemy(app)
model = SentenceVote()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(1000), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    in_session = db.Column(db.Boolean, nullable=True)
    session_topics = db.Column(db.String)
    browse_data = db.Column(db.String(10000), nullable=True)
    website_data = db.Column(db.String(10000), nullable=True)
    app_data = db.Column(db.String(10000), nullable=True)
    face_data = db.Column(db.String(10000), nullable=True)
    start_time = db.Column(db.Integer, nullable=True)
    prev_interval_scores = db.Column(db.String(10000), nullable=True)
    prev_browser_score = db.Column(db.Float, nullable=True)
    prev_face_score = db.Column(db.Float, nullable=True)
    prev_score = db.Column(db.Float, nullable=True)


def sigmoid(x: float) -> float:
    return 1 / (1 + math.e ** -(15.2 * x - 6))


def yawn_exp(x:float):
    result = (0.99 * (x + 0.15) + 0.56) ** 14.5
    return 0.6 if result > 0.6 else result


def validate_access_token(access_token: str, username: str):
    try:
        payload = jwt.decode(access_token, "secret_key", algorithms=["HS256"])
        if payload['username'] == username:
            return True
        else:
            return Response(
                json.dumps({"message": "Wrong access token"}),
                status=403
            )
    except Exception as e:
        print(e)
        return Response(
            json.dumps({"message": "Invalid access token"}),
            status=403
        )


def auth(func):
    @functools.wraps(func)
    def wrapper(*args):
        access_token = request.headers.get("Authorization")
        username = request.get_json()['Username']

        auth_status = validate_access_token(access_token, username)

        if auth_status is True:
            return func(*args)
        else:
            return auth_status
    return wrapper


def classify_site(url: str) -> int:
    resp = requests.get(url)
    parsed = BeautifulSoup(resp.text, 'html.parser')

    all_text = ""
    for text in parsed.find_all("p"):
        all_text = all_text + text.get_text() + "\n"

    result = model.test(all_text)

    if result[result.argmax(axis=0)] < 3:
        return -1
    else:
        return result.argmax(axis=0)


@app.route("/validate", methods=['POST'])
def validate():
    args = request.get_json()
    username = args['username']
    password : str = args['password']

    for user in Users.query.filter_by(username=username).all():
        if user.password_hash == hashlib.sha256(password.encode("utf-8")).hexdigest():
            return Response(
                json.dumps({"message": "success"}),
                status=200
            )

    return Response(
        json.dumps({"message": "User or password is incorrect"}),
        status=403
    )


@app.route("/get_info", methods=['POST'])
@auth
def get_info():
    username = request.get_json()['Username']

    return Response(
        json.dumps({"username": username, "password": "admin"}),
        status=200
    )


@app.route("/get_status", methods=['POST'])
@auth
def get_status():
    username = request.get_json()['Username']

    user_obj = Users.query.filter_by(username=username).first()

    if user_obj.in_session:
        return Response(
            json.dumps({"status": "yes"}),
            status=200
        )
    else:
        return Response(
            json.dumps({"status": "no"}),
            status=200
        )


@app.route("/post_browser_data", methods=["POST"])
@auth
def browser_data():
    url = request.get_json()["URL"]
    username = request.get_json()["Username"]
    user_obj: Users = Users.query.filter_by(username=username).first()

    if not user_obj.in_session:
        return Response(
            json.dumps({"message": "User not in session"}),
            status=403
        )

    exp = re.compile("^https?:\/\/(.+?)\/")
    if len(exp.findall(url)) == 0:
        domain = "undefined"
    else:
        domain = exp.findall(url)[0]

    website_data = defaultdict(lambda: 0)

    if user_obj.website_data is None or user_obj.website_data == "":
        pass
    else:
        for entry in user_obj.website_data.split("|"):
            if len(entry.split(",")) < 2:
                continue
            key, val = entry.split(",")
            website_data[key] = int(val)

    website_data[domain] += 1
    user_obj.website_data = ""

    for key, val in website_data.items():
        user_obj.website_data += f"{key},{val}|"

    print(user_obj.website_data)

    category = classify_site(url)
    curr_time = int(time.time())

    curr_timestamp = curr_time - user_obj.start_time
    user_obj.browse_data += f"{str(curr_timestamp)},{str(category)}|"
    db.session.commit()

    return Response(
        json.dumps({"message": "success"}),
        status=200
    )


@app.route("/post_face_data", methods=["POST"])
@auth
def face_data():
    action = request.get_json()["Action"]
    time_length = request.get_json()["Length"]
    username = request.get_json()["Username"]
    user_obj: Users = Users.query.filter_by(username=username).first()

    if not user_obj.in_session:
        return Response(
            json.dumps({"message": "User not in session"}),
            status=403
        )

    curr_timestamp = int(time.time()) - user_obj.start_time
    user_obj.face_data += f"{str(curr_timestamp)},{action},{str(time_length)}|"
    db.session.commit()

    return Response(
        json.dumps({"message": "success"}),
        status=200
    )


@app.route("/post_app_data", methods=["POST"])
@auth
def app_data():
    username = request.get_json()["Username"]
    curr_app_data = request.get_json()["Apps"]
    user_obj: Users = Users.query.filter_by(username=username).first()

    if not user_obj.in_session:
        return Response(
            json.dumps({"message": "User not in session"}),
            status=403
        )

    all_app_data = defaultdict(lambda: 0)

    if user_obj.app_data is None or user_obj.app_data == "":
        pass
    else:
        for entry in user_obj.app_data.split("|"):
            if len(entry.split(",")) < 2:
                continue
            key, val = entry.split(",")
            all_app_data[key] = int(val)

    for app in curr_app_data.split("|"):
        all_app_data[app] += 1

    user_obj.app_data = ""
    for key, val in all_app_data.items():
        user_obj.app_data += f"{key},{str(val)}|"

    db.session.commit()

    return Response(
        json.dumps({"message": "success"}),
        status=200
    )


@app.route("/set_session_status", methods=["POST"])
@auth
def set_status():
    username = request.get_json()["Username"]
    status = request.get_json()["Status"]
    user_obj : Users = Users.query.filter_by(username=username).first()

    if status == "start":
        if user_obj.in_session:
            return Response(
                json.dumps({"message": "success"}),
                status=200
            )

        user_obj.in_session = True
        user_obj.start_time = int(time.time())
        user_obj.browse_data = ""
        user_obj.face_data = ""
        user_obj.website_data = ""
        user_obj.session_topics = request.get_json()["Topic"]
        db.session.commit()

        return Response(
            json.dumps({"message": "success"}),
            status=200
        )
    elif status == "stop":
        if not user_obj.in_session:
            return Response(
                json.dumps({"message": "success"}),
                status=200
            )

        topics = user_obj.session_topics.split("|")
        topics.append("-1")

        web_data = [pair.split(",") for pair in user_obj.browse_data.split("|")]
        motion_data = [pair.split(",") for pair in user_obj.face_data.split("|")]
        total_time = int(time.time()) - user_obj.start_time

        if total_time / 6.0 < 1:
            interval_len = 1
        else:
            interval_len = int(total_time / 6.0)

        intervals = range(0, total_time, interval_len)

        scores = defaultdict(lambda: 0)
        irrelevant = 0
        semi_irrelevant = 0
        reg_motion = 0
        yawn = 0

        for i in range(len(intervals) - 1):
            lower_lim = intervals[i]
            upper_lim = intervals[i + 1]
            temp_irr_count = 0
            temp_semi_count = 0
            temp_reg_motion = 0
            temp_yawn = 0

            for data in web_data:
                if '' in data:
                    continue
                if lower_lim <= int(data[0]) < upper_lim:
                    if data[1] == "4":
                        temp_irr_count += 1
                        irrelevant += 1
                    elif data[1] not in topics:
                        temp_semi_count += 1
                        semi_irrelevant += 1

            for data in motion_data:
                if '' in data:
                    continue
                if lower_lim <= int(data[0]) < upper_lim:
                    if data[1] == "yawn":
                        temp_yawn += float(data[2])
                        yawn += float(data[2])
                    else:
                        temp_reg_motion += float(data[2])
                        reg_motion += float(data[2])

            scores[str(upper_lim)] += sigmoid(temp_irr_count / 5)
            scores[str(upper_lim)] += sigmoid(temp_semi_count / 5) / 2
            scores[str(upper_lim)] += sigmoid(temp_reg_motion / 5)
            scores[str(upper_lim)] += yawn_exp(temp_yawn / 5)
            scores[str(upper_lim)] = 1 - scores[str(upper_lim)]

        overall_browser_score = 1 - (sigmoid(irrelevant / total_time) + sigmoid(semi_irrelevant / total_time) / 2)
        overall_face_score = 1 - (sigmoid(reg_motion / total_time) + yawn_exp(yawn / total_time))

        user_obj.prev_browser_score = overall_browser_score
        user_obj.prev_face_score = overall_face_score
        user_obj.prev_score = (overall_face_score + overall_browser_score) / 2
        user_obj.prev_interval_scores = "|".join([f"{str(key)}:{str(val)}" for key, val in scores.items()])

        print(user_obj.prev_interval_scores)

        user_obj.in_session = False
        user_obj.start_time = None
        db.session.commit()

        return Response(
            json.dumps({"message": "success"}),
            status=200
        )
    else:
        return Response(
            json.dumps({"message": "Invalid status message"}),
            status=403
        )


@app.route("/get_interval_scores", methods=["POST"])
@auth
def get_browser_scores():
    username = request.get_json()["Username"]
    user_obj: Users = Users.query.filter_by(username=username).first()
    graph_dict = {}

    if user_obj.prev_interval_scores is None or user_obj.prev_interval_scores == "":
        return Response(
            json.dumps({"message": "no data"}),
            status=403
        )

    for pair in user_obj.prev_interval_scores.split("|"):
        if len(pair.split(":")) != 2:
            continue
        key, val = pair.split(":")
        graph_dict[key] = val

    return Response(
        json.dumps(graph_dict),
        status=200
    )


@app.route("/get_website_data", methods=["POST"])
def get_web_data():
    username = request.get_json()["Username"]
    user_obj: Users = Users.query.filter_by(username=username).first()
    data_dict = {}

    if user_obj.website_data is None or user_obj.website_data == "":
        return Response(
            json.dumps({"message": "no data"}),
            status=403
        )

    for entry in user_obj.website_data.split("|"):
        if len(entry.split(",")) < 2:
            continue
        key, val = entry.split(",")
        data_dict[key] = val

    return Response(
        json.dumps(data_dict),
        status=200
    )


@app.route("/get_app_data", methods=["POST"])
def get_app_data():
    username = request.get_json()["Username"]
    user_obj: Users = Users.query.filter_by(username=username).first()
    data_dict = {}

    if user_obj.app_data is None or user_obj.app_data == "":
        return Response(
            json.dumps({"message": "no data"}),
            status=403
        )

    for entry in user_obj.app_data.split("|"):
        if len(entry.split(",")) < 2:
            continue
        key, val = entry.split(",")
        data_dict[key] = val

    return Response(
        json.dumps(data_dict),
        status=200
    )


@app.route("/get_score", methods=["POST"])
@auth
def get_score():
    username = request.get_json()["Username"]
    user_obj: Users = Users.query.filter_by(username=username).first()

    if user_obj.prev_score is None or user_obj.prev_face_score is None or user_obj.prev_browser_score is None:
        return Response(
            json.dumps({"message": "no score"}),
            status=403
        )
    else:
        return Response(
            json.dumps({"score": str(user_obj.prev_score),
                        "browser_score": str(user_obj.prev_browser_score),
                        "face_score": str(user_obj.prev_face_score)}),
            status=200
        )


@app.route("/register", methods=["POST"])
def register():
    username = request.get_json()["Username"]
    password : str = request.get_json()["Password"]
    email = request.get_json()["Email"]

    if Users.query.filter_by(username=username).first() is not None:
        return Response(
            json.dumps({"message": "user already exist"}),
            status=403
        )

    new_user = Users(username=username,
                     password_hash=hashlib.sha256(password.encode("utf-8")).hexdigest(),
                     email=email
                     )

    db.session.add(new_user)
    db.session.commit()

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


#if __name__ == '__main__':
    #app.run(port=5002)