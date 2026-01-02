from dotenv import load_dotenv

load_dotenv()

from waitress import serve
from app import create_app

if __name__ == '__main__':
    print('Started Waitress web server on port 5000.')
    serve(create_app(), host = '127.0.0.1', port = 5000)
