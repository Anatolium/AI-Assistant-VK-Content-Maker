from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from app.models import User
from app import db
from generators.text_gen import PostGenerator
from generators.image_gen import ImageGenerator
from social_publishers.vk_publisher import VKPublisher
from social_stats.vk_stats import VKStats
from config import OPENAI_API_KEY
import datetime


smm_bp = Blueprint('smm', __name__)


@smm_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')


@smm_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        user.vk_api_id = request.form['vk_api_id']
        user.vk_group_id = request.form['vk_group_id']
        db.session.commit()
        flash('Settings saved!', 'success')

    return render_template('settings.html', user=user)


@smm_bp.route('/post-generator', methods=['GET', 'POST'])
def post_generator():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        tone = request.form['tone']
        topic = request.form['topic']
        generate_image = 'generate_image' in request.form
        auto_post = 'auto_post' in request.form

        user = User.query.get(session['user_id'])

        post_gen = PostGenerator(OPENAI_API_KEY, tone, topic)
        post_content = post_gen.generate_post()

        image_url = None
        if generate_image:
            image_gen = ImageGenerator(OPENAI_API_KEY)
            image_prompt = post_gen.generate_post_image_description()
            image_url = image_gen.generate_image(image_prompt)

        if auto_post:
            vk_publisher = VKPublisher(user.vk_api_id, user.vk_group_id)
            vk_publisher.publish_post(post_content, image_url)
            flash('Post published to VK successfully!', 'success')

        return render_template('post_generator.html', post_content=post_content, image_url=image_url)

    return render_template('post_generator.html')


@smm_bp.route('/vk-stats', methods=['GET'])
def vk_stats():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    vk_stats = VKStats(user.vk_api_id, user.vk_group_id)
    followers_count = vk_stats.get_followers()

    # Получаем статистику за последние 7 дней
    end_date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    try:
        stats_data = vk_stats.get_stats(start_date, end_date)
    except Exception as e:
        stats_data = []
        print("Ошибка при получении статистики VK:", e)

    # Суммируем значения
    total_views = 0
    total_visitors = 0
    total_reach = 0
    total_reach_subs = 0
    total_likes = 0
    total_comments = 0
    total_shares = 0

    for day in stats_data:
        visitors = day.get("visitors", {})
        reach = day.get("reach", {})
        activity = day.get("activity", {})

        total_views += visitors.get("views", 0)
        total_visitors += visitors.get("visitors", 0)
        total_reach += reach.get("reach", 0)
        total_reach_subs += reach.get("reach_subscribers", 0)
        total_likes += activity.get("likes", 0)
        total_comments += activity.get("comments", 0)
        total_shares += activity.get("shares", 0)

    # Собираем данные для вывода
    stats = {
        "Подписчики": followers_count,
        "Просмотры": total_views,
        "Посетители": total_visitors,
        "Охват": total_reach,
        "Охват подписчиков": total_reach_subs,
        "Лайки": total_likes,
        "Комментарии": total_comments,
        "Репосты": total_shares
    }

    return render_template('vk_stats.html', stats=stats)

