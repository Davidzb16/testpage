# -*- encoding: utf-8 -*-
"""
Deliveries Models for Flask Datta Able
"""

from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from apps import db

class Deliveries(db.Model):
    __tablename__ = 'deliveries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tracking_number = db.Column(db.String(100), nullable=False)
    amount_due = db.Column(db.Integer, nullable=False)  # Amount in cents
    status = db.Column(db.String(20), default='pending')  # pending, delivered, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)  # Soft delete

    # Relationship
    user = db.relationship('Users', backref='deliveries')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return f'<Delivery {self.tracking_number}>'

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise IntegrityError(error, 422)

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise IntegrityError(error, 422)

    def soft_delete(self) -> None:
        """Soft delete by setting deleted_at timestamp"""
        self.deleted_at = datetime.utcnow()
        self.save()

    def restore(self) -> None:
        """Restore soft deleted delivery"""
        self.deleted_at = None
        self.save()

    @classmethod
    def find_by_user_id(cls, user_id: int, include_deleted: bool = False):
        """Find all deliveries for a user"""
        query = cls.query.filter_by(user_id=user_id)
        if not include_deleted:
            query = query.filter(cls.deleted_at.is_(None))
        return query.order_by(cls.created_at.desc()).all()

    @classmethod
    def find_by_id_and_user(cls, delivery_id: int, user_id: int):
        """Find a specific delivery by ID and user"""
        return cls.query.filter_by(
            id=delivery_id, 
            user_id=user_id,
            deleted_at=None
        ).first()

    @classmethod
    def get_counts_by_user(cls, user_id: int):
        """Get delivery counts for a user"""
        from sqlalchemy import func
        
        counts = db.session.query(
            cls.status,
            func.count(cls.id).label('count')
        ).filter_by(
            user_id=user_id,
            deleted_at=None
        ).group_by(cls.status).all()
        
        return {status: count for status, count in counts}

class PasswordResets(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('Users', backref='password_resets')

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            setattr(self, property, value)

    def __repr__(self):
        return f'<PasswordReset {self.token[:10]}...>'

    def save(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise IntegrityError(error, 422)

    def delete_from_db(self) -> None:
        try:
            db.session.delete(self)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            db.session.close()
            error = str(e.__dict__['orig'])
            raise IntegrityError(error, 422)

    @classmethod
    def find_by_token(cls, token: str):
        """Find password reset by token"""
        return cls.query.filter_by(token=token).first()

    @classmethod
    def find_valid_by_token(cls, token: str):
        """Find valid (not expired, not used) password reset by token"""
        return cls.query.filter_by(
            token=token,
            used_at=None
        ).filter(cls.expires_at > datetime.utcnow()).first()
