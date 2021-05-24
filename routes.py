from functools import wraps
from typing import List

from flask import flash, redirect, url_for, render_template, request, Response, make_response
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app
from config import Config
from forms import LoginForm, MatchForm
from methods import check_token, get_next_match, prepare_for_next_week, update_winner
from models import User, Player, Group, Match


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


@app.route("/play", methods=["GET", "POST"])
@cookie_login_required
def play():
    user: User = current_user
    if not (1 <= user.week <= 7):
        flash(f"Invalid week {user.week}")
        return redirect(url_for("home"))
    match: Match = get_next_match(user.season, user.week)
    if match is None and user.week == 7:
        flash("All 7 weeks completed. Please review the standings. Game Over")
        return redirect(url_for("standings", region=Config.APAC))
    if match is None:
        prepare_for_next_week()
        flash(f"Week {user.week} completed. You have been logged out. Login again to start next week")
        return redirect(url_for("logout"))
    form = MatchForm(match)
    if not form.validate_on_submit():
        return render_template("play.html", match=match, form=form, title="Play")
    update_winner(match, winner=form.match_radio.data)
    url = url_for("play")
    if match.type in Config.REGION_CHANGE or \
            (match.type in Config.GROUP_REGION_CHANGE and match.group == Config.GROUP_D):
        url = url_for("results", region=match.region, week=match.week)
    return redirect(url)


@app.route("/standings/<region>")
@cookie_login_required
def standings(region: str):
    my_region = Config.APAC if not region or region not in Config.REGIONS else region
    user: User = current_user
    players: List[Player] = Player.objects.filter_by(region=my_region, season=user.season).get()
    players.sort(key=lambda player: player.rank)
    return render_template("standings.html", title="Standings", region=my_region, season=user.season, players=players)


@app.route("/results/<region>/<int:week>")
@cookie_login_required
def results(region: str, week: int):
    user: User = current_user
    grouped_players: List[Group] = Group.objects.filter_by(region=region, week=week, season=user.season).get()
    match_players: List[Match] = Match.objects.filter_by(region=region, week=week, season=user.season).get()
    match_players.sort(key=lambda match: match.match_id)
    groups: List[List[Group]] = list()
    matches: List[List[Match]] = list()
    for group_index in range(0, 4):
        groups.append([player for player in grouped_players if player.group == Config.GROUPS[group_index]])
        matches.append([match for match in match_players if match.group == Config.GROUPS[group_index]])
    quarterfinals: List[Match] = [match for match in match_players if match.type in Config.QUARTERFINALS]
    finals: List[Match] = [match for match in match_players if match.type in Config.FINALS]
    return render_template("results.html", title="Results", region=region, season=user.season, week=week, finals=finals,
                           max_weeks=user.week, groups=groups, group_matches=matches, quarterfinals=quarterfinals, )


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("standings", region=Config.APAC))
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template("login.html", form=form)
    user = User.objects.filter_by(username=form.username.data).first()
    if not user or not user.check_password(form.password.data):
        flash("Invalid username or password")
        return render_template("login.html", form=form)
    token = user.get_token()
    login_user(user=user)
    next_page = request.args.get("next")
    if not next_page or url_parse(next_page).netloc != str():
        next_page = url_for("standings", region=Config.APAC)
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
