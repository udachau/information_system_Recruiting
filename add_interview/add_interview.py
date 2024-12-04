from flask import request, Blueprint, render_template, session, redirect, url_for
from dbcm import UseDatabase
from mysql.connector.errors import DatabaseError, InterfaceError, ProgrammingError
from checker import check_role

interview_bp = Blueprint('interview_bp', __name__, template_folder='templates')


def get_employees(cursor):
    _SQL = '''SELECT employee_id, name FROM employees WHERE dismissal_date IS NULL;'''
    cursor.execute(_SQL)
    result = cursor.fetchall()
    keys = ['id', 'name']
    result = [dict(zip(keys, line)) for line in result]
    print('---EMPLOYEES:', result)  # Лог для отладки
    return result


def get_openings(cursor):
    _SQL = '''SELECT opening_id, position_id FROM openings WHERE close_date IS NULL;'''
    cursor.execute(_SQL)
    result = cursor.fetchall()
    keys = ['id', 'name']
    result = [dict(zip(keys, line)) for line in result]
    print('---OPENINGS:', result)  # Лог для отладки
    return result


def get_candidates(cursor):
    _SQL = '''SELECT candidate_id, name FROM candidates;'''
    cursor.execute(_SQL)
    result = cursor.fetchall()
    keys = ['id', 'name']
    result = [dict(zip(keys, line)) for line in result]
    print('---CANDIDATES:', result)  # Лог для отладки
    return result


def get_id_from_session(_list, find_name):
    try:
        # Преобразуем find_name в int для поиска
        find_name = int(find_name)
        for item in _list:
            if item['id'] == find_name:
                return item['id']
        print(f'ID not found for: {find_name} in {_list}')  # Лог для отладки
    except ValueError:
        print(f'ValueError: Cannot convert {find_name} to int')
    return None




def to_page(cursor, return_to):
    if return_to == 'employee':
        employee_choice = get_employees(cursor)
        return render_template('form_parts.html', part='employee',
                               employees=employee_choice, selected=session.get('employee'))
    elif return_to == 'opening':
        opening_choice = get_openings(cursor)
        return render_template('form_parts.html', part='opening',
                               openings=opening_choice, selected=session.get('opening'))
    elif return_to == 'candidate':
        candidate_choice = get_candidates(cursor)
        return render_template('form_parts.html', part='candidate',
                               candidates=candidate_choice, selected=session.get('candidate'))
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

            employee = request.form.get('employee')
            opening = request.form.get('opening')
            candidate = request.form.get('candidate')
            date = request.form.get('date')

            if employee:
                print('---EMPLOYEE SELECTED:', employee)
                session['employee'] = [get_employees(cursor), employee]

                # Печать текущего состояния сессии
                print(session['employee'])

                return to_page(cursor, 'opening')
            elif opening:
                print('---OPENING SELECTED:', opening)
                session['opening'] = [get_openings(cursor), opening]

                # Печать текущего состояния сессии
                print(session['employee'])
                print(session['opening'])

                return to_page(cursor, 'candidate')
            elif candidate:
                print('---CANDIDATE SELECTED:', candidate)
                session['candidate'] = [get_candidates(cursor), candidate]

                # Печать текущего состояния сессии
                print(session['employee'])
                print(session['opening'])
                print(session['candidate'])

                return to_page(cursor, 'date')
            elif date:
                print('---DATE SELECTED:', date)
                session['date'] = date

                # Печать текущего состояния сессии
                print(session['employee'])
                print(session['opening'])
                print(session['candidate'])
                print(session['date'])

                return render_template('confirm.html',
                                       employee=session['employee'][1],
                                       opening=session['opening'][1],
                                       candidate=session['candidate'][1],
                                       date=date)
            else:
                employee_choice = get_employees(cursor)
                session['employee'] = ['', '']
                return render_template('form_parts.html', part='employee', employees=employee_choice)

    except ProgrammingError as e:
        print('---SQL ERROR:', e)
        return render_template('error.html', error_msg="Ошибка при выполнении SQL-запроса!")
    except InterfaceError as e:
        print('---INTERFACE ERROR:', e)
        return render_template('error.html', error_msg="Ошибка подключения к базе данных!")
    except DatabaseError as e:
        print('---DATABASE ERROR:', e)
        return render_template('error.html', error_msg="Ошибка базы данных!")


@interview_bp.route('/save', methods=['POST'])
@check_role
def save_interview():
    if not request.form.get('save'):
        return redirect(url_for('interview_bp.add_interview'))

    print('---DEBUG SESSION BEFORE SAVE---')
    print('Employee:', session.get('employee'))
    print('Opening:', session.get('opening'))
    print('Candidate:', session.get('candidate'))
    print('Date:', session.get('date'))

    try:
        with UseDatabase(session['db_config']) as cursor:
            # Получение ID сотрудника
            employee_id = get_id_from_session(session['employee'][0], session['employee'][1])
            if not employee_id:
                return render_template('error.html', error_msg="Сотрудник не выбран!")
            
            # Получение ID вакансии
            opening_id = get_id_from_session(session['opening'][0], session['opening'][1])
            if not opening_id:
                return render_template('error.html', error_msg="Вакансия не выбрана!")
            
            # Получение ID кандидата
            candidate_id = get_id_from_session(session['candidate'][0], session['candidate'][1])
            if not candidate_id:
                return render_template('error.html', error_msg="Кандидат не выбран!")

            # SQL-запрос для таблицы interviews
            _SQL = '''INSERT INTO interviews (date, employee_id, opening_id) 
                      VALUES (%s, %s, %s);'''
            cursor.execute(_SQL, (session['date'], employee_id, opening_id))

            # Получение ID собеседования
            interview_id = cursor.lastrowid

            # SQL-запрос для таблицы interview_details
            _SQL = '''INSERT INTO interview_details (candidate_id, interview_id, result)
                      VALUES (%s, %s, %s);'''
            cursor.execute(_SQL, (candidate_id, interview_id, 0))

            # Явное подтверждение транзакции
            cursor.connection.commit()

            print('---INTERVIEW SAVED SUCCESSFULLY---')
            print('Interview ID:', interview_id)

    except (ProgrammingError, InterfaceError, DatabaseError) as e:
        print('---SAVE ERROR:', e)
        return render_template('error.html', error_msg="Не удалось сохранить данные!")

    # Очистка сессии
    session.pop('employee', None)
    session.pop('opening', None)
    session.pop('candidate', None)
    session.pop('date', None)

    return render_template('result.html')
