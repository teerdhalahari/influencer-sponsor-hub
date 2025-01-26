from application import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    platform = db.Column(db.String(100), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    sponsored_campaigns = db.relationship('Campaign', backref='sponsor', lazy=True, foreign_keys='Campaign.sponsor_id')
    influencer_campaigns = db.relationship('Campaign', backref='influencer', lazy=True, foreign_keys='Campaign.influencer_id')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    visibility = db.Column(db.String(10), nullable=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=True) 
    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"Campaign('{self.name}', '{self.start_date}', '{self.end_date}', '{self.budget}')"

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    payment_amount = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), default='Pending')
    sponsor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"AdRequest('{self.id}', '{self.campaign_id}', '{self.influencer_id}', '{self.status}')"
