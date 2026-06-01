import bleach
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import Message, TradeOffer, Notification

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/trades/<int:offer_id>/messages', methods=['GET', 'POST'])
@login_required
def trade_messages(offer_id):
    offer = TradeOffer.query.get_or_404(offer_id)
    if offer.sender_id != current_user.id and offer.receiver_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        body = bleach.clean(request.form.get('body', '').strip())
        if body:
            msg = Message(trade_offer_id=offer_id, sender_id=current_user.id, body=body)
            db.session.add(msg)
            other_id = offer.receiver_id if current_user.id == offer.sender_id else offer.sender_id
            db.session.add(Notification(
                user_id=other_id,
                title='New Message',
                body=f'{current_user.display_name} sent you a message about the trade.',
                link=url_for('messages.trade_messages', offer_id=offer_id)
            ))
            db.session.commit()
        return redirect(url_for('messages.trade_messages', offer_id=offer_id))

    # Mark incoming messages as read
    Message.query.filter_by(
        trade_offer_id=offer_id, is_read=False
    ).filter(Message.sender_id != current_user.id).update({'is_read': True})
    db.session.commit()

    msgs = Message.query.filter_by(trade_offer_id=offer_id).order_by(Message.created_at.asc()).all()
    return render_template('messages/trade_messages.html', offer=offer, messages=msgs)
