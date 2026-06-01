from datetime import datetime
from flask_login import UserMixin
from extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    display_name = db.Column(db.String(60))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    avatar = db.Column(db.String(200), default='default_avatar.png')
    trade_credits = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('Item', backref='owner', lazy='dynamic', foreign_keys='Item.owner_id')
    sent_offers = db.relationship('TradeOffer', backref='sender', lazy='dynamic', foreign_keys='TradeOffer.sender_id')
    received_offers = db.relationship('TradeOffer', backref='receiver', lazy='dynamic', foreign_keys='TradeOffer.receiver_id')
    sent_messages = db.relationship('Message', backref='author', lazy='dynamic', foreign_keys='Message.sender_id')
    given_reviews = db.relationship('Review', backref='reviewer', lazy='dynamic', foreign_keys='Review.reviewer_id')
    received_reviews = db.relationship('Review', backref='reviewed', lazy='dynamic', foreign_keys='Review.reviewed_id')
    wishlisted_items = db.relationship('Wishlist', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    @property
    def average_rating(self):
        reviews = Review.query.filter_by(reviewed_id=self.id).all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)

    @property
    def trade_count(self):
        return TradeOffer.query.filter(
            ((TradeOffer.sender_id == self.id) | (TradeOffer.receiver_id == self.id)),
            TradeOffer.status == 'completed'
        ).count()

    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='fa-tag')
    description = db.Column(db.String(200))
    items = db.relationship('Item', backref='category', lazy='dynamic')


class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    condition = db.Column(db.String(20), nullable=False)  # new, like_new, good, fair, poor
    estimated_value = db.Column(db.Float)
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    trade_type = db.Column(db.String(20), default='trade')  # trade, sell, gift
    looking_for = db.Column(db.Text)  # what the owner wants in return
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    images = db.relationship('ItemImage', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    tags = db.relationship('ItemTag', backref='item', lazy='dynamic', cascade='all, delete-orphan')
    wishlisters = db.relationship('Wishlist', backref='item', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def primary_image(self):
        img = self.images.filter_by(is_primary=True).first()
        if img:
            return img.filename
        first = self.images.first()
        return first.filename if first else 'no_image.png'

    @property
    def wishlist_count(self):
        return self.wishlisters.count()


class ItemImage(db.Model):
    __tablename__ = 'item_images'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    is_primary = db.Column(db.Boolean, default=False)


class ItemTag(db.Model):
    __tablename__ = 'item_tags'
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    tag = db.Column(db.String(30), nullable=False)


class TradeOffer(db.Model):
    __tablename__ = 'trade_offers'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    offered_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    requested_item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined, countered, completed, cancelled
    counter_offer_id = db.Column(db.Integer, db.ForeignKey('trade_offers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    offered_item = db.relationship('Item', foreign_keys=[offered_item_id])
    requested_item = db.relationship('Item', foreign_keys=[requested_item_id])
    messages = db.relationship('Message', backref='trade', lazy='dynamic')


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    trade_offer_id = db.Column(db.Integer, db.ForeignKey('trade_offers.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewed_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trade_offer_id = db.Column(db.Integer, db.ForeignKey('trade_offers.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text)
    link = db.Column(db.String(200))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
