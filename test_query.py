#!/usr/bin/env python3
from app import app, db
from models import OrderLine, Shop

with app.app_context():
    # Test query
    q = db.session.query(OrderLine, Shop).join(Shop, Shop.id==OrderLine.shop_id)

    all_data = q.all()
    print(f"Total rows: {len(all_data)}")

    # Check BILL_EMPTY
    bill_empty = [ol for ol, shop in all_data if hasattr(ol, 'allocation_status') and ol.allocation_status == 'BILL_EMPTY']
    print(f"BILL_EMPTY count: {len(bill_empty)}")

    if bill_empty:
        for ol in bill_empty[:5]:
            print(f"  - {ol.order_id}: {ol.allocation_status}")
