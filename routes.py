from functools import wraps

from flask import flash, redirect, url_for, render_template, request, Response, make_response
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app
from config import Config
from forms import LoginForm
from methods import check_token
from models import User


def cookie_login_required(route_function):
    @wraps(route_function)
    def decorated_route(*args, **kwargs):
        if current_user.is_authenticated:
            return route_function(*args, **kwargs)
        user = check_token(request.cookies.get("token"))
        if user:
            login_user(user=user)
            return route_function(*args, **kwargs)
        # noinspection PyUnresolvedReferences
        return app.login_manager.unauthorized()

    return decorated_route


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    home_page = "home"
    error_message = "Invalid username or password"
    if current_user.is_authenticated:
        return redirect(url_for(home_page))
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("login.html", form=form)
    user = User.objects.filter_by(username=form.username.data).first()
    if not user or not user.check_password(form.password.data):
        flash(error_message)
        return render_template("login.html", form=form)
    token = user.get_token()
    login_user(user=user)
    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != str():
        next_page = url_for(home_page)
    response: Response = make_response(redirect(next_page))
    response.set_cookie("token", token, max_age=Config.TOKEN_EXPIRY, secure=Config.CI_SECURITY, httponly=True,
                        samesite="Strict")
    return response


@app.route("/logout")
@cookie_login_required
def logout():
    current_user.revoke_token()
    logout_user()
    return redirect(url_for("home"))
