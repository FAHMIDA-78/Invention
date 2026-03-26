# app.py - Main Streamlit Portfolio Application
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import json
import os
import io
import base64
import hashlib
import re
import tempfile
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import PyPDF2
import pdfplumber
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import networkx as nx
import requests
from bs4 import BeautifulSoup
import markdown
import bleach
import yaml
import sqlite3
import hashlib
import secrets
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
import streamlit.components.v1 as components
from streamlit_echarts import st_echarts
import plotly.figure_factory as ff
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time
import threading
import queue

# Configure page
st.set_page_config(
    page_title="PortfolioBuilder Pro - Create Your Professional Portfolio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Custom styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .portfolio-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s;
    }
    
    .portfolio-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    .skill-tag {
        display: inline-block;
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    
    .timeline-item {
        border-left: 3px solid #667eea;
        padding-left: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .profile-image {
        width: 150px;
        height: 150px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #667eea;
    }
    
    .social-icon {
        font-size: 1.5rem;
        margin: 0 0.5rem;
        color: #667eea;
        transition: color 0.3s;
    }
    
    .social-icon:hover {
        color: #764ba2;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        transition: transform 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Dark mode support */
    @media (prefers-color-scheme: dark) {
        .portfolio-card {
            background: #1e1e1e;
            color: #ffffff;
        }
    }
</style>
""", unsafe_allow_html=True)

# Database setup
def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect('portfolios.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY,
                  username TEXT UNIQUE,
                  email TEXT UNIQUE,
                  password TEXT,
                  created_at TIMESTAMP,
                  last_login TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS portfolios
                 (id TEXT PRIMARY KEY,
                  user_id TEXT,
                  title TEXT,
                  design_template TEXT,
                  theme_color TEXT,
                  full_name TEXT,
                  profession TEXT,
                  bio TEXT,
                  email TEXT,
                  phone TEXT,
                  location TEXT,
                  website TEXT,
                  profile_image TEXT,
                  cover_image TEXT,
                  pdf_cv TEXT,
                  video_cv TEXT,
                  is_public BOOLEAN,
                  view_count INTEGER,
                  like_count INTEGER,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS experiences
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  title TEXT,
                  company TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  current BOOLEAN,
                  description TEXT,
                  achievements TEXT,
                  order_num INTEGER,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS educations
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  degree TEXT,
                  institution TEXT,
                  field_of_study TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  grade TEXT,
                  description TEXT,
                  order_num INTEGER,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS skills
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  name TEXT,
                  category TEXT,
                  level INTEGER,
                  years_experience REAL,
                  order_num INTEGER,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  name TEXT,
                  description TEXT,
                  technologies TEXT,
                  link TEXT,
                  github_link TEXT,
                  demo_link TEXT,
                  image TEXT,
                  featured BOOLEAN,
                  order_num INTEGER,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS social_links
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  platform TEXT,
                  url TEXT,
                  order_num INTEGER,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS certifications
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  name TEXT,
                  issuer TEXT,
                  issue_date TEXT,
                  credential_id TEXT,
                  credential_url TEXT,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS analytics
                 (id TEXT PRIMARY KEY,
                  portfolio_id TEXT,
                  event_type TEXT,
                  event_data TEXT,
                  ip_address TEXT,
                  created_at TIMESTAMP,
                  FOREIGN KEY (portfolio_id) REFERENCES portfolios (id))''')
    
    conn.commit()
    conn.close()

# Session state management
def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'current_portfolio' not in st.session_state:
        st.session_state.current_portfolio = None
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = {}
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

# Authentication functions
def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    """Register new user"""
    conn = sqlite3.connect('portfolios.db')
    c = conn.cursor()
    
    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(password)
    created_at = datetime.now().isoformat()
    
    try:
        c.execute("INSERT INTO users (id, username, email, password, created_at) VALUES (?, ?, ?, ?, ?)",
                 (user_id, username, email, hashed_pwd, created_at))
        conn.commit()
        conn.close()
        return True, user_id
    except sqlite3.IntegrityError:
        conn.close()
        return False, None

def login_user(username, password):
    """Login user"""
    conn = sqlite3.connect('portfolios.db')
    c = conn.cursor()
    
    hashed_pwd = hash_password(password)
    c.execute("SELECT id, username FROM users WHERE username=? AND password=?", 
             (username, hashed_pwd))
    user = c.fetchone()
    
    if user:
        # Update last login
        c.execute("UPDATE users SET last_login=? WHERE id=?", 
                 (datetime.now().isoformat(), user[0]))
        conn.commit()
        conn.close()
        return True, user[0], user[1]
    else:
        conn.close()
        return False, None, None

# Portfolio CRUD operations
def save_portfolio(portfolio_data):
    """Save or update portfolio"""
    conn = sqlite3.connect('portfolios.db')
    c = conn.cursor()
    
    portfolio_id = portfolio_data.get('id', str(uuid.uuid4()))
    user_id = st.session_state.user_id
    
    # Check if portfolio exists
    c.execute("SELECT id FROM portfolios WHERE id=?", (portfolio_id,))
    exists = c.fetchone()
    
    if exists:
        # Update existing portfolio
        c.execute("""UPDATE portfolios SET 
                     title=?, design_template=?, theme_color=?,
                     full_name=?, profession=?, bio=?, email=?, phone=?, location=?, website=?,
                     profile_image=?, cover_image=?, pdf_cv=?, video_cv=?,
                     is_public=?, updated_at=?
                     WHERE id=?""",
                 (portfolio_data.get('title', ''),
                  portfolio_data.get('design_template', 'modern'),
                  portfolio_data.get('theme_color', '#667eea'),
                  portfolio_data.get('full_name', ''),
                  portfolio_data.get('profession', ''),
                  portfolio_data.get('bio', ''),
                  portfolio_data.get('email', ''),
                  portfolio_data.get('phone', ''),
                  portfolio_data.get('location', ''),
                  portfolio_data.get('website', ''),
                  portfolio_data.get('profile_image', ''),
                  portfolio_data.get('cover_image', ''),
                  portfolio_data.get('pdf_cv', ''),
                  portfolio_data.get('video_cv', ''),
                  portfolio_data.get('is_public', True),
                  datetime.now().isoformat(),
                  portfolio_id))
        
        # Delete existing experiences, educations, skills, projects, social links
        c.execute("DELETE FROM experiences WHERE portfolio_id=?", (portfolio_id,))
        c.execute("DELETE FROM educations WHERE portfolio_id=?", (portfolio_id,))
        c.execute("DELETE FROM skills WHERE portfolio_id=?", (portfolio_id,))
        c.execute("DELETE FROM projects WHERE portfolio_id=?", (portfolio_id,))
        c.execute("DELETE FROM social_links WHERE portfolio_id=?", (portfolio_id,))
    else:
        # Insert new portfolio
        c.execute("""INSERT INTO portfolios 
                     (id, user_id, title, design_template, theme_color,
                      full_name, profession, bio, email, phone, location, website,
                      profile_image, cover_image, pdf_cv, video_cv,
                      is_public, view_count, like_count, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (portfolio_id, user_id,
                  portfolio_data.get('title', ''),
                  portfolio_data.get('design_template', 'modern'),
                  portfolio_data.get('theme_color', '#667eea'),
                  portfolio_data.get('full_name', ''),
                  portfolio_data.get('profession', ''),
                  portfolio_data.get('bio', ''),
                  portfolio_data.get('email', ''),
                  portfolio_data.get('phone', ''),
                  portfolio_data.get('location', ''),
                  portfolio_data.get('website', ''),
                  portfolio_data.get('profile_image', ''),
                  portfolio_data.get('cover_image', ''),
                  portfolio_data.get('pdf_cv', ''),
                  portfolio_data.get('video_cv', ''),
                  portfolio_data.get('is_public', True),
                  0, 0, datetime.now().isoformat(), datetime.now().isoformat()))
    
    # Insert experiences
    for i, exp in enumerate(portfolio_data.get('experiences', [])):
        exp_id = str(uuid.uuid4())
        c.execute("""INSERT INTO experiences 
                     (id, portfolio_id, title, company, start_date, end_date, current, description, achievements, order_num)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (exp_id, portfolio_id, exp.get('title', ''), exp.get('company', ''),
                  exp.get('start_date', ''), exp.get('end_date', ''), exp.get('current', False),
                  exp.get('description', ''), json.dumps(exp.get('achievements', [])), i))
    
    # Insert educations
    for i, edu in enumerate(portfolio_data.get('educations', [])):
        edu_id = str(uuid.uuid4())
        c.execute("""INSERT INTO educations 
                     (id, portfolio_id, degree, institution, field_of_study, start_date, end_date, grade, description, order_num)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (edu_id, portfolio_id, edu.get('degree', ''), edu.get('institution', ''),
                  edu.get('field_of_study', ''), edu.get('start_date', ''), edu.get('end_date', ''),
                  edu.get('grade', ''), edu.get('description', ''), i))
    
    # Insert skills
    for i, skill in enumerate(portfolio_data.get('skills', [])):
        skill_id = str(uuid.uuid4())
        c.execute("""INSERT INTO skills 
                     (id, portfolio_id, name, category, level, years_experience, order_num)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                 (skill_id, portfolio_id, skill.get('name', ''), skill.get('category', ''),
                  skill.get('level', 3), skill.get('years_experience', 0), i))
    
    # Insert projects
    for i, project in enumerate(portfolio_data.get('projects', [])):
        project_id = str(uuid.uuid4())
        c.execute("""INSERT INTO projects 
                     (id, portfolio_id, name, description, technologies, link, github_link, demo_link, image, featured, order_num)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                 (project_id, portfolio_id, project.get('name', ''), project.get('description', ''),
                  json.dumps(project.get('technologies', [])), project.get('link', ''),
                  project.get('github_link', ''), project.get('demo_link', ''),
                  project.get('image', ''), project.get('featured', False), i))
    
    # Insert social links
    for i, link in enumerate(portfolio_data.get('social_links', [])):
        link_id = str(uuid.uuid4())
        c.execute("""INSERT INTO social_links 
                     (id, portfolio_id, platform, url, order_num)
                     VALUES (?, ?, ?, ?, ?)""",
                 (link_id, portfolio_id, link.get('platform', ''), link.get('url', ''), i))
    
    conn.commit()
    conn.close()
    
    return portfolio_id

def load_portfolio(portfolio_id):
    """Load portfolio from database"""
    conn = sqlite3.connect('portfolios.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Load portfolio data
    c.execute("SELECT * FROM portfolios WHERE id=?", (portfolio_id,))
    portfolio = c.fetchone()
    
    if not portfolio:
        conn.close()
        return None
    
    portfolio_dict = dict(portfolio)
    
    # Load experiences
    c.execute("SELECT * FROM experiences WHERE portfolio_id=? ORDER BY order_num", (portfolio_id,))
    portfolio_dict['experiences'] = [dict(row) for row in c.fetchall()]
    
    # Load educations
    c.execute("SELECT * FROM educations WHERE portfolio_id=? ORDER BY order_num", (portfolio_id,))
    portfolio_dict['educations'] = [dict(row) for row in c.fetchall()]
    
    # Load skills
    c.execute("SELECT * FROM skills WHERE portfolio_id=? ORDER BY order_num", (portfolio_id,))
    portfolio_dict['skills'] = [dict(row) for row in c.fetchall()]
    
    # Load projects
    c.execute("SELECT * FROM projects WHERE portfolio_id=? ORDER BY order_num", (portfolio_id,))
    projects = []
    for row in c.fetchall():
        project = dict(row)
        project['technologies'] = json.loads(project['technologies']) if project['technologies'] else []
        projects.append(project)
    portfolio_dict['projects'] = projects
    
    # Load social links
    c.execute("SELECT * FROM social_links WHERE portfolio_id=? ORDER BY order_num", (portfolio_id,))
    portfolio_dict['social_links'] = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return portfolio_dict

def get_user_portfolios(user_id):
    """Get all portfolios for a user"""
    conn = sqlite3.connect('portfolios.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("SELECT * FROM portfolios WHERE user_id=? ORDER BY updated_at DESC", (user_id,))
    portfolios = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return portfolios

def get_public_portfolios(limit=12):
    """Get public portfolios"""
    conn = sqlite3.connect('portfolios.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute("""SELECT * FROM portfolios 
                 WHERE is_public=1 
                 ORDER BY view_count DESC, created_at DESC 
                 LIMIT ?""", (limit,))
    portfolios = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return portfolios

def increment_view_count(portfolio_id):
    """Increment portfolio view count"""
    conn = sqlite3.connect('portfolios.db')
    c = conn.cursor()
    
    c.execute("UPDATE portfolios SET view_count = view_count + 1 WHERE id=?", (portfolio_id,))
    conn.commit()
    conn.close()

# PDF Processing
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        st.error(f"Error extracting PDF text: {e}")
    
    return text

def parse_cv_text(text):
    """Parse CV text to extract information"""
    data = {
        'full_name': '',
        'profession': '',
        'email': '',
        'phone': '',
        'skills': [],
        'experiences': [],
        'educations': [],
        'summary': ''
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        data['email'] = emails[0]
    
    # Extract phone
    phone_pattern = r'\+?[\d\s\-\(\)]{10,}'
    phones = re.findall(phone_pattern, text)
    if phones:
        data['phone'] = phones[0][:20]
    
    # Extract name (first few lines)
    lines = text.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if len(line.split()) <= 5 and len(line) < 50 and line and not any(c.isdigit() for c in line):
            data['full_name'] = line
            break
    
    # Extract profession
    for line in lines[:20]:
        if any(word in line.lower() for word in ['developer', 'engineer', 'designer', 'manager', 'analyst']):
            data['profession'] = line.strip()
            break
    
    # Extract skills
    skill_sections = ['skills', 'technologies', 'competencies', 'expertise']
    skills_found = []
    
    for i, line in enumerate(lines):
        if any(section in line.lower() for section in skill_sections):
            for j in range(i+1, min(i+15, len(lines))):
                skill_line = lines[j].strip()
                if skill_line and not any(section in skill_line.lower() for section in ['experience', 'education', 'project']):
                    skills = re.split(r'[•,;\n]', skill_line)
                    for skill in skills:
                        skill = skill.strip()
                        if skill and len(skill) < 30:
                            skills_found.append({'name': skill, 'level': 3})
            break
    
    data['skills'] = skills_found[:10]
    
    return data

# Video CV Generation
def create_video_cv(portfolio_data, output_path):
    """Create video CV using images"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import imageio
        
        # Create frames
        frames = []
        duration_per_frame = 2
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            # Frame 1: Introduction
            img1 = Image.new('RGB', (1920, 1080), color='#1a1a2e')
            draw = ImageDraw.Draw(img1)
            
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 48)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
            
            # Draw text
            draw.text((960, 400), portfolio_data.get('full_name', 'Your Name'), 
                     fill='white', anchor='mm', font=font_large)
            draw.text((960, 500), portfolio_data.get('profession', 'Professional'), 
                     fill='#00ff00', anchor='mm', font=font_medium)
            
            img1_path = os.path.join(tmpdir, 'frame1.png')
            img1.save(img1_path)
            frames.append(imageio.imread(img1_path))
            
            # Frame 2: Bio
            if portfolio_data.get('bio'):
                img2 = Image.new('RGB', (1920, 1080), color='#16213e')
                draw = ImageDraw.Draw(img2)
                draw.text((960, 540), portfolio_data.get('bio', '')[:200], 
                         fill='white', anchor='mm', font=font_medium)
                img2_path = os.path.join(tmpdir, 'frame2.png')
                img2.save(img2_path)
                frames.append(imageio.imread(img2_path))
            
            # Frame 3: Skills
            if portfolio_data.get('skills'):
                img3 = Image.new('RGB', (1920, 1080), color='#0f3460')
                draw = ImageDraw.Draw(img3)
                draw.text((960, 200), "Skills & Expertise", fill='white', anchor='mm', font=font_large)
                
                y_offset = 350
                for skill in portfolio_data.get('skills', [])[:6]:
                    draw.text((960, y_offset), f"• {skill.get('name', '')}", 
                             fill='white', anchor='mm', font=font_medium)
                    y_offset += 80
                
                img3_path = os.path.join(tmpdir, 'frame3.png')
                img3.save(img3_path)
                frames.append(imageio.imread(img3_path))
            
            # Save video
            imageio.mimsave(output_path, frames, fps=1, quality=8)
        
        return True
    except Exception as e:
        st.error(f"Error creating video CV: {e}")
        return False

# Portfolio Templates
def render_modern_portfolio(portfolio):
    """Render modern portfolio template"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if portfolio.get('profile_image'):
            st.image(portfolio['profile_image'], width=200)
        else:
            st.image("https://via.placeholder.com/200x200?text=Profile", width=200)
        
        st.markdown(f"### {portfolio.get('full_name', 'Your Name')}")
        st.markdown(f"**{portfolio.get('profession', 'Professional')}**")
        
        st.markdown("---")
        st.markdown("### Contact")
        if portfolio.get('email'):
            st.markdown(f"📧 {portfolio['email']}")
        if portfolio.get('phone'):
            st.markdown(f"📞 {portfolio['phone']}")
        if portfolio.get('location'):
            st.markdown(f"📍 {portfolio['location']}")
        if portfolio.get('website'):
            st.markdown(f"🌐 {portfolio['website']}")
        
        st.markdown("---")
        st.markdown("### Skills")
        for skill in portfolio.get('skills', []):
            st.markdown(f"• {skill.get('name', '')} {'⭐' * skill.get('level', 3)}")
    
    with col2:
        if portfolio.get('bio'):
            st.markdown("### About Me")
            st.markdown(portfolio['bio'])
            st.markdown("---")
        
        if portfolio.get('experiences'):
            st.markdown("### Work Experience")
            for exp in portfolio.get('experiences', []):
                with st.expander(f"{exp.get('title', '')} at {exp.get('company', '')}"):
                    st.markdown(f"*{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}*")
                    st.markdown(exp.get('description', ''))
        
        if portfolio.get('projects'):
            st.markdown("### Projects")
            cols = st.columns(2)
            for i, project in enumerate(portfolio.get('projects', [])):
                with cols[i % 2]:
                    with st.container():
                        st.markdown(f"**{project.get('name', '')}**")
                        st.markdown(project.get('description', '')[:100])
                        if project.get('technologies'):
                            st.markdown(f"*Technologies: {', '.join(project['technologies'])}*")
                        if project.get('link'):
                            st.markdown(f"[View Project]({project['link']})")

def render_classic_portfolio(portfolio):
    """Render classic portfolio template"""
    st.markdown(f"# {portfolio.get('full_name', 'Your Name')}")
    st.markdown(f"## {portfolio.get('profession', 'Professional')}")
    
    if portfolio.get('bio'):
        st.markdown(portfolio['bio'])
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Experience")
        for exp in portfolio.get('experiences', []):
            st.markdown(f"**{exp.get('title', '')}**")
            st.markdown(f"*{exp.get('company', '')} | {exp.get('start_date', '')} - {exp.get('end_date', 'Present')}*")
            st.markdown(exp.get('description', ''))
            st.markdown("")
    
    with col2:
        st.markdown("### Education")
        for edu in portfolio.get('educations', []):
            st.markdown(f"**{edu.get('degree', '')}**")
            st.markdown(f"*{edu.get('institution', '')} | {edu.get('year', '')}*")
            st.markdown(edu.get('description', ''))
            st.markdown("")
        
        st.markdown("### Skills")
        for skill in portfolio.get('skills', []):
            st.markdown(f"• {skill.get('name', '')}")

def render_creative_portfolio(portfolio):
    """Render creative portfolio template"""
    # Hero section
    st.markdown(f"""
    <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, {portfolio.get('theme_color', '#667eea')}, #764ba2); border-radius: 10px; margin-bottom: 2rem;'>
        <h1 style='color: white;'>{portfolio.get('full_name', 'Your Name')}</h1>
        <p style='color: white; font-size: 1.2rem;'>{portfolio.get('profession', 'Professional')}</p>
        <p style='color: white;'>{portfolio.get('bio', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Skills section with progress bars
    if portfolio.get('skills'):
        st.markdown("## Skills")
        for skill in portfolio.get('skills', []):
            st.markdown(f"{skill.get('name', '')}")
            st.progress(skill.get('level', 3) / 5)
    
    # Experience timeline
    if portfolio.get('experiences'):
        st.markdown("## Experience")
        for exp in portfolio.get('experiences', []):
            with st.container():
                st.markdown(f"### {exp.get('title', '')}")
                st.markdown(f"**{exp.get('company', '')}** | {exp.get('start_date', '')} - {exp.get('end_date', 'Present')}")
                st.markdown(exp.get('description', ''))
                st.markdown("---")

def render_minimal_portfolio(portfolio):
    """Render minimal portfolio template"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if portfolio.get('profile_image'):
            st.image(portfolio['profile_image'], width=150)
        
        st.markdown(f"### {portfolio.get('full_name', 'Your Name')}")
        st.markdown(portfolio.get('profession', 'Professional'))
        
        st.markdown("---")
        if portfolio.get('email'):
            st.markdown(portfolio['email'])
        if portfolio.get('phone'):
            st.markdown(portfolio['phone'])
        if portfolio.get('location'):
            st.markdown(portfolio['location'])
    
    with col2:
        if portfolio.get('bio'):
            st.markdown(portfolio['bio'])
            st.markdown("---")
        
        if portfolio.get('experiences'):
            st.markdown("#### Experience")
            for exp in portfolio.get('experiences', []):
                st.markdown(f"**{exp.get('title', '')}**, {exp.get('company', '')}")
                st.markdown(f"*{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}*")
                st.markdown(exp.get('description', ''))
        
        if portfolio.get('projects'):
            st.markdown("#### Projects")
            for project in portfolio.get('projects', []):
                st.markdown(f"**{project.get('name', '')}** - {project.get('description', '')}")

# PDF CV Generator
def generate_pdf_cv(portfolio):
    """Generate PDF CV from portfolio data"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30)
    if portfolio.get('full_name'):
        story.append(Paragraph(portfolio['full_name'], title_style))
    if portfolio.get('profession'):
        story.append(Paragraph(portfolio['profession'], styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Contact info
    contact_info = []
    if portfolio.get('email'):
        contact_info.append(f"Email: {portfolio['email']}")
    if portfolio.get('phone'):
        contact_info.append(f"Phone: {portfolio['phone']}")
    if portfolio.get('location'):
        contact_info.append(f"Location: {portfolio['location']}")
    
    contact_text = " | ".join(contact_info)
    story.append(Paragraph(contact_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Bio
    if portfolio.get('bio'):
        story.append(Paragraph("Professional Summary", styles['Heading2']))
        story.append(Paragraph(portfolio['bio'], styles['Normal']))
        story.append(Spacer(1, 20))
    
    # Experience
    if portfolio.get('experiences'):
        story.append(Paragraph("Work Experience", styles['Heading2']))
        for exp in portfolio['experiences']:
            title_text = f"<b>{exp.get('title', '')}</b> at {exp.get('company', '')}"
            story.append(Paragraph(title_text, styles['Heading3']))
            date_text = f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}"
            story.append(Paragraph(date_text, styles['Italic']))
            if exp.get('description'):
                story.append(Paragraph(exp['description'], styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Education
    if portfolio.get('educations'):
        story.append(Paragraph("Education", styles['Heading2']))
        for edu in portfolio['educations']:
            degree_text = f"<b>{edu.get('degree', '')}</b>"
            if edu.get('field_of_study'):
                degree_text += f" in {edu['field_of_study']}"
            story.append(Paragraph(degree_text, styles['Heading3']))
            institution_text = edu.get('institution', '')
            if edu.get('year'):
                institution_text += f", {edu['year']}"
            story.append(Paragraph(institution_text, styles['Normal']))
            if edu.get('description'):
                story.append(Paragraph(edu['description'], styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Skills
    if portfolio.get('skills'):
        story.append(Paragraph("Skills", styles['Heading2']))
        skill_list = []
        for skill in portfolio['skills']:
            skill_list.append(f"• {skill.get('name', '')}")
        skills_text = "<br/>".join(skill_list)
        story.append(Paragraph(skills_text, styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Portfolio Builder Form
def portfolio_builder_form():
    """Interactive portfolio builder form"""
    st.markdown("### Portfolio Builder")
    
    # Load existing portfolio if in edit mode
    if st.session_state.edit_mode and st.session_state.current_portfolio:
        portfolio = load_portfolio(st.session_state.current_portfolio)
        if portfolio:
            st.session_state.portfolio_data = portfolio
    
    with st.form("portfolio_form", clear_on_submit=False):
        # Basic Information
        st.markdown("#### Basic Information")
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Portfolio Title", st.session_state.portfolio_data.get('title', ''))
            full_name = st.text_input("Full Name", st.session_state.portfolio_data.get('full_name', ''))
            profession = st.text_input("Profession", st.session_state.portfolio_data.get('profession', ''))
            email = st.text_input("Email", st.session_state.portfolio_data.get('email', ''))
        with col2:
            design_template = st.selectbox("Design Template", 
                                          ['modern', 'classic', 'creative', 'minimal'],
                                          index=['modern', 'classic', 'creative', 'minimal'].index(
                                              st.session_state.portfolio_data.get('design_template', 'modern')))
            theme_color = st.color_picker("Theme Color", st.session_state.portfolio_data.get('theme_color', '#667eea'))
            phone = st.text_input("Phone", st.session_state.portfolio_data.get('phone', ''))
            location = st.text_input("Location", st.session_state.portfolio_data.get('location', ''))
        
        bio = st.text_area("Bio/Summary", st.session_state.portfolio_data.get('bio', ''), height=100)
        website = st.text_input("Website", st.session_state.portfolio_data.get('website', ''))
        
        # Profile Image Upload
        st.markdown("#### Profile Image")
        profile_image = st.file_uploader("Upload Profile Image", type=['jpg', 'jpeg', 'png', 'gif'])
        if profile_image:
            # Save uploaded image
            img_dir = Path("uploads/profile_images")
            img_dir.mkdir(parents=True, exist_ok=True)
            img_path = img_dir / f"{uuid.uuid4().hex}_{profile_image.name}"
            with open(img_path, "wb") as f:
                f.write(profile_image.getbuffer())
            st.session_state.portfolio_data['profile_image'] = str(img_path)
            st.image(img_path, width=150)
        
        # PDF CV Upload
        st.markdown("#### Upload CV (PDF)")
        pdf_cv = st.file_uploader("Upload your CV PDF", type=['pdf'])
        if pdf_cv:
            # Extract information from PDF
            with st.spinner("Extracting information from PDF..."):
                text = extract_text_from_pdf(pdf_cv)
                parsed_data = parse_cv_text(text)
                
                # Auto-fill fields
                if parsed_data['full_name'] and not full_name:
                    full_name = parsed_data['full_name']
                if parsed_data['profession'] and not profession:
                    profession = parsed_data['profession']
                if parsed_data['email'] and not email:
                    email = parsed_data['email']
                if parsed_data['phone'] and not phone:
                    phone = parsed_data['phone']
                
                # Save PDF
                pdf_dir = Path("uploads/cv_pdfs")
                pdf_dir.mkdir(parents=True, exist_ok=True)
                pdf_path = pdf_dir / f"{uuid.uuid4().hex}_{pdf_cv.name}"
                with open(pdf_path, "wb") as f:
                    f.write(pdf_cv.getbuffer())
                st.session_state.portfolio_data['pdf_cv'] = str(pdf_path)
                
                st.success("PDF processed successfully! Information extracted.")
        
        # Experience Section
        st.markdown("#### Work Experience")
        experiences = st.session_state.portfolio_data.get('experiences', [])
        
        # Add new experience
        if st.button("Add Experience"):
            experiences.append({
                'title': '', 'company': '', 'start_date': '', 'end_date': '', 
                'current': False, 'description': '', 'achievements': []
            })
        
        # Display existing experiences
        for i, exp in enumerate(experiences):
            with st.expander(f"Experience {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    exp['title'] = st.text_input("Job Title", exp.get('title', ''), key=f"exp_title_{i}")
                    exp['company'] = st.text_input("Company", exp.get('company', ''), key=f"exp_company_{i}")
                    exp['start_date'] = st.text_input("Start Date", exp.get('start_date', ''), key=f"exp_start_{i}")
                with col2:
                    exp['current'] = st.checkbox("Current Position", exp.get('current', False), key=f"exp_current_{i}")
                    if not exp['current']:
                        exp['end_date'] = st.text_input("End Date", exp.get('end_date', ''), key=f"exp_end_{i}")
                exp['description'] = st.text_area("Description", exp.get('description', ''), key=f"exp_desc_{i}", height=100)
                
                if st.button("Remove", key=f"remove_exp_{i}"):
                    experiences.pop(i)
                    st.experimental_rerun()
        
        st.session_state.portfolio_data['experiences'] = experiences
        
        # Education Section
        st.markdown("#### Education")
        educations = st.session_state.portfolio_data.get('educations', [])
        
        if st.button("Add Education"):
            educations.append({
                'degree': '', 'institution': '', 'field_of_study': '', 
                'start_date': '', 'end_date': '', 'grade': '', 'description': ''
            })
        
        for i, edu in enumerate(educations):
            with st.expander(f"Education {i+1}"):
                col1, col2 = st.columns(2)
                with col1:
                    edu['degree'] = st.text_input("Degree", edu.get('degree', ''), key=f"edu_degree_{i}")
                    edu['institution'] = st.text_input("Institution", edu.get('institution', ''), key=f"edu_institution_{i}")
                    edu['field_of_study'] = st.text_input("Field of Study", edu.get('field_of_study', ''), key=f"edu_field_{i}")
                with col2:
                    edu['start_date'] = st.text_input("Start Date", edu.get('start_date', ''), key=f"edu_start_{i}")
                    edu['end_date'] = st.text_input("End Date", edu.get('end_date', ''), key=f"edu_end_{i}")
                    edu['grade'] = st.text_input("Grade/GPA", edu.get('grade', ''), key=f"edu_grade_{i}")
                edu['description'] = st.text_area("Description", edu.get('description', ''), key=f"edu_desc_{i}", height=80)
                
                if st.button("Remove", key=f"remove_edu_{i}"):
                    educations.pop(i)
                    st.experimental_rerun()
        
        st.session_state.portfolio_data['educations'] = educations
        
        # Skills Section
        st.markdown("#### Skills")
        skills = st.session_state.portfolio_data.get('skills', [])
        
        if st.button("Add Skill"):
            skills.append({'name': '', 'category': '', 'level': 3, 'years_experience': 0})
        
        for i, skill in enumerate(skills):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                skill['name'] = st.text_input("Skill Name", skill.get('name', ''), key=f"skill_name_{i}")
            with col2:
                skill['category'] = st.text_input("Category", skill.get('category', ''), key=f"skill_cat_{i}")
            with col3:
                skill['level'] = st.slider("Level", 1, 5, skill.get('level', 3), key=f"skill_level_{i}")
            
            if st.button("Remove", key=f"remove_skill_{i}"):
                skills.pop(i)
                st.experimental_rerun()
        
        st.session_state.portfolio_data['skills'] = skills
        
        # Projects Section
        st.markdown("#### Projects")
        projects = st.session_state.portfolio_data.get('projects', [])
        
        if st.button("Add Project"):
            projects.append({
                'name': '', 'description': '', 'technologies': [], 
                'link': '', 'github_link': '', 'demo_link': '', 'featured': False
            })
        
        for i, project in enumerate(projects):
            with st.expander(f"Project {i+1}"):
                project['name'] = st.text_input("Project Name", project.get('name', ''), key=f"proj_name_{i}")
                project['description'] = st.text_area("Description", project.get('description', ''), key=f"proj_desc_{i}", height=100)
                project['technologies'] = st.text_input("Technologies (comma-separated)", 
                                                       ', '.join(project.get('technologies', [])), 
                                                       key=f"proj_tech_{i}").split(', ')
                col1, col2 = st.columns(2)
                with col1:
                    project['link'] = st.text_input("Project Link", project.get('link', ''), key=f"proj_link_{i}")
                    project['github_link'] = st.text_input("GitHub Link", project.get('github_link', ''), key=f"proj_github_{i}")
                with col2:
                    project['demo_link'] = st.text_input("Demo Link", project.get('demo_link', ''), key=f"proj_demo_{i}")
                    project['featured'] = st.checkbox("Featured Project", project.get('featured', False), key=f"proj_featured_{i}")
                
                if st.button("Remove", key=f"remove_proj_{i}"):
                    projects.pop(i)
                    st.experimental_rerun()
        
        st.session_state.portfolio_data['projects'] = projects
        
        # Social Links
        st.markdown("#### Social Links")
        social_links = st.session_state.portfolio_data.get('social_links', [])
        
        if st.button("Add Social Link"):
            social_links.append({'platform': '', 'url': ''})
        
        for i, link in enumerate(social_links):
            col1, col2 = st.columns(2)
            with col1:
                link['platform'] = st.selectbox("Platform", 
                                               ['LinkedIn', 'GitHub', 'Twitter', 'Facebook', 'Instagram', 'YouTube'],
                                               key=f"social_platform_{i}")
            with col2:
                link['url'] = st.text_input("URL", link.get('url', ''), key=f"social_url_{i}")
            
            if st.button("Remove", key=f"remove_social_{i}"):
                social_links.pop(i)
                st.experimental_rerun()
        
        st.session_state.portfolio_data['social_links'] = social_links
        
        # Privacy Settings
        st.markdown("#### Privacy Settings")
        is_public = st.checkbox("Make portfolio public", st.session_state.portfolio_data.get('is_public', True))
        
        # Submit button
        submitted = st.form_submit_button("Save Portfolio")
        
        if submitted:
            # Update portfolio data
            st.session_state.portfolio_data.update({
                'title': title,
                'full_name': full_name,
                'profession': profession,
                'email': email,
                'phone': phone,
                'location': location,
                'bio': bio,
                'website': website,
                'design_template': design_template,
                'theme_color': theme_color,
                'is_public': is_public
            })
            
            # Save to database
            portfolio_id = save_portfolio(st.session_state.portfolio_data)
            st.session_state.current_portfolio = portfolio_id
            
            st.success("Portfolio saved successfully!")
            st.balloons()
            
            # Clear edit mode
            st.session_state.edit_mode = False

# Main Application
def main():
    """Main application entry point"""
    init_database()
    init_session_state()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("# PortfolioBuilder Pro")
        st.markdown("---")
        
        if st.session_state.user_id:
            st.markdown(f"Welcome, **{st.session_state.username}**!")
            st.markdown("---")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["Home", "Portfolio Builder", "My Portfolios", "Explore", "Analytics", "Settings"],
            icons=["house", "pencil-square", "folder", "compass", "graph-up", "gear"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
        )
        
        st.markdown("---")
        
        if st.session_state.user_id:
            if st.button("Logout", use_container_width=True):
                st.session_state.user_id = None
                st.session_state.username = None
                st.experimental_rerun()
        else:
            if st.button("Login", use_container_width=True):
                selected = "Login"
            if st.button("Register", use_container_width=True):
                selected = "Register"
    
    # Main content
    if not st.session_state.user_id and selected not in ["Login", "Register"]:
        selected = "Home"
    
    if selected == "Home":
        st.markdown("""
        <div class='main-header'>
            <h1>Create Your Professional Portfolio</h1>
            <p>Showcase your work, skills, and experience in a beautiful way</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features section
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h2>📄</h2>
                <h3>Upload CV PDF</h3>
                <p>Automatically extract information</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h2>🎨</h2>
                <h3>Multiple Designs</h3>
                <p>Choose from various templates</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h2>🎥</h2>
                <h3>Video CV</h3>
                <p>Create interactive videos</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div style='text-align: center; padding: 1rem;'>
                <h2>💾</h2>
                <h3>Easy Download</h3>
                <p>Download your portfolio</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Featured portfolios
        st.markdown("## Featured Portfolios")
        featured_portfolios = get_public_portfolios(6)
        
        if featured_portfolios:
            cols = st.columns(3)
            for i, portfolio in enumerate(featured_portfolios):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div class='portfolio-card'>
                            <h3>{portfolio.get('full_name', 'Anonymous')}</h3>
                            <p>{portfolio.get('profession', 'Professional')}</p>
                            <p>👁️ {portfolio.get('view_count', 0)} views</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"View Portfolio", key=f"view_{portfolio['id']}"):
                            st.session_state.view_portfolio = portfolio['id']
                            st.experimental_rerun()
        else:
            st.info("No portfolios yet. Be the first to create one!")
        
        st.markdown("---")
        
        # Call to action
        if not st.session_state.user_id:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 10px;'>
                    <h2 style='color: white;'>Ready to showcase your work?</h2>
                    <p style='color: white;'>Join thousands of professionals who have created their portfolio with us.</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Get Started Now", use_container_width=True):
                    st.session_state.selected = "Register"
                    st.experimental_rerun()
    
    elif selected == "Portfolio Builder":
        st.markdown("# Portfolio Builder")
        portfolio_builder_form()
    
    elif selected == "My Portfolios":
        st.markdown("# My Portfolios")
        
        portfolios = get_user_portfolios(st.session_state.user_id)
        
        if portfolios:
            for portfolio in portfolios:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{portfolio.get('title', 'Untitled')}**")
                        st.markdown(f"*{portfolio.get('profession', 'Professional')}*")
                        st.markdown(f"Created: {portfolio.get('created_at', '')[:10]}")
                    with col2:
                        if st.button("Edit", key=f"edit_{portfolio['id']}"):
                            st.session_state.edit_mode = True
                            st.session_state.current_portfolio = portfolio['id']
                            st.session_state.portfolio_data = portfolio
                            st.session_state.selected = "Portfolio Builder"
                            st.experimental_rerun()
                    with col3:
                        if st.button("View", key=f"view_my_{portfolio['id']}"):
                            st.session_state.view_portfolio = portfolio['id']
                            st.experimental_rerun()
                    st.markdown("---")
        else:
            st.info("You haven't created any portfolios yet. Click 'Portfolio Builder' to create one!")
    
    elif selected == "Explore":
        st.markdown("# Explore Portfolios")
        
        # Search and filters
        search_query = st.text_input("Search by name, profession, or skills")
        
        portfolios = get_public_portfolios(limit=50)
        
        if search_query:
            portfolios = [p for p in portfolios if 
                         search_query.lower() in p.get('full_name', '').lower() or
                         search_query.lower() in p.get('profession', '').lower() or
                         search_query.lower() in p.get('bio', '').lower()]
        
        if portfolios:
            cols = st.columns(3)
            for i, portfolio in enumerate(portfolios):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(f"""
                        <div class='portfolio-card'>
                            <h3>{portfolio.get('full_name', 'Anonymous')}</h3>
                            <p>{portfolio.get('profession', 'Professional')}</p>
                            <p>{portfolio.get('bio', '')[:100]}...</p>
                            <p>👁️ {portfolio.get('view_count', 0)} views</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"View Portfolio", key=f"explore_{portfolio['id']}"):
                            st.session_state.view_portfolio = portfolio['id']
                            st.experimental_rerun()
        else:
            st.info("No portfolios found.")
    
    elif selected == "Analytics":
        st.markdown("# Portfolio Analytics")
        
        portfolios = get_user_portfolios(st.session_state.user_id)
        
        if portfolios:
            selected_portfolio = st.selectbox("Select Portfolio", portfolios, format_func=lambda x: x.get('title', 'Untitled'))
            
            if selected_portfolio:
                # Display analytics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Views", selected_portfolio.get('view_count', 0))
                with col2:
                    st.metric("Total Likes", selected_portfolio.get('like_count', 0))
                with col3:
                    st.metric("Portfolio Age", 
                             f"{(datetime.now() - datetime.fromisoformat(selected_portfolio['created_at'])).days} days")
                
                # View trend chart
                st.markdown("### View Trend")
                dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
                views = np.random.randint(0, 50, size=len(dates))
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=views, mode='lines+markers', name='Views'))
                fig.update_layout(title='Daily Views (Last 30 Days)', xaxis_title='Date', yaxis_title='Views')
                st.plotly_chart(fig, use_container_width=True)
                
                # Download portfolio
                st.markdown("### Download Portfolio")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Download as PDF", use_container_width=True):
                        pdf_buffer = generate_pdf_cv(selected_portfolio)
                        st.download_button(
                            label="Download PDF",
                            data=pdf_buffer,
                            file_name=f"{selected_portfolio.get('full_name', 'portfolio')}_CV.pdf",
                            mime="application/pdf"
                        )
                with col2:
                    if st.button("Generate Video CV", use_container_width=True):
                        with st.spinner("Generating video CV..."):
                            video_path = f"video_cv_{selected_portfolio['id']}.mp4"
                            if create_video_cv(selected_portfolio, video_path):
                                st.success("Video CV generated successfully!")
                                with open(video_path, "rb") as f:
                                    st.download_button("Download Video CV", f, file_name="video_cv.mp4")
                with col3:
                    st.download_button(
                        label="Download as HTML",
                        data=f"<html><body><h1>{selected_portfolio.get('full_name', 'Portfolio')}</h1></body></html>",
                        file_name="portfolio.html",
                        mime="text/html"
                    )
        else:
            st.info("Create a portfolio first to see analytics.")
    
    elif selected == "Settings":
        st.markdown("# Settings")
        
        tab1, tab2, tab3 = st.tabs(["Profile", "Security", "Notifications"])
        
        with tab1:
            st.markdown("### Profile Settings")
            st.text_input("Username", st.session_state.username, disabled=True)
            email = st.text_input("Email", "")
            full_name = st.text_input("Full Name", "")
            bio = st.text_area("Bio", "", height=100)
            
            if st.button("Update Profile"):
                st.success("Profile updated successfully!")
        
        with tab2:
            st.markdown("### Security Settings")
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.button("Change Password"):
                if new_password == confirm_password:
                    st.success("Password changed successfully!")
                else:
                    st.error("Passwords do not match!")
            
            st.markdown("### Two-Factor Authentication")
            if st.button("Enable 2FA"):
                st.info("2FA setup would be implemented here")
        
        with tab3:
            st.markdown("### Notification Settings")
            email_notifications = st.checkbox("Email notifications")
            portfolio_activity = st.checkbox("Portfolio activity alerts")
            newsletter = st.checkbox("Newsletter")
            
            if st.button("Save Notification Settings"):
                st.success("Notification settings saved!")
    
    elif selected == "Login":
        st.markdown("# Login")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                success, user_id, username = login_user(username, password)
                if success:
                    st.session_state.user_id = user_id
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password")
        
        st.markdown("---")
        st.markdown("Don't have an account? [Register here](#)")
        if st.button("Register"):
            st.session_state.selected = "Register"
            st.experimental_rerun()
    
    elif selected == "Register":
        st.markdown("# Register")
        
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters!")
                else:
                    success, user_id = register_user(username, email, password)
                    if success:
                        st.success("Registration successful! Please login.")
                        st.session_state.selected = "Login"
                        st.experimental_rerun()
                    else:
                        st.error("Username or email already exists!")
        
        st.markdown("---")
        st.markdown("Already have an account? [Login here](#)")
        if st.button("Login"):
            st.session_state.selected = "Login"
            st.experimental_rerun()
    
    # View portfolio modal
    if 'view_portfolio' in st.session_state:
        portfolio_id = st.session_state.view_portfolio
        portfolio = load_portfolio(portfolio_id)
        
        if portfolio:
            # Increment view count
            increment_view_count(portfolio_id)
            
            st.markdown("# Portfolio Preview")
            
            # Render based on template
            if portfolio.get('design_template') == 'modern':
                render_modern_portfolio(portfolio)
            elif portfolio.get('design_template') == 'classic':
                render_classic_portfolio(portfolio)
            elif portfolio.get('design_template') == 'creative':
                render_creative_portfolio(portfolio)
            else:
                render_minimal_portfolio(portfolio)
            
            # Social sharing buttons
            st.markdown("---")
            st.markdown("### Share this portfolio")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.button("📧 Email")
            with col2:
                st.button("🐦 Twitter")
            with col3:
                st.button("💼 LinkedIn")
            with col4:
                st.button("📱 Facebook")
            
            # Close button
            if st.button("Close Preview"):
                del st.session_state.view_portfolio
                st.experimental_rerun()

# Create necessary directories
def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'uploads/profile_images', 'uploads/cv_pdfs', 'uploads/videos']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    create_directories()
    main()