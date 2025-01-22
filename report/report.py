import os
import json
from flask import Blueprint, render_template, request, session, redirect, url_for
from dbcm import UseDatabase
from datetime import datetime
from sql_provider import SQLProvider
from checker import check_role

# Инициализация Blueprint
report_bp = Blueprint('report_bp', __name__, template_folder='templates')
provider = SQLProvider('report/sql')

# Пути к файлам конфигурации
config_path = os.path.join('data_files', 'reports_config.json')
permissions_path = os.path.join('data_files', 'role_permissions.json')

# Загрузка конфигурации
with open(config_path, 'r', encoding='utf-8') as f:
    REPORTS_CONFIG = json.load(f)

with open(permissions_path, 'r', encoding='utf-8') as f:
    ROLE_PERMISSIONS = json.load(f)

# Проверка корректности интервала
def validate_date_interval(start_date, end_date):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        if start > end:
            return False, "Дата начала не может быть позже даты окончания."
        if (end.year - start.year) * 12 + end.month - start.month < 1:
            return False, "Интервал должен быть не менее одного месяца."
        return True, None
    except ValueError:
        return False, "Некорректный формат даты."

# Маршрут: Список доступных отчётов
@report_bp.route('/report', methods=['GET', 'POST'])
@check_role
def list_reports():
    """
    Отображение списка всех доступных типов отчётов с формами для выбора дат
    и кнопками "Посмотреть" и "Создать".
    """
    role = session['db_config']['user']
    if not role:
        return render_template('error.html', error_msg="Роль пользователя не определена.")
    
    available_reports = []
    for key, config in REPORTS_CONFIG.items():
        permissions = ROLE_PERMISSIONS.get(role, {})
        can_view = permissions.get('can_view', False)
        can_create = permissions.get('can_create', False)
        if can_view or can_create:
            available_reports.append({
                'report_type': key,
                'name': config['name'],
                'can_view': can_view,
                'can_create': can_create
            })

    return render_template('report_list.html', reports=available_reports, can_view=can_view, can_create=can_create)

@report_bp.route('/report/<report_type>/create', methods=['POST'])
@check_role
def create_report(report_type):
    """
    Создание отчета за указанный временной интервал.
    """
    config = REPORTS_CONFIG.get(report_type)
    if not config:
        return render_template('error.html', error_msg="Некорректный тип отчета.")
    
    role = session['db_config']['user']
    if not ROLE_PERMISSIONS.get(role, {}).get('can_create'):
        return render_template('error.html', error_msg="У вас нет прав для создания отчёта.")

    # Получение дат из формы
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    # Проверка корректности интервала
    valid, error_msg = validate_date_interval(start_date, end_date)
    if not valid:
        return render_template('error.html', error_msg=error_msg)

    # Формирование интервала дат
    date_range = f"{start_date} - {end_date}"

    with UseDatabase(session['db_config']) as cursor:
        # Проверка существования отчёта
        query_check = provider.get('check_report.sql')
        cursor.execute(query_check, (date_range,))
        if cursor.fetchone()[0] > 0:
            return render_template('error.html', error_msg="Отчёт за указанный интервал уже существует.")

        # Генерация отчёта через процедуру
        procedure = config['create_procedure']
        query_create = f"CALL {procedure}(%s, %s);"
        cursor.execute(query_create, (start_date, end_date))

    # Сообщение об успешном создании
    success_msg = f"Отчёт за период {start_date} - {end_date} успешно создан."
    return render_template('success.html', message=success_msg)

@report_bp.route('/report/<report_type>/view', methods=['GET'])
@check_role
def view_report(report_type):
    """
    Просмотр отчета за указанный временной интервал.
    """
    config = REPORTS_CONFIG.get(report_type)
    if not config:
        return render_template('error.html', error_msg="Некорректный тип отчета.")

    role = session['db_config']['user']
    if not ROLE_PERMISSIONS.get(role, {}).get('can_view'):
        return render_template('error.html', error_msg="У вас нет прав для просмотра отчёта.")

    # Получение дат из параметров запроса
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Проверка корректности интервала
    valid, error_msg = validate_date_interval(start_date, end_date)
    if not valid:
        return render_template('error.html', error_msg=error_msg)

    # Формирование интервала дат
    date_range = f"{start_date} - {end_date}"

    with UseDatabase(session['db_config']) as cursor:
        # Проверка существования отчёта
        query_check = provider.get('check_report.sql')
        cursor.execute(query_check, (date_range,))
        if cursor.fetchone()[0] == 0:
            return render_template('error.html', error_msg="Отчёт за указанный период не существует. Сначала создайте отчёт.")

        # Получение данных отчёта
        query_view = config['view_query']
        cursor.execute(query_view, (date_range,))
        report_data = cursor.fetchall()

        return render_template(config['template'], data=report_data, start_date=start_date, end_date=end_date)
