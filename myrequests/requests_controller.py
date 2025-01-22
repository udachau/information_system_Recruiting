from flask import Blueprint, render_template, request, session
from dbcm import UseDatabase
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
    """Текущая ситуация по вакансии X."""
    if request.method == 'POST':
        vacancy_name = request.form.get('vacancy_name')

        if not vacancy_name:
            return render_template('error.html', error_msg="Не указано название вакансии!")

        sql = '''
            SELECT 
                o.position_id,
                p.job_name,
                o.open_date,
                o.close_date,
                (SELECT COUNT(*) FROM response WHERE opening_id = o.opening_id) AS candidates_applied,
                (SELECT COUNT(*) FROM interview_details id
                 JOIN interviews i ON id.interview_id = i.interview_id
                 WHERE i.opening_id = o.opening_id) AS interviews_done,
                CASE 
                    WHEN o.close_date IS NULL THEN 'Открыта'
                    ELSE 'Закрыта'
                END AS status
            FROM openings o
            JOIN positions p ON o.position_id = p.position_id
            WHERE p.job_name = %s;
        '''
        keys = ['position_id', 'job_name', 'open_date', 'close_date', 'candidates_applied', 'interviews_done', 'status']

        try:
            with UseDatabase(session['db_config']) as cursor:
                result = make_request(cursor, sql, (vacancy_name,), keys)
                if not result:
                    return render_template('no_data.html')
                return render_template('request1_result.html', table=result)
        except Exception as e:
            return render_template('error.html', error_msg=str(e))

    return render_template('params_form.html', param_name='название вакансии', action_url='/request1')


@requests_bp.route('/request2', methods=['GET', 'POST'])
@check_role
def request2():
    """Анализ эффективности отдела."""
    if request.method == 'POST':
        department_name = request.form.get('department_name')

        if not department_name:
            return render_template('error.html', error_msg="Не указано название отдела!")

        sql = '''
            SELECT 
                p.job_name AS department_name,
                COUNT(e.employee_id) AS employees_count,
                AVG(e.salary) AS avg_salary,
                AVG(YEAR(CURDATE()) - YEAR(e.birth_date)) AS avg_age
            FROM employees e
            JOIN positions p ON e.position_id = p.position_id
            WHERE p.job_name = %s
            GROUP BY p.job_name;
        '''
        keys = ['department_name', 'employees_count', 'avg_salary', 'avg_age']

        try:
            with UseDatabase(session['db_config']) as cursor:
                result = make_request(cursor, sql, (department_name,), keys)
                if not result:
                    return render_template('no_data.html', error_msg="Нет данных для указанного отдела.")
                return render_template('request2_result.html', table=result)
        except Exception as e:
            return render_template('error.html', error_msg=str(e))

    return render_template('params_form_enter_depart_name.html', param_name='название отдела', action_url='/request2')


"""@requests_bp.route('/request3', methods=['GET', 'POST'])
@check_role
def request3():
    
    if request.method == 'POST':
        months = request.form.get('months')

        if not months or not months.isdigit():
            return render_template('error.html', error_msg="Укажите количество месяцев в числовом формате!")

        months = int(months)

        sql = '''
            SELECT 
                p.division_code,
                COUNT(CASE WHEN o.close_date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH) THEN 1 END) AS new_hires,
                COUNT(CASE WHEN o.close_date IS NULL THEN 1 END) AS active_vacancies,
                ROUND(COUNT(CASE WHEN o.close_date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH) THEN 1 END) / %s, 2) AS avg_hires_per_month
            FROM openings o
            JOIN positions p ON o.position_id = p.position_id
            GROUP BY p.division_code;
        '''
        keys = ['division_code', 'new_hires', 'active_vacancies', 'avg_hires_per_month']

        try:
            with UseDatabase(session['db_config']) as cursor:
                result = make_request(cursor, sql, (months, months, months), keys)
                if not result:
                    return render_template('no_data.html')
                return render_template('request3_result.html', table=result)
        except Exception as e:
            return render_template('error.html', error_msg=str(e))

    return render_template('params_form_enter_year.html', param_name='количество месяцев', action_url='/request3') """
