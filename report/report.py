from flask import request, Blueprint, render_template, session, redirect, url_for
from dbcm import UseDatabase
from checker import check_role

report_bp = Blueprint('report_bp', __name__, template_folder='templates')


def proccheck(cursor, l_year):
    _SQL = '''SELECT COUNT(*) FROM report
           WHERE year=%s'''
    cursor.execute(_SQL, (l_year,))
    result = cursor.fetchall()

    return result[0][0]


def get_report(cursor, l_year):
    _SQL = """
        SELECT id_rep, position_id, job_name, openings_count, avg_close_days
        FROM report
        WHERE `year`=%s"""

    keys = ['id_rep', 'id_structure', 'name_vac', 'num_open', 'avg_num_days']

    cursor.execute(_SQL, (l_year,))
    result = cursor.fetchall()

    result = [dict(zip(keys, line)) for line in result]

    return result


@report_bp.route('/report', methods=['GET', 'POST'])
@check_role
def proc():
    year = request.form.get('year')

    if year:
        try:
            with UseDatabase(session['db_config']) as cursor:
                strnum = proccheck(cursor, year)
                if strnum == 0:
                    cursor.callproc('annual_report', (year,))

                result = get_report(cursor, year)
                return render_template('report.html', table=result)

        except ProgrammingError:
            return render_template('error.html', error_msg="Не удалось записать протокол!")
        except InterfaceError:
            return render_template('error.html', error_msg="Ошибка.")
        except DatabaseError:
            return render_template('error.html', error_msg="Не удалось подключиться к базе данных.")



    return render_template('proc.html')
