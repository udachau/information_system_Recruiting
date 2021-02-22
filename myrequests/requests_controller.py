from flask import request, Blueprint, render_template, session, redirect, url_for
from dbcm import UseDatabase
from mysql.connector.errors import InterfaceError, ProgrammingError, DatabaseError
import json
from checker import check_role

requests_bp = Blueprint('requests_bp', __name__, template_folder='templates')


def make_request(cursor, sql, values, keys):
    cursor.execute(sql, values)
    result = cursor.fetchall()

    result = [dict(zip(keys, line)) for line in result]
    return result


@requests_bp.route('/request1', methods=['GET', 'POST'])
@check_role
def request1():
    _SQL = """SELECT id_struct, unit_vac, COUNT(*) as count
    FROM `recruiting`.`vacancy`
    WHERE YEAR(date_open) = %s
    GROUP BY id_struct;
    """

    if request.args.get('return'):
        return redirect(url_for('requests_menu'))

    year = request.form.get('year')

    if year:
        try:
            with UseDatabase(session['db_config']) as cursor:
                keys = ['id_struct', 'unit_vac', 'count']
                values = (year,)

                result = make_request(cursor, _SQL, values, keys)
                return render_template('request1_result.html', report=result, year=year)

        except DatabaseError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось выполнить запрос!")

    return render_template('params_form_enter_year.html', request=1)


@requests_bp.route('/request2', methods=['GET', 'POST'])
@check_role
def request2():
    _SQL = """
        SELECT `co-worker`.*
        FROM `recruiting`.`co-worker`
        JOIN staffing_table ON `co-worker`.id_struct = staffing_table.id_struct
        WHERE unit=%s AND date_dis IS NULL
        ORDER BY birth DESC
        LIMIT 1;
        """

    if request.args.get('return'):
        return redirect(url_for('requests_menu'))

    text = request.form.get('text')

    if text:
        try:
            with UseDatabase(session['db_config']) as cursor:
                keys = ['id_work', 'FName_worker', 'birth', 'address_w', 'educat',
                        'salary', 'date_res', 'date_dis', 'id_struct']
                values = (text,)

                result = make_request(cursor, _SQL, values, keys)
                return render_template('request2_result.html', report=result, text=text)

        except DatabaseError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось записать протокол!")

    return render_template('params_form_enter_depart_name.html', request=2)


@requests_bp.route('/request3', methods=['GET', 'POST'])
@check_role
def request3():
    _SQL = """
        SELECT staffing_table.*
        FROM `recruiting`.`staffing_table`
        LEFT JOIN (SELECT *
            FROM `recruiting`.`vacancy`
            WHERE YEAR(vacancy.date_open) = %s) AS year_vacancy
        ON staffing_table.id_struct = year_vacancy.id_struct
        WHERE year_vacancy.id_struct IS NULL;
        """

    if request.args.get('return'):
        return redirect(url_for('requests_menu'))

    year = request.form.get('year')

    if year:
        try:
            with UseDatabase(session['db_config']) as cursor:
                keys = ['id_struct', 'unit', 'minmax_salary']
                values = (year,)

                result = make_request(cursor, _SQL, values, keys)
                return render_template('request3_result.html', report=result, year=year)

        except DatabaseError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось записать протокол!")

    return render_template('params_form_enter_year.html', request=3)
