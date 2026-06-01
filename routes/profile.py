import os
import uuid
import bleach
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import User, Item, Review, Wishlist, Notification

profile_bp = Blueprint('profile', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


@profile_bp.route('/profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    items = Item.query.filter_by(owner_id=user.id, is_available=True).order_by(Item.created_at.desc()).all()
    reviews = Review.query.filter_by(reviewed_id=user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile/user_profile.html', user=user, items=items, reviews=reviews)


@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.display_name = bleach.clean(request.form.get('display_name', '').strip())
        current_user.bio = bleach.clean(request.form.get('bio', '').strip())
        current_user.location = bleach.clean(request.form.get('location', '').strip())

        avatar = request.files.get('avatar')
        if avatar and avatar.filename and allowed_file(avatar.filename):
            ext = avatar.filename.rsplit('.', 1)[1].lower()
            filename = f"avatar_{uuid.uuid4().hex}.{ext}"
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            avatar.save(path)
            current_user.avatar = filename

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile.user_profile', username=current_user.username))
    return render_template('profile/edit_profile.html')


@profile_bp.route('/my-items')
@login_required
def my_items():
    items = Item.query.filter_by(owner_id=current_user.id).order_by(Item.created_at.desc()).all()
    return render_template('profile/my_items.html', items=items)


@profile_bp.route('/wishlist')
@login_required
def my_wishlist():
    wishlist = Wishlist.query.filter_by(user_id=current_user.id).order_by(Wishlist.created_at.desc()).all()
    return render_template('profile/my_wishlist.html', wishlist=wishlist)


@profile_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    unread = [n for n in notifs if not n.is_read]
    for n in unread:
        n.is_read = True
    db.session.commit()
    return render_template('profile/notifications.html', notifications=notifs)


@profile_bp.route('/leaderboard')
def leaderboard():
    top_traders = User.query.all()
    top_traders = sorted(top_traders, key=lambda u: u.trade_count, reverse=True)[:20]
    return render_template('profile/leaderboard.html', traders=top_traders)
