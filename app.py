import sqlite3
import random
import re
from datetime import date, timedelta

from flask import (
    Flask, g, render_template, request, redirect, url_for,
    session, flash, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from models import init_db, get_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_request
    def teardown_request(exception):
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()


    @app.route('/')
    def index():
        sort = request.args.get('sort', 'name')
        order = {'name': 'name', 'price': 'price', 'impact': 'impact'}.get(sort, 'name')
        items = g.db.execute(f"SELECT * FROM items ORDER BY {order}").fetchall()
        return render_template('index.html', items=items)

    @app.route('/about/<int:item_id>')
    def about(item_id):
        token = g.db.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if token is None:
            abort(404)
        return render_template('about.html', token=token)

    @app.route('/price_data/<int:item_id>')
    def price_data(item_id):
        row = g.db.execute(
            "SELECT price FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if row is None:
            abort(404)
        base_price = row['price']

        today = date.today()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
        prices = [
            round(base_price * (1 + random.uniform(-0.05, 0.05)), 2)
            for _ in dates
        ]
        return jsonify(dates=dates, prices=prices)

    @app.route('/add/<int:item_id>')
    def add(item_id):
        cart = session.get('basket', {})
        cart[str(item_id)] = cart.get(str(item_id), 0) + 1
        session['basket'] = cart
        flash('Item added to basket.')
        return redirect(request.referrer or url_for('index'))

    @app.route('/basket')
    def basket():
        cart = session.get('basket', {})
        items = []
        total = 0.0
        for id_str, qty in cart.items():
            try:
                item_id = int(id_str)
            except ValueError:
                continue
            row = g.db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
            if not row:
                continue
            sub = row['price'] * qty
            total += sub
            items.append({'item': row, 'qty': qty, 'sub': sub})
        return render_template('basket.html', items=items, total=total)

    @app.route('/remove/<int:item_id>')
    def remove(item_id):
        cart = session.get('basket', {})
        cart.pop(str(item_id), None)
        session['basket'] = cart
        flash('Item removed from basket.')
        return redirect(url_for('basket'))

    @app.route('/checkout', methods=['GET', 'POST'])
    def checkout():
        if request.method == 'POST':
            cc = request.form.get('cc_number', '').replace(' ', '').replace('-', '')
            name = request.form.get('name', '').strip()
            exp = request.form.get('exp', '').strip()
            errors = []
            if not re.fullmatch(r"\d{16}", cc):
                errors.append('Invalid credit card number.')
            if not name:
                errors.append('Cardholder name required.')
            if not exp:
                errors.append('Expiry date required.')
            if errors:
                for e in errors:
                    flash(e)
                return redirect(url_for('checkout'))
            session.pop('basket', None)
            return render_template('success.html')
        return render_template('checkout.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username'].strip()
            pw = request.form['password']
            if not username or not pw:
                flash('Username and password are required.')
                return redirect(url_for('register'))
            pw_hash = generate_password_hash(pw)
            try:
                g.db.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, pw_hash)
                )
                g.db.commit()
                flash('Registration successful. Please log in.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already taken.')
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            pw = request.form['password']
            user = g.db.execute(
                'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
            if user and check_password_hash(user['password_hash'], pw):
                session['user_id'] = user['id']
                flash('Logged in successfully.')
                return redirect(url_for('index'))
            flash('Invalid username or password.')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)
        flash('You have been logged out.')
        return redirect(url_for('index'))

    @app.route('/review/<int:item_id>', methods=['POST'])
    def review(item_id):
        if 'user_id' not in session:
            flash('Login required to leave a review.')
            return redirect(url_for('login'))
        rating = int(request.form.get('rating', 0))
        comment = request.form.get('comment', '').strip()
        g.db.execute(
            'INSERT INTO reviews (item_id, user_id, rating, comment) VALUES (?, ?, ?, ?)',
            (item_id, session['user_id'], rating, comment)
        )
        g.db.commit()
        flash('Review submitted.')
        return redirect(url_for('about', item_id=item_id))

    @app.route('/search')
    def search():
        q = f"%{request.args.get('q', '').strip()}%"
        items = g.db.execute(
            'SELECT * FROM items WHERE name LIKE ? OR description LIKE ?',
            (q, q)
        ).fetchall()
        return render_template('index.html', items=items)

    @app.route('/invoice')
    def invoice():
        cart = session.get('basket', {})
        items = []
        total = 0.0
        for id_str, qty in cart.items():
            try:
                item_id = int(id_str)
            except ValueError:
                continue
            row = g.db.execute(
                'SELECT * FROM items WHERE id = ?', (item_id,)
            ).fetchone()
            if row is None:
                continue
            sub = row['price'] * qty
            total += sub
            items.append({'item': row, 'qty': qty, 'sub': sub})
        if not items:
            flash('Your basket is empty or contains no valid items.')
        return render_template('invoice.html', items=items, total=total)

    @app.route('/shipping')
    def shipping():
        return render_template('shipping_label.html')

    @app.cli.command('initdb')
    def initdb_command():
        init_db(app)
        print('Database initialized.')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
