from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import Item, User, Notification, Wishlist
from extensions import db

api_bp = Blueprint('api', __name__)


@api_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    results = Item.query.filter(
        Item.title.ilike(f'%{q}%'), Item.is_available == True
    ).limit(8).all()
    return jsonify([{
        'id': i.id,
        'title': i.title,
        'image': i.primary_image,
        'condition': i.condition,
        'owner': i.owner.display_name
    } for i in results])


@api_bp.route('/notifications/count')
@login_required
def notif_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


@api_bp.route('/wishlist/toggle/<int:item_id>', methods=['POST'])
@login_required
def wishlist_toggle(item_id):
    item = Item.query.get_or_404(item_id)
    existing = Wishlist.query.filter_by(user_id=current_user.id, item_id=item_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({'wishlisted': False, 'count': item.wishlist_count})
    db.session.add(Wishlist(user_id=current_user.id, item_id=item_id))
    db.session.commit()
    return jsonify({'wishlisted': True, 'count': item.wishlist_count})
