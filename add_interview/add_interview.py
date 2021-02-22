from flask import request, Blueprint, render_template, session, redirect, url_for
from dbcm import UseDatabase
import json
from mysql.connector.errors import DatabaseError, InterfaceError, ProgrammingError
from checker import check_role

interview_bp = Blueprint('interview_bp', __name__, template_folder='templates')


def get_recruiter(cursor):
    _SQL = '''SELECT id_worker, FName_worker
        FROM `recruiting`.`co-worker`
        WHERE id_struct = 12;
        '''

    cursor.execute(_SQL)
    result = cursor.fetchall()

    keys = ['id', 'name']
    result = [dict(zip(keys, line)) for line in result]

    return result


def get_vacancy(cursor):
    _SQL = '''SELECT id_vac, unit_vac
        FROM vacancy
        WHERE date_close = 00-00-0000;
        '''

    cursor.execute(_SQL)
    result = cursor.fetchall()

    keys = ['id', 'name']
    result = [dict(zip(keys, line)) for line in result]

    return result


def get_candidate(cursor):
    _SQL = """
    SELECT id_cand, FName_cand
    FROM `recruiting`.`candidate`
    """

    cursor.execute(_SQL)
    result = cursor.fetchall()

    keys = ['id', 'name']
    result = [dict(zip(keys, line)) for line in result]

    return result


def get_id_from_session(_list, find_name):
    for i in range(len(_list)):
        if _list[i]['name'] == find_name:
            return _list[i]['id']


def to_page(cursor, return_to):
    if return_to == 'recruiter':
        recruiter_choice = get_recruiter(cursor)
        return render_template('form_parts.html', part='recruiter',
                               recruiter=recruiter_choice, selected=session.get('recruiter'))
    elif return_to == 'vacancy':
        vacancy_choice = get_vacancy(cursor)
        return render_template('form_parts.html', part='vacancy',
                               vacancy=vacancy_choice, selected=session.get('vacancy'))
    elif return_to == 'candidate':
        candidate_choice = get_candidate(cursor)
        return render_template('form_parts.html', part='candidate',
                               candidate=candidate_choice, selected=session.get('candidate'))
    else:
        return render_template('form_parts.html', part='date', selected=session.get('date'))


@interview_bp.route('/add', methods=['GET', 'POST'])
@check_role
def add_interview():
    try:
        with UseDatabase(session['db_config']) as cursor:
            return_to = request.args.get('return')

            if return_to:
                return to_page(cursor, return_to)

            recruiter = request.form.get('recruiter')
            vacancy = request.form.get('vacancy')
            candidate = request.form.get('candidate')
            date = request.form.get('date')

            if recruiter:
                print('---recr')
                session['recruiter'][1] = recruiter
                session['recruiter'][0] = get_id_from_session(session['recruiter'][0], recruiter)

                vacancy = get_vacancy(cursor)
                session['vacancy'] = ['', '']
                session['vacancy'][0] = vacancy

                print(session['recruiter'])
                session.update()
                return render_template('form_parts.html', part='vacancy', vacancy=vacancy)

            elif vacancy:
                print('---vac')
                session['vacancy'][1] = vacancy
                session['vacancy'][0] = get_id_from_session(session['vacancy'][0], vacancy)

                candidate = get_candidate(cursor)
                session['candidate'] = ['', '']
                session['candidate'][0] = candidate

                print(session['recruiter'])
                print(session['vacancy'])
                print(session['candidate'])
                session.update()
                return render_template('form_parts.html', part='candidate', candidate=candidate)

            elif candidate:
                print('---cand')
                session['candidate'][1] = candidate
                session['candidate'][0] = get_id_from_session(session['candidate'][0], candidate)

                print(session['recruiter'])
                print(session['vacancy'])
                print(session['candidate'])
                session.update()
                return render_template('form_parts.html', part='date')

            elif date:
                print('---date')
                session['date'] = date

                print(session['recruiter'])
                print(session['vacancy'])
                print(session['candidate'])
                print(session['date'])
                return render_template('confirm.html',
                                       recruiter=session['recruiter'][1],
                                       vacancy=session['vacancy'][1],
                                       candidate=session['candidate'][1],
                                       date=session.get('date'))

            else:
                recruiter = get_recruiter(cursor)
                session['recruiter'] = ['', '']
                session['recruiter'][0] = recruiter
                session.update()
                return render_template('form_parts.html', part='recruiter', recruiter=recruiter)


    except ProgrammingError:
        return render_template('error.html', error_msg="Не удалось записать протокол!")
    except InterfaceError:
        return render_template('error.html', error_msg="Ошибка.")
    except DatabaseError:
        return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")



@interview_bp.route('/save', methods=['GET', 'POST'])
@check_role
def save_interview():
    if not request.form.get('save'):
        return redirect(url_for('interview_bp.add_interview'))

    try:
        with UseDatabase(session['db_config']) as cursor:
            _SQL = f"""INSERT INTO `recruiting`.`interview`(`date_int`, interview.`id_worker`, interview.`id_cand`, interview.`id_vac`) 
                   VALUES('{session['date']}', {session['recruiter'][0]}, {session['candidate'][0]}, {session['vacancy'][0]});"""
            print(_SQL)
            cursor.execute(_SQL)


    except ProgrammingError:
        return render_template('error.html', error_msg="Не удалось записать протокол!")
    except InterfaceError:
        return render_template('error.html', error_msg="Ошибка.")
    except DatabaseError:
        return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")


    session.pop('recruiter')
    session.pop('vacancy')
    session.pop('candidate')
    session.pop('date')

    return render_template('result.html')
