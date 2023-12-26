from authlib.integrations.flask_client import OAuth
from flask import Flask, url_for, redirect, render_template, session, Response
import requests
import time


def fetch_data(location: str, params: dict = {}):
    return requests.get((appConfig.get('BASE_URL') + location),
                        headers={"Authorization": f"Bearer {session.get('token')['access_token']}"},
                        params=params).json()


def fetch_new_token():
    return oauth.testApp.fetch_access_token(refresh_token=session['token']['refresh_token'],
                                            grant_type='refresh_token')


app = Flask(__name__)
app.jinja_env.globals.update(fetch_new_token=fetch_new_token)

appConfig = {
    "OAUTH2_CLIENT_ID": "authpy",
    "OAUTH2_CLIENT_SECRET": "M7rXgYmSKIf-UraURWA2FBiPSVU",
    "BASE_URL": "https://student.sbhs.net.au/api",
    "FLASK_SECRET": "ca45313770bf434552e2a8c8",
    "FLASK_PORT": 5000
}

app.secret_key = appConfig.get("FLASK_SECRET")

oauth = OAuth(app)
oauth.register(
    "testApp",
    client_id=appConfig.get("OAUTH2_CLIENT_ID"),
    client_secret=appConfig.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "all-ro",
        "state": "abc",
    },
    authorize_url=f"{appConfig.get('BASE_URL')}/authorize",
    access_token_url=f"{appConfig.get('BASE_URL')}/token",
)


@app.route("/")
def homepage():
    if "token" not in session:
        return render_template("test.html", session=session.get("token"),
                               pretty=session.get("token"))
    # return fetch_data("/timetable/daytimetable.json", {"date": "2021-08-20"})
    json_timetable = fetch_data("/timetable/daytimetable.json", {"date": "2021-08-20"})
    return render_template("test.html", session=session.get("token"),
                           pretty=json_timetable, fetch_new_token=fetch_new_token())


@app.route("/testlogin")
def login():
    if "token" in session:
        return redirect(url_for("homepage"))
    redirect_uri = url_for('callback', _external=True)
    return oauth.testApp.authorize_redirect(redirect_uri=redirect_uri)


@app.route("/testlogout")
def logout():
    session.clear()
    return redirect(url_for("homepage"))


@app.route("/callback")
def callback():
    token = oauth.testApp.authorize_access_token()
    session["token"] = token
    return redirect(url_for("homepage"))


# "https://student.sbhs.net.au/api/<component>/<method>.<return format>?<parameters>"

# Authorisation Endpoint:	https://student.sbhs.net.au/api/authorize
# Token Endpoint:	https://student.sbhs.net.au/api/token
# API Scopes: all-ro - read-only access to a student's Portal data
# API Resource Endpoint:	https://student.sbhs.net.au/api/
# client_id
# client_secret

if __name__ == '__main__':
    app.run(debug=False)
