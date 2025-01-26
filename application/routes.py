from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from application import app, db, login_manager
from application.model import User, Campaign, AdRequest
from application.forms import AdRequestForm, LoginForm, RegistrationForm, CampaignForm

from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@app.route('/')
@login_required
def home():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/influencersignup', methods=["GET", "POST"])
def influencer_signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role="influencer", platform=form.platform.data)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful!', category='success')
        return redirect(url_for('login'))
    return render_template('influencersignup.html', form=form)

@app.route('/sponsorsignup', methods=["GET", "POST"])
def sponsor_signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role="sponsor", industry=form.industry.data)
        db.session.add(user)
        db.session.commit()
        flash('Signup successful!', category='success')
        return redirect(url_for('login'))
    return render_template('sponsorsignup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login successful!', category='success')
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.role == "admin":
                return redirect(url_for('admin_dashboard'))
            elif user.role == "influencer":
                return redirect(url_for('influencer_dashboard'))
            elif user.role == "sponsor":
                return redirect(url_for('sponsor_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid username or password', category='danger')
    return render_template('login.html', form=form)


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to view this page.', 'danger')
        return redirect(url_for('login'))  # Redirect to a relevant page

    total_users = User.query.count()
    total_campaigns = Campaign.query.count()
    total_ad_requests = AdRequest.query.count()
    flagged_items = Campaign.query.filter_by(status='flagged').count()

    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_campaigns=total_campaigns,
        total_ad_requests=total_ad_requests,
        flagged_items=flagged_items,
        campaigns=Campaign.query.all()
    )


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been successfully logged out', category='success')
    return redirect(url_for('login'))



