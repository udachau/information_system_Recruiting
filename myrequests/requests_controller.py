from flask import request, Blueprint, render_template, session, redirect, url_for
from dbcm import UseDatabase
from pymysql.err import ProgrammingError, InterfaceError, OperationalError
from checker import check_role

requests_bp = Blueprint('requests_bp', __name__, template_folder='templates')

def make_request(cursor, sql, values, keys):
    """Универсальная функция для выполнения запросов."""
    cursor.execute(sql, values)
    result = cursor.fetchall()
    return [dict(zip(keys, line)) for line in result]


@requests_bp.route('/request1', methods=['GET', 'POST'])
@check_role
def request1():
    """Обработчик запроса 1."""
    _SQL = """
        SELECT COUNT(*) as employee_count, division_code
        FROM positions
        JOIN employees ON positions.position_id = employees.employee_id
        WHERE YEAR(employees.enrollment_date) = %s
        GROUP BY division_code;
    """

    # Если пользователь нажал "вернуться"
    if request.args.get('return'):
        return redirect(url_for('requests_menu'))

    # Получить введённый год
    year = request.form.get('year')

    if not year:
        return render_template('params_form_enter_year.html', request=1)

    if not year.isdigit() or int(year) < 1:
        return render_template('error.html', error_msg="Введите корректный год!")

    try:
        with UseDatabase(session['db_config']) as cursor:
            keys = ['employee_count', 'division_code']
            values = (year,)

            result = make_request(cursor, _SQL, values, keys)

            if not result:
                return render_template('no_data.html', message="Данные за указанный год не найдены.")

            return render_template('request1_result.html', report=result, year=year)

    except OperationalError:
        return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
    except InterfaceError:
        return render_template('error.html', error_msg="Ошибка подключения.")
    except ProgrammingError as e:
        return render_template('error.html', error_msg=f"Ошибка выполнения запроса: {e}")

@requests_bp.route('/request2', methods=['GET', 'POST'])
@check_role
def request2():
    _SQL = """
        SELECT e.*
        FROM employees e
        JOIN positions p ON e.position_id = p.position_id
        WHERE p.job_name = %s AND e.dismissal_date IS NULL
        ORDER BY e.birth_date DESC
        LIMIT 1;
    """

    if request.args.get('return'):
        return redirect(url_for('requests_menu'))

    text = request.form.get('text')

    if text:
        try:
            with UseDatabase(session['db_config']) as cursor:
                keys = ['employee_id', 'name', 'birth_date', 'address', 'education', 'position_id', 'salary', 'enrollment_date', 'dismissal_date']
                values = (text,)

                result = make_request(cursor, _SQL, values, keys)
                return render_template('request2_result.html', report=result, text=text)

        except OperationalError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось выполнить запрос!")

    return render_template('params_form_enter_depart_name.html', request=2)


@requests_bp.route('/request3', methods=['GET', 'POST'])
@check_role
def request3():
    _SQL = """
        SELECT p.position_id, p.job_name, CONCAT(p.min_salary, '-', p.max_salary) AS minmax_salary
        FROM positions p
        LEFT JOIN openings o ON p.position_id = o.position_id AND YEAR(o.open_date) = %s
        WHERE o.opening_id IS NULL;
    """

    if request.args.get('return'):
        return redirect(url_for('requests_menu'))

    year = request.form.get('year')

    if year:
        try:
            with UseDatabase(session['db_config']) as cursor:
                keys = ['position_id', 'job_name', 'minmax_salary']
                values = (year,)

                result = make_request(cursor, _SQL, values, keys)
                return render_template('request3_result.html', report=result, year=year)

        except OperationalError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось выполнить запрос!")

    return render_template('params_form_enter_year.html', request=3)
