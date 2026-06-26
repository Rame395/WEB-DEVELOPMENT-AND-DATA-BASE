from flask import Blueprint, render_template, flash, redirect, url_for, request
from decorator import admin_required, login_required, csrf_protected
from database.schema import db

manage_currency_bp = Blueprint('manage_currency', __name__)


# ============================
# LIST CURRENCIES
# ============================
@manage_currency_bp.route('/admin/manage_currency')
@login_required
@admin_required
def manage_currencies():
    CURRENCY_LIST_QUERY = """
        SELECT id, code, name, symbol, exchange_rate_to_gbp, is_active
        FROM currencies
    """
    currencies = db.fetchQuery(CURRENCY_LIST_QUERY)

    COUNT_QUERY = "SELECT COUNT(*) AS total FROM currencies"
    total_currencies = db.fetchQuery(COUNT_QUERY)[0]['total']
    print(f"Currencies : {currencies}")

    return render_template(
        'admin/currency_management/manage_currency.html',
        currencies=currencies,
        total_currencies=total_currencies
    )


# ============================
# ADD CURRENCY
# ============================
@manage_currency_bp.route('/admin/manage_currency/add', methods=['GET', 'POST'])
@login_required
@admin_required
@csrf_protected
def add_currency():
    if request.method == 'POST':
        code = request.form.get('code').strip().upper()
        name = request.form.get('name').strip()
        symbol = request.form.get('symbol').strip()
        rate = request.form.get('exchange_rate_to_gbp')
        is_active = request.form.get('is_active', 1)

        if not all([code, name, symbol, rate]):
            flash("All fields are required", "warning")
            return redirect(url_for('manage_currency.add_currency'))

        CHECK_QUERY = "SELECT id FROM currencies WHERE code=%s"
        if db.fetchQuery(CHECK_QUERY, (code,)):
            flash("Currency code already exists", "danger")
            return redirect(url_for('manage_currency.add_currency'))

        INSERT_QUERY = """
            INSERT INTO currencies (code, name, symbol, exchange_rate_to_gbp, is_active)
            VALUES (%s, %s, %s, %s, %s)
        """
        db.executeQuery(INSERT_QUERY, (code, name, symbol, rate, is_active))

        flash("Currency added successfully", "success")
        return redirect(url_for('manage_currency.manage_currencies'))

    return render_template('admin/currency_management/add_currency.html')


# ============================
# DELETE CURRENCY
# ============================
@manage_currency_bp.route('/admin/manage_currency/delete/<int:id>')
@login_required
@admin_required
@csrf_protected
def delete_currency(id):
    CHECK_QUERY = "SELECT id FROM currencies WHERE id=%s"
    currency = db.fetchQuery(CHECK_QUERY, (id,))

    if not currency:
        flash("Currency not found", "danger")
        return redirect(url_for('manage_currency.manage_currencies'))

    DELETE_QUERY = "DELETE FROM currencies WHERE id=%s"
    db.executeQuery(DELETE_QUERY, (id,))

    flash("Currency deleted successfully", "success")
    return redirect(url_for('manage_currency.manage_currencies'))



# ============================
# EDIT CURRENCY
# ============================
@manage_currency_bp.route('/admin/manage_currency/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
@csrf_protected
def edit_currency(id):
    CHECK_QUERY = "SELECT * FROM currencies WHERE id=%s"
    currency = db.fetchQuery(CHECK_QUERY, (id,))

    if not currency:
        flash("Currency not found", "danger")
        return redirect(url_for('manage_currency.manage_currencies'))

    currency = currency[0]

    if request.method == 'POST':
        code = request.form.get('code').strip().upper()
        name = request.form.get('name').strip()
        symbol = request.form.get('symbol').strip()
        rate = request.form.get('exchange_rate_to_gbp')
        is_active = request.form.get('is_active')

        UPDATE_QUERY = """
            UPDATE currencies
            SET code=%s, name=%s, symbol=%s, exchange_rate_to_gbp=%s, is_active=%s
            WHERE id=%s
        """
        db.executeQuery(UPDATE_QUERY, (code, name, symbol, rate, is_active, id))

        flash("Currency updated successfully", "success")
        return redirect(url_for('manage_currency.manage_currencies'))

    return render_template('admin/currency_management/edit_currency.html', currency=currency)
