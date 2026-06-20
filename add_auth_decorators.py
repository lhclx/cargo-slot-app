import re

path = r'C:\Users\Administrator\.qclaw\workspace\cargo-slot-app\app.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

# Skip if already decorated (check for require_auth/require_writer/require_admin after routes)
replacements = [
    ("@app.route('/api/slots', methods=['GET'])\n", "@app.route('/api/slots', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/stats/teu', methods=['GET'])\n", "@app.route('/api/stats/teu', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/stats/weeks', methods=['GET'])\n", "@app.route('/api/stats/weeks', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/slots', methods=['POST'])\n", "@app.route('/api/slots', methods=['POST'])\n@require_writer\n"),
    ("@app.route('/api/slots/<int:slot_id>', methods=['PUT'])\n", "@app.route('/api/slots/<int:slot_id>', methods=['PUT'])\n@require_writer\n"),
    ("@app.route('/api/slots/<int:slot_id>', methods=['DELETE'])\n", "@app.route('/api/slots/<int:slot_id>', methods=['DELETE'])\n@require_admin\n"),
    ("@app.route('/api/trash', methods=['GET'])\n", "@app.route('/api/trash', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/trash/<int:slot_id>/restore', methods=['POST'])\n", "@app.route('/api/trash/<int:slot_id>/restore', methods=['POST'])\n@require_admin\n"),
    ("@app.route('/api/trash/<int:slot_id>/permanent', methods=['DELETE'])\n", "@app.route('/api/trash/<int:slot_id>/permanent', methods=['DELETE'])\n@require_admin\n"),
    ("@app.route('/api/trash/clear', methods=['DELETE'])\n", "@app.route('/api/trash/clear', methods=['DELETE'])\n@require_admin\n"),
    ("@app.route('/api/slots/export', methods=['GET'])\n", "@app.route('/api/slots/export', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/stats', methods=['GET'])\n", "@app.route('/api/stats', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/template')\n", "@app.route('/api/template')\n@require_auth\n"),
    ("@app.route('/api/import', methods=['POST'])\n", "@app.route('/api/import', methods=['POST'])\n@require_writer\n"),
    ("@app.route('/api/recognize-so', methods=['POST'])\n", "@app.route('/api/recognize-so', methods=['POST'])\n@require_writer\n"),
    ("@app.route('/api/orders', methods=['GET'])\n", "@app.route('/api/orders', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/orders', methods=['POST'])\n", "@app.route('/api/orders', methods=['POST'])\n@require_writer\n"),
    ("@app.route('/api/orders/<int:order_id>', methods=['PUT'])\n", "@app.route('/api/orders/<int:order_id>', methods=['PUT'])\n@require_writer\n"),
    ("@app.route('/api/orders/<int:order_id>', methods=['DELETE'])\n", "@app.route('/api/orders/<int:order_id>', methods=['DELETE'])\n@require_admin\n"),
    ("@app.route('/api/logs/<int:order_id>', methods=['GET'])\n", "@app.route('/api/logs/<int:order_id>', methods=['GET'])\n@require_auth\n"),
    ("@app.route('/api/logs', methods=['POST'])\n", "@app.route('/api/logs', methods=['POST'])\n@require_writer\n"),
]

for old, new in replacements:
    if old not in text:
        print(f'MISSING: {old.strip()}')
    elif new in text:
        print(f'ALREADY: {old.strip()}')
    else:
        text = text.replace(old, new)
        print(f'ADDED: {old.strip()}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('DONE')
