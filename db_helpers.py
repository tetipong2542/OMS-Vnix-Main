"""
Database Helper Functions for Dual Database Mode

This module provides utilities for querying data from both old (SQLite)
and new (Turso/libSQL) databases when DUAL_DB_MODE is enabled.

Usage:
    from db_helpers import dual_query, is_dual_mode_enabled

    # Query from both old and new databases
    all_products = dual_query(Product, bind_old='data_old')
    all_prices = dual_query(SkuPricing, bind_old='price_old')
"""

import os
from typing import List, Optional, Type
from sqlalchemy.orm import Query


def is_dual_mode_enabled() -> bool:
    """Check if Dual Database Mode is enabled via environment variable."""
    return os.environ.get("ENABLE_DUAL_DB_MODE", "").lower() in ("true", "1", "yes")


def dual_query(
    model: Type,
    bind_old: Optional[str] = None,
    filters: Optional[dict] = None,
    order_by: Optional[str] = None
) -> List:
    """
    Query data from both old (SQLite) and new (Turso) databases.

    Args:
        model: SQLAlchemy model class to query
        bind_old: Bind key for old database (e.g., 'data_old', 'price_old', 'supplier_old')
                  If None, only queries from the default/new database
        filters: Dictionary of filter conditions (e.g., {'sku': 'ABC123'})
        order_by: Column name to order results by

    Returns:
        List of model instances from both databases (old + new)

    Example:
        # Query products from both databases
        products = dual_query(Product, bind_old='data_old', filters={'brand': 'Samsung'})

        # Query prices from both databases
        prices = dual_query(SkuPricing, bind_old='price_old', order_by='sku')
    """
    from models import db

    results = []

    # Query from OLD database (if dual mode is enabled and bind_old is specified)
    if is_dual_mode_enabled() and bind_old:
        try:
            # Use text SQL for raw query from old database
            # This is necessary because SQLAlchemy models are bound to the new database
            from sqlalchemy import inspect

            # Get table name and columns from model
            mapper = inspect(model)
            table_name = mapper.tables[0].name

            # Build query
            engine_old = db.engines.get(bind_old)
            if engine_old:
                with engine_old.connect() as conn:
                    # Simple select all - we'll filter in Python
                    from sqlalchemy import text
                    query_sql = f"SELECT * FROM {table_name}"

                    # Apply SQL-level ordering if specified
                    if order_by:
                        query_sql += f" ORDER BY {order_by}"

                    result = conn.execute(text(query_sql))
                    rows = result.fetchall()

                    # Convert rows to model instances
                    columns = result.keys()
                    for row in rows:
                        row_dict = dict(zip(columns, row))

                        # Apply filters if specified
                        if filters:
                            matches = all(row_dict.get(k) == v for k, v in filters.items())
                            if not matches:
                                continue

                        # Create model instance from row data
                        instance = model(**row_dict)
                        results.append(instance)
        except Exception as e:
            print(f"[WARNING] Failed to query from old database ({bind_old}): {e}")
            import traceback
            traceback.print_exc()

    # Query from NEW database (default or specific bind)
    try:
        # Determine which bind to use for new data
        # Models with __bind_key__ will automatically use their bind
        query_new = model.query

        # Apply filters
        if filters:
            for key, value in filters.items():
                query_new = query_new.filter(getattr(model, key) == value)

        # Apply ordering
        if order_by:
            query_new = query_new.order_by(getattr(model, order_by))

        results.extend(query_new.all())
    except Exception as e:
        print(f"[WARNING] Failed to query from new database: {e}")

    return results


def dual_count(
    model: Type,
    bind_old: Optional[str] = None,
    filters: Optional[dict] = None
) -> int:
    """
    Count records from both old and new databases.

    Args:
        model: SQLAlchemy model class to count
        bind_old: Bind key for old database
        filters: Dictionary of filter conditions

    Returns:
        Total count from both databases
    """
    from models import db

    count = 0

    # Count from OLD database
    if is_dual_mode_enabled() and bind_old:
        try:
            from sqlalchemy import inspect, text

            # Get table name from model
            mapper = inspect(model)
            table_name = mapper.tables[0].name

            engine_old = db.engines.get(bind_old)
            if engine_old:
                with engine_old.connect() as conn:
                    # Build count query
                    if filters:
                        # Build WHERE clause
                        where_parts = [f"{k} = :{k}" for k in filters.keys()]
                        where_clause = " AND ".join(where_parts)
                        query_sql = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause}"
                        result = conn.execute(text(query_sql), filters)
                    else:
                        query_sql = f"SELECT COUNT(*) as count FROM {table_name}"
                        result = conn.execute(text(query_sql))

                    count += result.scalar()
        except Exception as e:
            print(f"[WARNING] Failed to count from old database ({bind_old}): {e}")

    # Count from NEW database
    try:
        query_new = model.query

        if filters:
            for key, value in filters.items():
                query_new = query_new.filter(getattr(model, key) == value)

        count += query_new.count()
    except Exception as e:
        print(f"[WARNING] Failed to count from new database: {e}")

    return count


def get_old_bind_for_model(model: Type) -> Optional[str]:
    """
    Determine the appropriate old database bind key for a given model.

    Args:
        model: SQLAlchemy model class

    Returns:
        Bind key string ('data_old', 'price_old', 'supplier_old') or None
    """
    # Check if model has __bind_key__ attribute
    bind_key = getattr(model, '__bind_key__', None)

    if bind_key == 'price':
        return 'price_old'
    elif bind_key == 'supplier':
        return 'supplier_old'
    else:
        # Default bind (data.db)
        return 'data_old'


# Convenience functions for specific database types

def dual_query_data(model: Type, filters: Optional[dict] = None, order_by: Optional[str] = None) -> List:
    """Query from both old and new data databases (data.db)."""
    return dual_query(model, bind_old='data_old', filters=filters, order_by=order_by)


def dual_query_price(model: Type, filters: Optional[dict] = None, order_by: Optional[str] = None) -> List:
    """Query from both old and new price databases (price.db)."""
    return dual_query(model, bind_old='price_old', filters=filters, order_by=order_by)


def dual_query_supplier(model: Type, filters: Optional[dict] = None, order_by: Optional[str] = None) -> List:
    """Query from both old and new supplier databases (supplier_stock.db)."""
    return dual_query(model, bind_old='supplier_old', filters=filters, order_by=order_by)


def dual_query_auto(model: Type, filters: Optional[dict] = None, order_by: Optional[str] = None) -> List:
    """
    Automatically determine the correct old bind and query from both databases.

    This function inspects the model's __bind_key__ attribute to determine
    which old database to query from.
    """
    bind_old = get_old_bind_for_model(model)
    return dual_query(model, bind_old=bind_old, filters=filters, order_by=order_by)
