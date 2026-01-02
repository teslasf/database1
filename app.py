#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 31 12:04:38 2025

@author: halilbayraktar
"""

import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from chembl_webresource_client.new_client import new_client
import pandas as pd

app = Flask(__name__)

# --- ADD THIS LINE ---
# It looks for an environment variable, otherwise uses the string as a backup
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-123')

# Database Configuration
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri or "sqlite:///local.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model (The table structure)
class Guestbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    message = db.Column(db.String(500))
    # Add this line:
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
  
@app.route('/', methods=['GET', 'POST'])
def index():
    db.create_all() # Ensures tables exist in Postgres
    
    if request.method == 'POST':
        new_name = request.form.get('username')
        new_lastname = request.form.get('userlastname')
        new_msg = request.form.get('content')
        # Access the molecule resource
        molecule = new_client.molecule
        records = molecule.filter(molecule_properties__full_mwt__lte=int(new_lastname)).only(['molecule_chembl_id','molecule_structures','molecule_properties'])

# Convert the first 5 results to a Pandas DataFrame for easy viewing
        df = pd.DataFrame.from_dict(records[:50])

        
        new_entry = Guestbook(name=new_name,lastname=df['molecule_chembl_id'][1],message=new_msg)
        db.session.add(new_entry)
        db.session.commit()
 # --- ADD THIS LINE ---
        #flash('Successfully added your message to the database!')
        
        return redirect(url_for('index'))

    entries = Guestbook.query.order_by(Guestbook.id.desc()).all()
    return render_template('index.html', entries=entries)

if __name__ == "__main__":
    app.run()
