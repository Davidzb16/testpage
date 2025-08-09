# -*- encoding: utf-8 -*-
"""
Deliveries Routes for Flask Datta Able
"""

import os
import secrets
from datetime import datetime, timedelta
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from apps import db
from apps.deliveries import blueprint
from apps.deliveries.models import Deliveries, PasswordResets
from apps.authentication.models import Users

@blueprint.route('/')
@login_required
def index():
    """Main deliveries page"""
    deliveries = Deliveries.find_by_user_id(current_user.id)
    counts = Deliveries.get_counts_by_user(current_user.id)
    
    return render_template(
        'deliveries/index.html',
        deliveries=deliveries,
        pending_count=counts.get('pending', 0),
        delivered_count=counts.get('delivered', 0),
        cancelled_count=counts.get('cancelled', 0)
    )

@blueprint.route('/add', methods=['POST'])
@login_required
def add_delivery():
    """Add a new delivery"""
    try:
        tracking_number = request.form.get('tracking_number', '').strip()
        amount_due = request.form.get('amount_due', '').strip()
        
        if not tracking_number:
            return jsonify({'success': False, 'message': 'Tracking number is required'})
        
        if not amount_due:
            return jsonify({'success': False, 'message': 'Amount is required'})
        
        try:
            amount_cents = int(float(amount_due) * 100)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid amount format'})
        
        # Check if tracking number already exists for this user
        existing = Deliveries.query.filter_by(
            user_id=current_user.id,
            tracking_number=tracking_number,
            deleted_at=None
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Tracking number already exists'})
        
        delivery = Deliveries(
            user_id=current_user.id,
            tracking_number=tracking_number,
            amount_due=amount_cents,
            status='pending'
        )
        delivery.save()
        
        return jsonify({
            'success': True,
            'message': 'Delivery added successfully',
            'delivery': {
                'id': delivery.id,
                'tracking_number': delivery.tracking_number,
                'amount_due': delivery.amount_due / 100,
                'status': delivery.status,
                'created_at': delivery.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@blueprint.route('/status', methods=['POST'])
@login_required
def update_status():
    """Update delivery status"""
    try:
        delivery_id = request.form.get('delivery_id')
        new_status = request.form.get('status')
        
        if not delivery_id or not new_status:
            return jsonify({'success': False, 'message': 'Missing required fields'})
        
        delivery = Deliveries.find_by_id_and_user(int(delivery_id), current_user.id)
        if not delivery:
            return jsonify({'success': False, 'message': 'Delivery not found'})
        
        valid_statuses = ['pending', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'success': False, 'message': 'Invalid status'})
        
        delivery.status = new_status
        delivery.updated_at = datetime.utcnow()
        delivery.save()
        
        return jsonify({
            'success': True,
            'message': f'Status updated to {new_status}',
            'status': new_status
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@blueprint.route('/delete', methods=['POST'])
@login_required
def delete_delivery():
    """Soft delete a delivery"""
    try:
        delivery_id = request.form.get('delivery_id')
        
        if not delivery_id:
            return jsonify({'success': False, 'message': 'Delivery ID is required'})
        
        delivery = Deliveries.find_by_id_and_user(int(delivery_id), current_user.id)
        if not delivery:
            return jsonify({'success': False, 'message': 'Delivery not found'})
        
        delivery.soft_delete()
        
        return jsonify({
            'success': True,
            'message': 'Delivery deleted successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@blueprint.route('/restore', methods=['POST'])
@login_required
def restore_delivery():
    """Restore a soft deleted delivery"""
    try:
        delivery_id = request.form.get('delivery_id')
        
        if not delivery_id:
            return jsonify({'success': False, 'message': 'Delivery ID is required'})
        
        delivery = Deliveries.query.filter_by(
            id=int(delivery_id),
            user_id=current_user.id
        ).first()
        
        if not delivery:
            return jsonify({'success': False, 'message': 'Delivery not found'})
        
        if not delivery.deleted_at:
            return jsonify({'success': False, 'message': 'Delivery is not deleted'})
        
        delivery.restore()
        
        return jsonify({
            'success': True,
            'message': 'Delivery restored successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@blueprint.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Please enter your email address', 'error')
            return render_template('deliveries/forgot_password.html')
        
        user = Users.find_by_email(email)
        if not user:
            flash('If an account with that email exists, a reset link has been sent', 'info')
            return render_template('deliveries/forgot_password.html')
        
        # Create password reset token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        reset_record = PasswordResets(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        reset_record.save()
        
        # In a real app, you would send an email here
        # For now, we'll just show the token
        flash(f'Password reset token: {token}', 'info')
        flash('This token expires in 1 hour', 'info')
        
        return render_template('deliveries/forgot_password.html')
    
    return render_template('deliveries/forgot_password.html')

@blueprint.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset"""
    reset_record = PasswordResets.find_valid_by_token(token)
    
    if not reset_record:
        flash('Invalid or expired reset token', 'error')
        return redirect(url_for('deliveries_blueprint.forgot_password'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please fill in all fields', 'error')
            return render_template('deliveries/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('deliveries/reset_password.html', token=token)
        
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('deliveries/reset_password.html', token=token)
        
        # Update user password
        from apps.authentication.util import hash_pass
        user = Users.find_by_id(reset_record.user_id)
        user.password = hash_pass(password)
        user.save()
        
        # Mark reset token as used
        reset_record.used_at = datetime.utcnow()
        reset_record.save()
        
        flash('Password updated successfully. You can now log in with your new password.', 'success')
        return redirect(url_for('authentication_blueprint.login'))
    
    return render_template('deliveries/reset_password.html', token=token)

@blueprint.route('/demo-data')
@login_required
def create_demo_data():
    """Create demo delivery data for the current user"""
    try:
        # Check if user already has deliveries
        existing_deliveries = Deliveries.find_by_user_id(current_user.id)
        if existing_deliveries:
            return jsonify({'success': False, 'message': 'Demo data already exists'})
        
        # Create demo deliveries
        demo_deliveries = [
            {'tracking_number': 'DEMO001', 'amount_due': 2500, 'status': 'pending'},
            {'tracking_number': 'DEMO002', 'amount_due': 1500, 'status': 'delivered'},
            {'tracking_number': 'DEMO003', 'amount_due': 3000, 'status': 'pending'},
            {'tracking_number': 'DEMO004', 'amount_due': 800, 'status': 'cancelled'},
        ]
        
        for demo in demo_deliveries:
            delivery = Deliveries(
                user_id=current_user.id,
                tracking_number=demo['tracking_number'],
                amount_due=demo['amount_due'],
                status=demo['status']
            )
            delivery.save()
        
        return jsonify({
            'success': True,
            'message': 'Demo data created successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})