@app.route('/campaign/<int:campaign_id>/create_ad_request', methods=['GET', 'POST'])
@login_required
def create_ad_request(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer_id = request.form.get('influencer_id')
    influencer = User.query.get_or_404(influencer_id)
    form = AdRequestForm()

    if form.validate_on_submit():
        ad_request = AdRequest(
            campaign_id=campaign_id,
            influencer_id=form.influencer_id.data,
            messages=form.messages.data,
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status='Pending',
            sponsor_id=current_user.id  # Assuming current_user is the sponsor
        )
        db.session.add(ad_request)
        db.session.commit()
        flash('Ad request created successfully!', 'success')
        return redirect(url_for('find'))  # Redirect to campaigns page or wherever you need to go

    return render_template('create_ad_request.html', form=form, campaign=campaign, influencer=influencer)






def get_influencer_rating(user_id):
    return 4.5  # Placeholder function, replace with actual implementation

def calculate_influencer_earnings(user_id):
    return 1000  # Placeholder function, replace with actual implementation

def get_active_campaigns_for_influencer(user_id):
    return Campaign.query.filter_by(influencer_id=user_id, status='Active').all()

def get_new_requests_for_influencer(user_id):
    return AdRequest.query.filter_by(influencer_id=user_id, status='Pending').all()

def get_ongoing_campaigns():
    return Campaign.query.filter_by(status='Ongoing').all()

def get_flagged_campaigns():
    return Campaign.query.filter_by(status='Flagged').all()

def get_new_requests_for_admin():
    return AdRequest.query.filter_by(status='Pending').all()

def get_active_campaigns_for_sponsor(user_id):
    return Campaign.query.filter_by(sponsor_id=user_id, status='Active').all()

def get_new_requests_for_sponsor(user_id):
    return AdRequest.query.filter_by(sponsor_id=user_id, status='Pending').all()

@app.route('/profile')
@login_required
def profile():
    if current_user.role == 'influencer':
        influencer_rating = get_influencer_rating(current_user.id)
        influencer_earnings = calculate_influencer_earnings(current_user.id)
        campaigns = Campaign.query.filter_by(status='Active').all()
        new_requests = get_new_requests_for_influencer(current_user.id)
        return render_template('profile.html', rating=influencer_rating, earnings=influencer_earnings, campaigns=campaigns, new_requests=new_requests)
    
    elif current_user.role == 'admin':
        campaigns = Campaign.query.filter_by(status='Active').all()
        flagged_campaigns = get_flagged_campaigns()
        new_requests = get_new_requests_for_admin()
        return render_template('profile.html', campaigns=campaigns, flagged_campaigns=flagged_campaigns, new_requests=new_requests)
    
    elif current_user.role == 'sponsor':
        active_campaigns = get_active_campaigns_for_sponsor(current_user.id)
        new_requests = get_new_requests_for_sponsor(current_user.id)
        return render_template('profile.html', active_campaigns=active_campaigns, new_requests=new_requests)
    
    else:
        flash('Unauthorized access!', category='danger')
        return redirect(url_for('home'))



@app.route('/influencer/dashboard')
@login_required
def influencer_dashboard():
    if current_user.role != 'influencer':
        flash('Unauthorized access!', category='danger')
        return redirect(url_for('home'))

    # Fetch active campaigns for the influencer
    campaigns = Campaign.query.filter_by(status='Active').all()

    # Simulated new requests for illustration (replace with actual logic)
    ad_requests = AdRequest.query.filter_by(influencer_id=current_user.id).all()

    return render_template('influencer_dashboard.html', campaigns=campaigns, ad_requests=ad_requests)


@app.route('/sponsor/dashboard')
@login_required
def sponsor_dashboard():
    if current_user.role != 'sponsor':
        flash('Unauthorized access!', category='danger')
        return redirect(url_for('home'))

    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    return render_template('sponsor_dashboard.html', campaigns=campaigns)



@app.route('/find', methods=['GET', 'POST'])
@login_required
def find():
    campaigns = []

    if current_user.role == 'admin':
        campaigns = Campaign.query.all()
    elif current_user.role == 'influencer':
        campaigns = Campaign.query.filter_by(influencer_id=current_user.id).all()
    elif current_user.role == 'sponsor':
        campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()

    influencers = User.query.filter_by(role='influencer').all()

    return render_template('find.html', current_user=current_user, campaigns=campaigns, influencers=influencers)



@app.route('/campaign/<int:campaign_id>/flag', methods=['POST'])
@login_required
def flag_campaign(campaign_id):
    if current_user.role != 'admin':
        flash('Unauthorized access!', category='danger')
        return redirect(url_for('home'))

    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.status = 'Flagged'
    db.session.commit()
    flash('Campaign flagged successfully!', 'success')
    return redirect(url_for('find'))

@app.route('/campaign/<int:campaign_id>/request', methods=['POST'])
@login_required
def request_campaign(campaign_id):
    if current_user.role != 'influencer':
        flash('Unauthorized access!', category='danger')
        return redirect(url_for('home'))

    campaign = Campaign.query.get_or_404(campaign_id)
    ad_request = AdRequest(
        campaign_id=campaign.id,
        influencer_id=current_user.id,
        status='Pending'
    )
    db.session.add(ad_request)
    db.session.commit()
    flash('Ad request created successfully!', 'success')
    return redirect(url_for('find'))

@app.route('/campaigns')
@login_required
def campaigns():
    if current_user.role != 'sponsor':
        flash('Unauthorized access!', category='danger')
        return redirect(url_for('home'))

    # Assuming you have a method to fetch campaigns for the current sponsor
    campaigns = get_active_campaigns_for_sponsor(current_user.id)
    form = AdRequestForm()
    
    return render_template('campaigns.html', campaigns=campaigns, form=form)




@app.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        # Process the form data to create a new campaign
        name = form.name.data
        status = form.status.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        budget = form.budget.data

        new_campaign = Campaign(
            name=name, 
            status=status, 
            start_date=start_date, 
            end_date=end_date, 
            budget=budget,
            sponsor_id=current_user.id  # Ensure the sponsor_id is set
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaigns'))
    return render_template('create_campaign.html', form=form)











    


