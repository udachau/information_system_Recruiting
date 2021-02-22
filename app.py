from flask import Flask, redirect, render_template, url_for, session, request
import json
from checker import check_role
from authorization.login import auth_blueprint
from add_interview.add_interview import interview_bp
from myrequests.requests_controller import requests_bp
from report.report import report_bp
from os import urandom

app = Flask(__name__)

app.register_blueprint(auth_blueprint)
app.register_blueprint(interview_bp)
app.register_blueprint(requests_bp)
app.register_blueprint(report_bp)

with open('data_files/secret_key.json') as f:
    app.secret_key = json.load(f)['secret_key']


@app.route('/requests', methods=["GET", "POST"])
@check_role
def requests_menu():
    req = request.args.get('req')

    with open('data_files/requests_menu.json', encoding='utf-8') as f:
        r_menu = json.load(f)

    route_mapping = {
        '1': url_for('requests_bp.request1'),
        '2': url_for('requests_bp.request2'),
        '3': url_for('requests_bp.request3'),
        'exit': url_for('menu')
    }

    if req is None:
        return render_template('requests_ menu.html', menu=r_menu,
                               user=session['db_config']['user'], password=session['db_config']['password'])
    else:
        return redirect(route_mapping[req])



@app.route('/', methods=["GET", "POST"])
@check_role
def menu():
    with open('data_files/menu.json', encoding='utf-8') as f:
        main_menu = json.load(f)

    req = request.args.get('req')

    route_mapping = {
        'requests': url_for('requests_menu'),
        'make': url_for('interview_bp.add_interview'),
        'reports': url_for('report_bp.proc'),
        'exit': 'exit.html'
    }

    if req is None:
        return render_template('menu.html', menu=main_menu,
                               user=session['db_config']['user'], password=session['db_config']['password'])
    if req != 'exit':
        return redirect(route_mapping[req])
    else:
        session.pop('db_config')
        return render_template(route_mapping[req])


if __name__ == '__main__':
    app.run(debug=True)