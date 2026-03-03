from flask import Blueprint, jsonify
from auth import token_required
from models import Account, Position
from services.market_data import get_stock_quote

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/', methods=['GET'])
@token_required
def get_portfolio():
    account = Account.query.filter_by(user_id=request.user_id).first()
    positions = Position.query.filter_by(account_id=account.id).all()
    
    portfolio_value = account.cash_balance
    holdings = []
    
    for pos in positions:
        quote = get_stock_quote(pos.symbol)
        current_price = quote['price'] if quote else 0
        market_value = current_price * pos.quantity
        cost_basis = pos.average_price * pos.quantity
        unrealized_pl = market_value - cost_basis
        portfolio_value += market_value
        
        holdings.append({
            'symbol': pos.symbol,
            'quantity': pos.quantity,
            'avg_price': pos.average_price,
            'current_price': current_price,
            'market_value': market_value,
            'unrealized_pl': unrealized_pl
        })
    
    return jsonify({
        'cash_balance': account.cash_balance,
        'holdings': holdings,
        'total_value': portfolio_value
    })
