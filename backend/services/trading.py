from models import db, Account, Position, Order
from services.market_data import get_stock_quote

def execute_order(account_id, symbol, side, quantity):
    """Execute a paper trade: update cash and positions."""
    account = Account.query.get(account_id)
    if not account:
        return {'success': False, 'message': 'Account not found'}
    
    # Get current price
    quote = get_stock_quote(symbol)
    if not quote:
        return {'success': False, 'message': 'Invalid symbol or API error'}
    price = quote['price']
    total_cost = price * quantity
    
    # Validate based on side
    if side == 'buy':
        if account.cash_balance < total_cost:
            return {'success': False, 'message': 'Insufficient funds'}
        account.cash_balance -= total_cost
        
        # Update or create position
        position = Position.query.filter_by(account_id=account_id, symbol=symbol).first()
        if position:
            # Weighted average price
            new_quantity = position.quantity + quantity
            position.average_price = ((position.average_price * position.quantity) + (price * quantity)) / new_quantity
            position.quantity = new_quantity
        else:
            position = Position(account_id=account_id, symbol=symbol, quantity=quantity, average_price=price)
            db.session.add(position)
            
    elif side == 'sell':
        position = Position.query.filter_by(account_id=account_id, symbol=symbol).first()
        if not position or position.quantity < quantity:
            return {'success': False, 'message': 'Insufficient shares'}
        
        position.quantity -= quantity
        account.cash_balance += total_cost
        
        if position.quantity == 0:
            db.session.delete(position)
    else:
        return {'success': False, 'message': 'Invalid side'}
    
    # Record order
    order = Order(account_id=account_id, symbol=symbol, side=side, quantity=quantity, price=price)
    db.session.add(order)
    db.session.commit()
    
    return {'success': True, 'price': price, 'cash_balance': account.cash_balance}
