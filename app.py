"""
Главное приложение Flask для системы управления ДиМОС
"""
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from config import config
from models import db, User, Event, Vote, VoteOption, VoteResponse, Document, Project, Task, News, Appeal, Comment

# Создание приложения
app = Flask(__name__)
app.config.from_object(config['development'])

# Инициализация расширений
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице.'

@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя для Flask-Login"""
    return User.query.get(int(user_id))


# Контекстный процессор для глобальных переменных
@app.context_processor
def inject_globals():
    """Добавление глобальных переменных в шаблоны"""
    return {
        'org_name': app.config['ORGANIZATION_NAME'],
        'org_short_name': app.config['ORGANIZATION_SHORT_NAME'],
        'departments': app.config['DEPARTMENTS'],
        'now': datetime.utcnow()
    }


# ============================================================================
# ОСНОВНЫЕ МАРШРУТЫ
# ============================================================================

@app.route('/')
def index():
    """Главная страница"""
    # Последние новости
    latest_news = News.query.filter_by(is_published=True)\
        .order_by(News.published_at.desc()).limit(5).all()

    # Ближайшие мероприятия
    upcoming_events = Event.query.filter(
        Event.start_datetime >= datetime.utcnow(),
        Event.status != 'cancelled'
    ).order_by(Event.start_datetime).limit(5).all()

    # Активные голосования
    active_votes = Vote.query.filter(
        Vote.status == 'active',
        Vote.end_date >= datetime.utcnow()
    ).order_by(Vote.end_date).limit(3).all()

    return render_template('index.html',
                         latest_news=latest_news,
                         upcoming_events=upcoming_events,
                         active_votes=active_votes)


@app.route('/dashboard')
@login_required
def dashboard():
    """Личный кабинет"""
    # Статистика пользователя
    user_stats = {
        'events_count': current_user.events.count(),
        'projects_count': current_user.projects.count(),
        'votes_participated': current_user.vote_responses.count(),
        'documents_uploaded': current_user.documents.count()
    }

    # Ближайшие мероприятия пользователя
    user_events = current_user.events.filter(
        Event.start_datetime >= datetime.utcnow()
    ).order_by(Event.start_datetime).limit(5).all()

    # Задачи пользователя
    user_tasks = Task.query.filter(
        Task.assignee_id == current_user.id,
        Task.status.in_(['todo', 'in_progress'])
    ).order_by(Task.due_date).limit(10).all()

    return render_template('dashboard.html',
                         stats=user_stats,
                         events=user_events,
                         tasks=user_tasks)


# ============================================================================
# АУТЕНТИФИКАЦИЯ
# ============================================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Ваш аккаунт деактивирован. Обратитесь к администратору.', 'danger')
                return redirect(url_for('login'))

            login_user(user, remember=remember)
            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        patronymic = request.form.get('patronymic')
        phone = request.form.get('phone')
        department = request.form.get('department') or None

        # Проверка существования пользователя
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'danger')
            return redirect(url_for('register'))

        # Создание нового пользователя
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            patronymic=patronymic,
            phone=phone,
            department=department,
            role='member'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Теперь вы можете войти в систему.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')


# ============================================================================
# МЕРОПРИЯТИЯ
# ============================================================================

@app.route('/events')
@login_required
def events_list():
    """Список мероприятий"""
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.start_datetime.desc())\
        .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('events/list.html', events=events)


@app.route('/events/<int:event_id>')
@login_required
def event_detail(event_id):
    """Детали мероприятия"""
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)


@app.route('/events/create', methods=['GET', 'POST'])
@login_required
def event_create():
    """Создание мероприятия"""
    if current_user.role not in ['admin', 'chairman', 'secretary']:
        flash('У вас нет прав для создания мероприятий', 'danger')
        return redirect(url_for('events_list'))

    if request.method == 'POST':
        event = Event(
            title=request.form.get('title'),
            description=request.form.get('description'),
            start_datetime=datetime.fromisoformat(request.form.get('start_datetime')),
            end_datetime=datetime.fromisoformat(request.form.get('end_datetime')) if request.form.get('end_datetime') else None,
            location=request.form.get('location'),
            online_link=request.form.get('online_link'),
            event_type=request.form.get('event_type'),
            creator_id=current_user.id
        )
        db.session.add(event)
        db.session.commit()

        flash('Мероприятие успешно создано', 'success')
        return redirect(url_for('event_detail', event_id=event.id))

    return render_template('events/create.html')


# ============================================================================
# ГОЛОСОВАНИЯ
# ============================================================================

@app.route('/votes')
@login_required
def votes_list():
    """Список голосований"""
    page = request.args.get('page', 1, type=int)
    votes = Vote.query.filter(Vote.status != 'draft')\
        .order_by(Vote.created_at.desc())\
        .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('votes/list.html', votes=votes)


@app.route('/votes/<int:vote_id>')
@login_required
def vote_detail(vote_id):
    """Детали голосования"""
    vote = Vote.query.get_or_404(vote_id)
    user_response = VoteResponse.query.filter_by(
        vote_id=vote_id,
        user_id=current_user.id
    ).first()
    return render_template('votes/detail.html', vote=vote, user_response=user_response)


@app.route('/votes/<int:vote_id>/vote', methods=['POST'])
@login_required
def vote_submit(vote_id):
    """Отправка голоса"""
    vote = Vote.query.get_or_404(vote_id)

    if vote.status != 'active':
        flash('Голосование неактивно', 'danger')
        return redirect(url_for('vote_detail', vote_id=vote_id))

    if datetime.utcnow() > vote.end_date:
        flash('Голосование завершено', 'danger')
        return redirect(url_for('vote_detail', vote_id=vote_id))

    # Проверка, голосовал ли уже пользователь
    existing_response = VoteResponse.query.filter_by(
        vote_id=vote_id,
        user_id=current_user.id
    ).first()

    if existing_response:
        flash('Вы уже проголосовали', 'warning')
        return redirect(url_for('vote_detail', vote_id=vote_id))

    option_id = request.form.get('option_id')
    comment = request.form.get('comment')

    response = VoteResponse(
        vote_id=vote_id,
        user_id=current_user.id,
        option_id=option_id,
        comment=comment
    )
    db.session.add(response)
    db.session.commit()

    flash('Ваш голос учтен', 'success')
    return redirect(url_for('vote_detail', vote_id=vote_id))


# ============================================================================
# ПРОЕКТЫ
# ============================================================================

@app.route('/projects')
@login_required
def projects_list():
    """Список проектов"""
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.created_at.desc())\
        .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('projects/list.html', projects=projects)


@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """Детали проекта"""
    project = Project.query.get_or_404(project_id)
    tasks = project.tasks.order_by(Task.created_at.desc()).all()
    return render_template('projects/detail.html', project=project, tasks=tasks)


# ============================================================================
# ДОКУМЕНТЫ
# ============================================================================

@app.route('/documents')
@login_required
def documents_list():
    """Список документов"""
    page = request.args.get('page', 1, type=int)
    documents = Document.query.order_by(Document.created_at.desc())\
        .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('documents/list.html', documents=documents)


def allowed_file(filename):
    """Проверка допустимого расширения файла"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/documents/upload', methods=['GET', 'POST'])
