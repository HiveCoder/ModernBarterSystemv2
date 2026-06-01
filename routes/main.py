from flask import Blueprint, render_template, request
from flask_login import current_user
from models import Item, User, Category, TradeOffer
from extensions import db
from sqlalchemy import or_, func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    featured_items = Item.query.filter_by(is_available=True, is_featured=True).order_by(Item.created_at.desc()).limit(8).all()
    recent_items = Item.query.filter_by(is_available=True).order_by(Item.created_at.desc()).limit(12).all()
    categories = Category.query.all()
    total_users = User.query.count()
    total_items = Item.query.filter_by(is_available=True).count()
    total_trades = TradeOffer.query.filter_by(status='completed').count()
    return render_template('main/index.html',
                           featured_items=featured_items,
                           recent_items=recent_items,
                           categories=categories,
                           stats={'users': total_users, 'items': total_items, 'trades': total_trades})


@main_bp.route('/marketplace')
def marketplace():
    page = request.args.get('page', 1, type=int)
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category', type=int)
    condition = request.args.get('condition', '')
    sort = request.args.get('sort', 'newest')
    trade_type = request.args.get('trade_type', '')
    location = request.args.get('location', '').strip()
    min_val = request.args.get('min_val', type=float)
    max_val = request.args.get('max_val', type=float)

    query = Item.query.filter_by(is_available=True)

    if q:
        search = f'%{q}%'
        query = query.filter(or_(Item.title.ilike(search), Item.description.ilike(search),
                                 Item.looking_for.ilike(search)))
    if category_id:
        query = query.filter_by(category_id=category_id)
    if condition:
        query = query.filter_by(condition=condition)
    if trade_type:
        query = query.filter_by(trade_type=trade_type)
    if location:
        query = query.filter(Item.location.ilike(f'%{location}%'))
    if min_val is not None:
        query = query.filter(Item.estimated_value >= min_val)
    if max_val is not None:
        query = query.filter(Item.estimated_value <= max_val)

    if sort == 'oldest':
        query = query.order_by(Item.created_at.asc())
    elif sort == 'value_high':
        query = query.order_by(Item.estimated_value.desc())
    elif sort == 'value_low':
        query = query.order_by(Item.estimated_value.asc())
    elif sort == 'popular':
        query = query.order_by(Item.view_count.desc())
    elif sort == 'wishlist':
        query = query.outerjoin(Item.wishlisters).group_by(Item.id).order_by(func.count().desc())
    else:
        query = query.order_by(Item.created_at.desc())

    items = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    return render_template('main/marketplace.html', items=items, categories=categories,
                           q=q, category_id=category_id, condition=condition,
                           sort=sort, trade_type=trade_type, location=location,
                           min_val=min_val, max_val=max_val)


@main_bp.route('/about')
def about():
    return render_template('main/about.html')


@main_bp.route('/how-it-works')
def how_it_works():
    return render_template('main/how_it_works.html')
