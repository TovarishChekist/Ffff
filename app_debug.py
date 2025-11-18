"""
ВРЕМЕННОЕ ПРИЛОЖЕНИЕ ДЛЯ ОТЛАДКИ
⚠️ НЕ ИСПОЛЬЗУЙТЕ В ПРОДАКШЕНЕ!
⚠️ ТОЛЬКО ДЛЯ ЛОКАЛЬНОГО ТЕСТИРОВАНИЯ!

Это версия без проверки входа в систему.
"""
import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Контекстный процессор
@app.context_processor
def inject_globals():
    # В режиме отладки всегда используем первого админа
    admin = User.query.filter_by(role='admin').first()
    return {
        'org_name': app.config['ORGANIZATION_NAME'],
        'org_short_name': app.config['ORGANIZATION_SHORT_NAME'],
        'departments': app.config['DEPARTMENTS'],
        'now': datetime.utcnow(),
        'current_user': admin if admin else None
    }

# ГЛАВНАЯ
@app.route('/')
def index():
    latest_news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(5).all()
    upcoming_events = Event.query.filter(Event.start_datetime >= datetime.utcnow()).order_by(Event.start_datetime).limit(5).all()
    active_votes = Vote.query.filter(Vote.status == 'active').limit(3).all()
    return render_template('index.html', latest_news=latest_news, upcoming_events=upcoming_events, active_votes=active_votes)

# АДМИНКА (БЕЗ ПРОВЕРКИ ВХОДА!)
@app.route('/admin')
def admin_panel():
    stats = {
        'users_count': User.query.count(),
        'events_count': Event.query.count(),
        'projects_count': Project.query.count(),
        'documents_count': Document.query.count(),
        'appeals_count': Appeal.query.count()
    }
    dept_stats = {}
    for dept_key, dept_name in app.config['DEPARTMENTS'].items():
        dept_stats[dept_name] = User.query.filter_by(department=dept_key).count()
    return render_template('admin/panel.html', stats=stats, dept_stats=dept_stats)

@app.route('/admin/users')
def admin_users():
    page = request.args.get('page', 1, type=int)
    department_filter = request.args.get('department')
    query = User.query
    if department_filter:
        query = query.filter_by(department=department_filter)
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('admin/users.html', users=users, department_filter=department_filter)

# СОБЫТИЯ
@app.route('/events')
def events_list():
    page = request.args.get('page', 1, type=int)
    events = Event.query.order_by(Event.start_datetime.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('events/list.html', events=events)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('events/detail.html', event=event)

# ПРОЕКТЫ
@app.route('/projects')
def projects_list():
    page = request.args.get('page', 1, type=int)
    projects = Project.query.order_by(Project.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('projects/list.html', projects=projects)

@app.route('/projects/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    tasks = project.tasks.order_by(Task.created_at.desc()).all()
    return render_template('projects/detail.html', project=project, tasks=tasks)

# НОВОСТИ
@app.route('/news')
def news_list():
    page = request.args.get('page', 1, type=int)
    news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('news/list.html', news=news)

@app.route('/news/<int:news_id>')
def news_detail(news_id):
    news_item = News.query.get_or_404(news_id)
    news_item.views_count += 1
    db.session.commit()
    comments = news_item.comments.order_by(Comment.created_at.desc()).all()
    return render_template('news/detail.html', news=news_item, comments=comments)

# ДОКУМЕНТЫ
@app.route('/documents')
def documents_list():
    page = request.args.get('page', 1, type=int)
    documents = Document.query.order_by(Document.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('documents/list.html', documents=documents)

# ОБРАЩЕНИЯ
@app.route('/appeals')
def appeals_list():
    page = request.args.get('page', 1, type=int)
    appeals = Appeal.query.order_by(Appeal.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('appeals/list.html', appeals=appeals)

@app.route('/appeals/create', methods=['GET', 'POST'])
def appeal_create():
    if request.method == 'POST':
        appeal = Appeal(
            title=request.form.get('title'),
            content=request.form.get('content'),
            category=request.form.get('category'),
            contact_name=request.form.get('contact_name'),
            contact_email=request.form.get('contact_email'),
            contact_phone=request.form.get('contact_phone')
        )
        db.session.add(appeal)
        db.session.commit()
        flash('Ваше обращение принято', 'success')
        return redirect(url_for('index'))
    return render_template('appeals/create.html')

# ГОЛОСОВАНИЯ
@app.route('/votes')
def votes_list():
    page = request.args.get('page', 1, type=int)
    votes = Vote.query.filter(Vote.status != 'draft').order_by(Vote.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template('votes/list.html', votes=votes)

@app.route('/votes/<int:vote_id>')
def vote_detail(vote_id):
    vote = Vote.query.get_or_404(vote_id)
    return render_template('votes/detail.html', vote=vote, user_response=None)

# ОШИБКИ
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    print("\n" + "="*60)
    print("⚠️  РЕЖИМ ОТЛАДКИ - БЕЗ ПРОВЕРКИ ВХОДА!")
    print("="*60)
    print("Доступ к админке: http://localhost:5000/admin")
    print("⚠️  НЕ ИСПОЛЬЗУЙТЕ В ПРОДАКШЕНЕ!")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
