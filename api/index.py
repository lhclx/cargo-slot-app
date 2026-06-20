import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app

def handler(request, context=None):
    return app(request.environ, start_response=None)
