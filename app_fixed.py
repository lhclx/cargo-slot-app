# -*- coding: utf-8 -*-
import json, os, datetime, base64, re, hashlib, secrets, time
from flask import Flask, request, jsonify, send_file, session, redirect
from flask_cors import CORS
import openpyxl
import requests as http_requests
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from io import BytesIO


def normalize_date(val):
    """标准化日期格式：去掉时间部分，只保留 YYYY-MM-DD"""
    if not val:
        return ''
    s = str(val).strip()
    m = re.match(r'(\d{4}-\d{2}-\d{2})', s)
    return m.group(1) if m else s


def get_week_number(etd_str, eta_str=None):
    """根据ETD/ETA计算自然周编号（ISO周）"""
    date_str = etd_str or eta_str or ''
    if not date_str:
        return ''
    m = re.match(r'(\d{4}-\d{2}-\d{2})', str(date_str))
    if not m:
        return ''
    try:
        d = datetime.datetime.strptime(m.group(1), '%Y-%m-%d')
        return 'W' + str(d.isocalendar()[1])
    except:
        return ''

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cargo-slot-dev-secret-key-change-in-production')
CORS(app, supports_credentials=True)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'slots.json')
TRASH_FILE = os.path.join(DATA_DIR, 'trash.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
