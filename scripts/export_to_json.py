import json
import os
import sys

# Ensure project root is on sys.path to import app
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app import create_app

OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'data')


def default(o):
    try:
        from bson import ObjectId
        if isinstance(o, ObjectId):
            return str(o)
    except Exception:
        pass
    raise TypeError


def main():
    app = create_app()
    with app.app_context():
        db = app.mongo_db
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        collections = ['users', 'events', 'hotels', 'caterings', 'vendors', 'bookings']
        for name in collections:
            data = list(db[name].find())
            out_path = os.path.abspath(os.path.join(OUTPUT_DIR, f'{name}.json'))
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=default)
            print(f'Wrote {len(data)} docs to {out_path}')


if __name__ == '__main__':
    main()
