"""Borrowers blueprint."""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app import db
from app.models import Borrower

bp = Blueprint('borrowers', __name__, url_prefix='/borrowers')


@bp.route('/')
def list_borrowers():
    """List all borrowers."""
    borrowers = Borrower.query.all()
    return render_template('borrowers/list.html', borrowers=borrowers)


@bp.route('/<int:borrower_id>')
def detail(borrower_id):
    """Borrower detail page with loan history."""
    borrower = Borrower.query.get_or_404(borrower_id)
    return render_template('borrowers/detail.html', borrower=borrower)


@bp.route('/new', methods=['GET', 'POST'])
def create():
    """Create a new borrower."""
    if request.method == 'POST':
        borrower = Borrower(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form.get('phone')
        )
        db.session.add(borrower)
        db.session.commit()
        flash('Borrower created successfully!', 'success')
        return redirect(url_for('borrowers.detail', borrower_id=borrower.id))
    
    return render_template('borrowers/form.html', borrower=None)


@bp.route('/<int:borrower_id>/edit', methods=['GET', 'POST'])
def edit(borrower_id):
    """Edit a borrower."""
    borrower = Borrower.query.get_or_404(borrower_id)
    
    if request.method == 'POST':
        borrower.name = request.form['name']
        borrower.email = request.form['email']
        borrower.phone = request.form.get('phone')
        db.session.commit()
        flash('Borrower updated successfully!', 'success')
        return redirect(url_for('borrowers.detail', borrower_id=borrower.id))
    
    return render_template('borrowers/form.html', borrower=borrower)


# API endpoints
@bp.route('/api/search')
def api_search():
    """Search borrowers API endpoint."""
    query = request.args.get('q', '')
    
    borrowers = Borrower.query.filter(
        Borrower.name.ilike(f'%{query}%') |
        Borrower.email.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([borrower.to_dict() for borrower in borrowers])
