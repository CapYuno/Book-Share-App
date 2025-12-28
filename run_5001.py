"""Entry point for the BookShare Flask application - Port 5001."""
import os
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
