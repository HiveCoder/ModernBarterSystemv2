import os
import uuid
import bleach
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Item, ItemImage, ItemTag, Category, Wishlist, Notification, User

items_bp = Blueprint('items', __name__)

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def save_image(file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(path)
    return filename


@items_bp.route('/items/new', methods=['GET', 'POST'])
@login_required
def new_item():
    categories = Category.query.all()
    if request.method == 'POST':
        title = bleach.clean(request.form.get('title', '').strip())
        description = bleach.clean(request.form.get('description', '').strip())
        condition = request.form.get('condition', 'good')
        category_id = request.form.get('category_id', type=int)
        estimated_value = request.form.get('estimated_value', type=float)
        location = bleach.clean(request.form.get('location', '').strip())
        trade_type = request.form.get('trade_type', 'trade')
        looking_for = bleach.clean(request.form.get('looking_for', '').strip())
        tags_raw = bleach.clean(request.form.get('tags', '').strip())

        if not title or not description:
            flash('Title and description are required.', 'danger')
            return render_template('items/new_item.html', categories=categories)

        item = Item(
            title=title, description=description, condition=condition,
            category_id=category_id, estimated_value=estimated_value,
            location=location or current_user.location,
            trade_type=trade_type, looking_for=looking_for,
            owner_id=current_user.id
        )
        db.session.add(item)
        db.session.flush()

        # Handle images
        images = request.files.getlist('images')
        first = True
        for img in images:
            if img and img.filename and allowed_file(img.filename):
                fname = save_image(img)
                db.session.add(ItemImage(item_id=item.id, filename=fname, is_primary=first))
                first = False

        # Handle tags
        if tags_raw:
            for tag in [t.strip() for t in tags_raw.split(',') if t.strip()][:8]:
                db.session.add(ItemTag(item_id=item.id, tag=tag[:30]))

        db.session.commit()
        flash('Item listed successfully!', 'success')
        return redirect(url_for('items.item_detail', item_id=item.id))
    return render_template('items/new_item.html', categories=categories)


@items_bp.route('/items/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    item.view_count += 1
    db.session.commit()
    is_wishlisted = False
    if current_user.is_authenticated:
        is_wishlisted = Wishlist.query.filter_by(user_id=current_user.id, item_id=item_id).first() is not None
    similar_items = Item.query.filter(
        Item.category_id == item.category_id,
        Item.id != item_id,
        Item.is_available == True
    ).limit(4).all()
    return render_template('items/item_detail.html', item=item, is_wishlisted=is_wishlisted, similar_items=similar_items)


@items_bp.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner_id != current_user.id:
        abort(403)
    categories = Category.query.all()
    if request.method == 'POST':
        item.title = bleach.clean(request.form.get('title', '').strip())
        item.description = bleach.clean(request.form.get('description', '').strip())
        item.condition = request.form.get('condition', 'good')
        item.category_id = request.form.get('category_id', type=int)
        item.estimated_value = request.form.get('estimated_value', type=float)
        item.location = bleach.clean(request.form.get('location', '').strip())
        item.trade_type = request.form.get('trade_type', 'trade')
        item.looking_for = bleach.clean(request.form.get('looking_for', '').strip())
        item.is_available = bool(request.form.get('is_available'))

        images = request.files.getlist('images')
        has_primary = item.images.filter_by(is_primary=True).first() is not None
        for img in images:
            if img and img.filename and allowed_file(img.filename):
                fname = save_image(img)
                db.session.add(ItemImage(item_id=item.id, filename=fname, is_primary=not has_primary))
                has_primary = True

        # Refresh tags
        ItemTag.query.filter_by(item_id=item.id).delete()
        tags_raw = bleach.clean(request.form.get('tags', '').strip())
        if tags_raw:
            for tag in [t.strip() for t in tags_raw.split(',') if t.strip()][:8]:
                db.session.add(ItemTag(item_id=item.id, tag=tag[:30]))

        db.session.commit()
        flash('Item updated!', 'success')
        return redirect(url_for('items.item_detail', item_id=item.id))
    return render_template('items/edit_item.html', item=item, categories=categories)


@items_bp.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner_id != current_user.id:
        abort(403)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted.', 'info')
    return redirect(url_for('profile.my_items'))


@items_bp.route('/items/<int:item_id>/wishlist', methods=['POST'])
@login_required
def toggle_wishlist(item_id):
    item = Item.query.get_or_404(item_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return {'wishlisted': False, 'count': item.wishlist_count}
    else:
        db.session.add(Wishlist(user_id=current_user.id, item_id=item_id))
        db.session.commit()
        return {'wishlisted': True, 'count': item.wishlist_count}