@login_required
def document_upload():
    """Загрузка документа"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Добавляем timestamp к имени файла для уникальности
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"

            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            document = Document(
                title=request.form.get('title'),
                description=request.form.get('description'),
                filename=filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                category=request.form.get('category'),
                uploader_id=current_user.id
            )
            db.session.add(document)
            db.session.commit()

            flash('Документ успешно загружен', 'success')
            return redirect(url_for('documents_list'))
        else:
            flash('Недопустимый тип файла', 'danger')

    return render_template('documents/upload.html')


# ============================================================================
# НОВОСТИ
# ============================================================================

@app.route('/news')
def news_list():
    """Список новостей"""
    page = request.args.get('page', 1, type=int)
    news = News.query.filter_by(is_published=True)\
        .order_by(News.published_at.desc())\
        .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    return render_template('news/list.html', news=news)


@app.route('/news/<int:news_id>')
def news_detail(news_id):
    """Детали новости"""
    news_item = News.query.get_or_404(news_id)
    if not news_item.is_published and not (current_user.is_authenticated and current_user.role == 'admin'):
        flash('Новость не опубликована', 'danger')
        return redirect(url_for('news_list'))

    # Увеличиваем счетчик просмотров
    news_item.views_count += 1
    db.session.commit()

    comments = news_item.comments.order_by(Comment.created_at.desc()).all()
    return render_template('news/detail.html', news=news_item, comments=comments)


# ============================================================================
# ОБРАЩЕНИЯ
# ============================================================================

@app.route('/appeals')
@login_required
def appeals_list():
    """Список обращений"""
    page = request.args.get('page', 1, type=int)

    if current_user.role in ['admin', 'chairman']:
        # Админы и председатели видят все обращения
        appeals = Appeal.query.order_by(Appeal.created_at.desc())\
            .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)
    else:
        # Обычные пользователи видят только свои обращения
        appeals = Appeal.query.filter_by(author_id=current_user.id)\
            .order_by(Appeal.created_at.desc())\
            .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)

    return render_template('appeals/list.html', appeals=appeals)


@app.route('/appeals/create', methods=['GET', 'POST'])
def appeal_create():
    """Создание обращения"""
    if request.method == 'POST':
        appeal = Appeal(
            title=request.form.get('title'),
            content=request.form.get('content'),
            category=request.form.get('category'),
            author_id=current_user.id if current_user.is_authenticated else None,
            contact_name=request.form.get('contact_name'),
            contact_email=request.form.get('contact_email'),
            contact_phone=request.form.get('contact_phone')
        )
        db.session.add(appeal)
        db.session.commit()

        flash('Ваше обращение принято и будет рассмотрено', 'success')
        return redirect(url_for('index'))

    return render_template('appeals/create.html')


# ============================================================================
# ПРОФИЛЬ
# ============================================================================

@app.route('/profile')
@login_required
def profile():
    """Профиль пользователя"""
    return render_template('profile/view.html', user=current_user)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def profile_edit():
    """Редактирование профиля"""
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.patronymic = request.form.get('patronymic')
        current_user.phone = request.form.get('phone')
        current_user.department = request.form.get('department') or None
        current_user.bio = request.form.get('bio')

        db.session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('profile'))

    return render_template('profile/edit.html')


# ============================================================================
# АДМИНИСТРАТИВНЫЕ ФУНКЦИИ
# ============================================================================

@app.route('/admin')
@login_required
def admin_panel():
    """Административная панель"""
    if current_user.role != 'admin':
        flash('У вас нет доступа к административной панели', 'danger')
        return redirect(url_for('dashboard'))

    stats = {
        'users_count': User.query.count(),
        'events_count': Event.query.count(),
        'projects_count': Project.query.count(),
        'documents_count': Document.query.count(),
        'appeals_count': Appeal.query.count()
    }

    # Статистика по отделам
    dept_stats = {}
    for dept_key, dept_name in app.config['DEPARTMENTS'].items():
        dept_stats[dept_name] = User.query.filter_by(department=dept_key).count()

    return render_template('admin/panel.html', stats=stats, dept_stats=dept_stats)


@app.route('/admin/users')
@login_required
def admin_users():
    """Список пользователей для администратора"""
    if current_user.role != 'admin':
        flash('У вас нет доступа к этой странице', 'danger')
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    department_filter = request.args.get('department')

    # Базовый запрос
    query = User.query

    # Фильтрация по отделу
    if department_filter:
        query = query.filter_by(department=department_filter)

    users = query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False)

    return render_template('admin/users.html', users=users, department_filter=department_filter)


# ============================================================================
# АДМИНИСТРАТИВНОЕ РЕДАКТИРОВАНИЕ
# ============================================================================

@app.route('/admin/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_event_edit(event_id):
    """Редактирование мероприятия (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для редактирования мероприятий', 'danger')
        return redirect(url_for('events_list'))

    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.description = request.form.get('description')
        event.start_datetime = datetime.fromisoformat(request.form.get('start_datetime'))
        event.end_datetime = datetime.fromisoformat(request.form.get('end_datetime')) if request.form.get('end_datetime') else None
        event.location = request.form.get('location')
        event.online_link = request.form.get('online_link')
        event.event_type = request.form.get('event_type')
        event.status = request.form.get('status', 'planned')

        db.session.commit()
        flash('Мероприятие успешно обновлено', 'success')
        return redirect(url_for('event_detail', event_id=event.id))

    return render_template('admin/event_edit.html', event=event)


@app.route('/admin/events/<int:event_id>/delete', methods=['POST'])
@login_required
def admin_event_delete(event_id):
    """Удаление мероприятия (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для удаления мероприятий', 'danger')
        return redirect(url_for('events_list'))

    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()

    flash('Мероприятие успешно удалено', 'success')
    return redirect(url_for('events_list'))


@app.route('/admin/votes/<int:vote_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_vote_edit(vote_id):
    """Редактирование голосования (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для редактирования голосований', 'danger')
        return redirect(url_for('votes_list'))

    vote = Vote.query.get_or_404(vote_id)

    if request.method == 'POST':
        vote.title = request.form.get('title')
        vote.description = request.form.get('description')
        vote.start_datetime = datetime.fromisoformat(request.form.get('start_datetime'))
        vote.end_datetime = datetime.fromisoformat(request.form.get('end_datetime'))
        vote.status = request.form.get('status', 'active')
        vote.is_anonymous = request.form.get('is_anonymous') == 'on'
        vote.is_public = request.form.get('is_public') == 'on'

        db.session.commit()
        flash('Голосование успешно обновлено', 'success')
        return redirect(url_for('vote_detail', vote_id=vote.id))

    return render_template('admin/vote_edit.html', vote=vote)


@app.route('/admin/votes/<int:vote_id>/delete', methods=['POST'])
@login_required
def admin_vote_delete(vote_id):
    """Удаление голосования (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для удаления голосований', 'danger')
        return redirect(url_for('votes_list'))

    vote = Vote.query.get_or_404(vote_id)

    # Удаляем связанные ответы и опции
    VoteResponse.query.filter_by(vote_id=vote_id).delete()
    VoteOption.query.filter_by(vote_id=vote_id).delete()

    db.session.delete(vote)
    db.session.commit()

    flash('Голосование успешно удалено', 'success')
    return redirect(url_for('votes_list'))


@app.route('/admin/news/<int:news_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_news_edit(news_id):
    """Редактирование новости (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для редактирования новостей', 'danger')
        return redirect(url_for('news_list'))

    news = News.query.get_or_404(news_id)

    if request.method == 'POST':
        news.title = request.form.get('title')
        news.summary = request.form.get('summary')
        news.content = request.form.get('content')
        news.is_important = request.form.get('is_important') == 'on'

        db.session.commit()
        flash('Новость успешно обновлена', 'success')
        return redirect(url_for('news_detail', news_id=news.id))

    return render_template('admin/news_edit.html', news=news)


@app.route('/admin/news/<int:news_id>/delete', methods=['POST'])
@login_required
def admin_news_delete(news_id):
    """Удаление новости (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для удаления новостей', 'danger')
        return redirect(url_for('news_list'))

    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()

    flash('Новость успешно удалена', 'success')
    return redirect(url_for('news_list'))


@app.route('/admin/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_project_edit(project_id):
    """Редактирование проекта (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для редактирования проектов', 'danger')
        return redirect(url_for('projects_list'))

    project = Project.query.get_or_404(project_id)

    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.status = request.form.get('status', 'planning')
        project.start_date = datetime.fromisoformat(request.form.get('start_date')).date() if request.form.get('start_date') else None
        project.end_date = datetime.fromisoformat(request.form.get('end_date')).date() if request.form.get('end_date') else None

        db.session.commit()
        flash('Проект успешно обновлен', 'success')
        return redirect(url_for('project_detail', project_id=project.id))

    return render_template('admin/project_edit.html', project=project)


@app.route('/admin/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def admin_project_delete(project_id):
    """Удаление проекта (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для удаления проектов', 'danger')
        return redirect(url_for('projects_list'))

    project = Project.query.get_or_404(project_id)

    # Удаляем связанные задачи
    Task.query.filter_by(project_id=project_id).delete()

    db.session.delete(project)
    db.session.commit()

    flash('Проект успешно удален', 'success')
    return redirect(url_for('projects_list'))


@app.route('/admin/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_user_edit(user_id):
    """Редактирование пользователя (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для редактирования пользователей', 'danger')
        return redirect(url_for('dashboard'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.email = request.form.get('email')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.patronymic = request.form.get('patronymic')
        user.role = request.form.get('role')
        user.department = request.form.get('department')
        user.is_active = request.form.get('is_active') == 'on'

        # Если задан новый пароль
        if request.form.get('new_password'):
            user.set_password(request.form.get('new_password'))

        db.session.commit()
        flash('Пользователь успешно обновлен', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin/user_edit.html', user=user)


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_user_delete(user_id):
    """Удаление пользователя (только админ)"""
    if current_user.role != 'admin':
        flash('У вас нет прав для удаления пользователей', 'danger')
        return redirect(url_for('dashboard'))

    if user_id == current_user.id:
        flash('Вы не можете удалить свой собственный аккаунт', 'danger')
        return redirect(url_for('admin_users'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    flash('Пользователь успешно удален', 'success')
    return redirect(url_for('admin_users'))


# ============================================================================
# ОБРАБОТЧИКИ ОШИБОК
# ============================================================================

@app.errorhandler(404)
def not_found_error(error):
    """Обработчик ошибки 404"""
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """Обработчик ошибки 500"""
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ============================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ============================================================================

if __name__ == '__main__':
    with app.app_context():
        # Создание директории для загрузок
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000)
