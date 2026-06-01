import bleach
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import TradeOffer, Item, Notification, Review, User

trades_bp = Blueprint('trades', __name__)


def _notify(user_id, title, body, link=None):
    db.session.add(Notification(user_id=user_id, title=title, body=body, link=link))


@trades_bp.route('/trade/offer/<int:item_id>', methods=['GET', 'POST'])
@login_required
def make_offer(item_id):
    requested_item = Item.query.get_or_404(item_id)
    if requested_item.owner_id == current_user.id:
        flash("You can't trade with yourself.", 'warning')
        return redirect(url_for('items.item_detail', item_id=item_id))

    my_items = Item.query.filter_by(owner_id=current_user.id, is_available=True).all()
    if not my_items:
        flash('You need to list an item before making a trade offer.', 'warning')
        return redirect(url_for('items.new_item'))

    if request.method == 'POST':
        offered_item_id = request.form.get('offered_item_id', type=int)
        message = bleach.clean(request.form.get('message', '').strip())

        offered_item = Item.query.get(offered_item_id)
        if not offered_item or offered_item.owner_id != current_user.id:
            flash('Invalid item selection.', 'danger')
            return render_template('trades/make_offer.html', requested_item=requested_item, my_items=my_items)

        # Check for duplicate pending offer
        existing = TradeOffer.query.filter_by(
            sender_id=current_user.id,
            offered_item_id=offered_item_id,
            requested_item_id=item_id,
            status='pending'
        ).first()
        if existing:
            flash('You already have a pending offer for this trade.', 'warning')
            return redirect(url_for('trades.offer_detail', offer_id=existing.id))

        offer = TradeOffer(
            sender_id=current_user.id,
            receiver_id=requested_item.owner_id,
            offered_item_id=offered_item_id,
            requested_item_id=item_id,
            message=message
        )
        db.session.add(offer)
        db.session.flush()
        _notify(requested_item.owner_id,
                'New Trade Offer!',
                f'{current_user.display_name} wants to trade for your "{requested_item.title}".',
                url_for('trades.offer_detail', offer_id=offer.id))
        db.session.commit()
        flash('Trade offer sent!', 'success')
        return redirect(url_for('trades.offer_detail', offer_id=offer.id))

    return render_template('trades/make_offer.html', requested_item=requested_item, my_items=my_items)


@trades_bp.route('/trades')
@login_required
def my_trades():
    tab = request.args.get('tab', 'received')
    received = TradeOffer.query.filter_by(receiver_id=current_user.id).order_by(TradeOffer.created_at.desc()).all()
    sent = TradeOffer.query.filter_by(sender_id=current_user.id).order_by(TradeOffer.created_at.desc()).all()
    return render_template('trades/my_trades.html', received=received, sent=sent, tab=tab)


@trades_bp.route('/trades/<int:offer_id>')
@login_required
def offer_detail(offer_id):
    offer = TradeOffer.query.get_or_404(offer_id)
    if offer.sender_id != current_user.id and offer.receiver_id != current_user.id:
        abort(403)
    return render_template('trades/offer_detail.html', offer=offer)


@trades_bp.route('/trades/<int:offer_id>/respond', methods=['POST'])
@login_required
def respond_offer(offer_id):
    offer = TradeOffer.query.get_or_404(offer_id)
    if offer.receiver_id != current_user.id:
        abort(403)
    if offer.status != 'pending':
        flash('This offer is no longer active.', 'warning')
        return redirect(url_for('trades.offer_detail', offer_id=offer_id))

    action = request.form.get('action')
    if action == 'accept':
        offer.status = 'accepted'
        _notify(offer.sender_id, 'Trade Offer Accepted!',
                f'{current_user.display_name} accepted your trade offer!',
                url_for('trades.offer_detail', offer_id=offer_id))
        flash('Trade accepted! Coordinate with the trader to complete the exchange.', 'success')
    elif action == 'decline':
        offer.status = 'declined'
        _notify(offer.sender_id, 'Trade Offer Declined',
                f'{current_user.display_name} declined your trade offer.',
                url_for('trades.offer_detail', offer_id=offer_id))
        flash('Trade declined.', 'info')
    db.session.commit()
    return redirect(url_for('trades.offer_detail', offer_id=offer_id))


@trades_bp.route('/trades/<int:offer_id>/complete', methods=['POST'])
@login_required
def complete_trade(offer_id):
    offer = TradeOffer.query.get_or_404(offer_id)
    if offer.sender_id != current_user.id and offer.receiver_id != current_user.id:
        abort(403)
    if offer.status != 'accepted':
        flash('Trade must be accepted before marking as complete.', 'warning')
        return redirect(url_for('trades.offer_detail', offer_id=offer_id))

    offer.status = 'completed'
    offer.completed_at = datetime.utcnow()
    offer.offered_item.is_available = False
    offer.requested_item.is_available = False

    # Award trade credits
    offer.sender.trade_credits += 10
    offer.receiver.trade_credits += 10

    other_id = offer.receiver_id if current_user.id == offer.sender_id else offer.sender_id
    _notify(other_id, 'Trade Completed!',
            f'{current_user.display_name} marked the trade as complete. Please leave a review!',
            url_for('trades.leave_review', offer_id=offer_id))
    db.session.commit()
    flash('Trade marked as complete! You earned 10 trade credits. Please leave a review.', 'success')
    return redirect(url_for('trades.leave_review', offer_id=offer_id))


@trades_bp.route('/trades/<int:offer_id>/cancel', methods=['POST'])
@login_required
def cancel_offer(offer_id):
    offer = TradeOffer.query.get_or_404(offer_id)
    if offer.sender_id != current_user.id:
        abort(403)
    if offer.status not in ('pending',):
        flash('Cannot cancel this offer.', 'warning')
        return redirect(url_for('trades.offer_detail', offer_id=offer_id))
    offer.status = 'cancelled'
    db.session.commit()
    flash('Offer cancelled.', 'info')
    return redirect(url_for('trades.my_trades'))


@trades_bp.route('/trades/<int:offer_id>/review', methods=['GET', 'POST'])
@login_required
def leave_review(offer_id):
    offer = TradeOffer.query.get_or_404(offer_id)
    if offer.sender_id != current_user.id and offer.receiver_id != current_user.id:
        abort(403)
    if offer.status != 'completed':
        flash('You can only review completed trades.', 'warning')
        return redirect(url_for('trades.offer_detail', offer_id=offer_id))

    reviewed_id = offer.receiver_id if current_user.id == offer.sender_id else offer.sender_id
    already = Review.query.filter_by(reviewer_id=current_user.id, trade_offer_id=offer_id).first()
    if already:
        flash('You already reviewed this trade.', 'info')
        return redirect(url_for('trades.offer_detail', offer_id=offer_id))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = bleach.clean(request.form.get('comment', '').strip())
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'danger')
            return render_template('trades/leave_review.html', offer=offer)
        review = Review(reviewer_id=current_user.id, reviewed_id=reviewed_id,
                        trade_offer_id=offer_id, rating=rating, comment=comment)
        db.session.add(review)
        _notify(reviewed_id, 'New Review!',
                f'{current_user.display_name} left you a {rating}-star review.',
                url_for('profile.user_profile', username=User.query.get(reviewed_id).username))
        db.session.commit()
        flash('Review submitted!', 'success')
        return redirect(url_for('trades.offer_detail', offer_id=offer_id))

    return render_template('trades/leave_review.html', offer=offer)
