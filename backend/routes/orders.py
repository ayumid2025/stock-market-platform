from flask import Blueprint, request, jsonify
from auth import token_required
from models import Account, Order
from services.trading import execute_order

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
@token_required
def place_order():
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    side = data.get('side')
    quantity = data.get('quantity')
    
    if not symbol or not side or not quantity:
        return jsonify({'message': 'Missing fields'}), 400
    
    account = Account.query.filter_by(user_id=request.user_id).first()
    if not account:
        return jsonify({'message': 'Account not found'}), 404
    
    result = execute_order(account.id, symbol, side, int(quantity))
    if result['success']:
        return jsonify({
            'message': 'Order executed',
            'price': result['price'],
            'cash_balance': result['cash_balance']
        }), 201
    else:
        return jsonify({'message': result['message']}), 400

@orders_bp.route('/', methods=['GET'])
@token_required
def get_orders():
    account = Account.query.filter_by(user_id=request.user_id).first()
    orders = Order.query.filter_by(account_id=account.id).order_by(Order.created_at.desc()).all()
    return jsonify([{
        'id': o.id,
        'symbol': o.symbol,
        'side': o.side,
        'quantity': o.quantity,
        'price': o.price,
        'created_at': o.created_at.isoformat()
    } for o in orders])
