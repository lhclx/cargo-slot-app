# -*- coding: utf-8 -*-
import json, os, datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
DATA_FILE = os.path.join(DATA_DIR, 'slots.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/api/slots', methods=['GET'])
def get_slots():
    data = load_data()
    for key in ['status','carrier','operator','port']:
        val = request.args.get(key)
        if val:
            if key == 'port':
                data = [s for s in data if s.get('destination_port') == val or s.get('loading_port') == val]
            else:
                fld = {'status':'status','carrier':'carrier','operator':'operator'}[key]
                data = [s for s in data if s.get(fld) == val]
    # client-side search
    q = request.args.get('q','').lower().strip()
    if q:
        data = [s for s in data if q in str(s.get('so_no','')).lower() or q in str(s.get('booking_ref','')).lower() or q in str(s.get('client','')).lower()]
    return jsonify(data)

@app.route('/api/slots', methods=['POST'])
def add_slot():
    data = load_data()
    slot = request.get_json()
    slot['id'] = max([s['id'] for s in data], default=0) + 1
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    slot['created_at'] = now
    slot['updated_at'] = now
    data.append(slot)
    save_data(data)
    return jsonify(slot), 201

@app.route('/api/slots/<int:slot_id>', methods=['PUT'])
def update_slot(slot_id):
    data = load_data()
    for i, s in enumerate(data):
        if s['id'] == slot_id:
            upd = request.get_json()
            upd['updated_at'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            upd['id'] = slot_id
            upd['created_at'] = s.get('created_at', '')
            data[i] = upd
            save_data(data)
            return jsonify(upd)
    return jsonify({'error': 'not found'}), 404

@app.route('/api/slots/<int:slot_id>', methods=['DELETE'])
def delete_slot(slot_id):
    data = load_data()
    new_data = [s for s in data if s['id'] != slot_id]
    if len(new_data) == len(data):
        return jsonify({'error': 'not found'}), 404
    save_data(new_data)
    return jsonify({'ok': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    stats = {'total': len(data), 'by_status': {}, 'by_carrier': {}, 'by_destination': {}, 'by_operator': {}}
    for s in data:
        for fld, key in [('status','by_status'),('carrier','by_carrier'),('destination_port','by_destination'),('operator','by_operator')]:
            v = s.get(fld, '未知')
            stats[key][v] = stats[key].get(v, 0) + 1
    return jsonify(stats)

@app.route('/')
def index():
    return send_html()

def send_html():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html'), 'r', encoding='utf-8') as f:
        return f.read(), {'Content-Type': 'text/html; charset=utf-8'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print(f"  Cargo Slot Management System")
    print(f"  Port: {port}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False)

# For Render.com gunicorn compatibility
app = app
