"""Serverless function entry point for Vercel deployment."""
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

# Set environment variable to indicate we're on Vercel
os.environ['VERCEL'] = '1'

# Create the Flask app instance
app = create_app('production')

# This is the WSGI application that Vercel will call
# Vercel requires the app object to be named 'app'
