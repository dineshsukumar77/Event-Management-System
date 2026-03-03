import json
import os
import sys

# Ensure project root is on sys.path to import app
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app import create_app

INPUT_DIR = os.path.join(PROJECT_ROOT, 'data')


def main():
    app = create_app()
    with app.app_context():
        db = app.mongo_db
        if not os.path.isdir(INPUT_DIR):
            print(f'No data folder found at {INPUT_DIR}')
            return
        collections = ['users', 'events', 'hotels', 'caterings', 'vendors', 'bookings']
        for name in collections:
            path = os.path.join(INPUT_DIR, f'{name}.json')
            if not os.path.isfile(path):
                print(f'Skipping {name}: {path} not found')
                continue
            with open(path, 'r', encoding='utf-8') as f:
                docs = json.load(f)
            if not isinstance(docs, list):
                print(f'{name}: invalid JSON format (expected list)')
                continue
            # Convert _id strings back to ObjectId if present
            from bson import ObjectId
            for d in docs:
                if isinstance(d, dict) and '_id' in d and isinstance(d['_id'], dict) and '$oid' in d['_id']:
                    d['_id'] = ObjectId(d['_id']['$oid'])
                elif isinstance(d, dict) and '_id' in d and isinstance(d['_id'], str):
                    try:
                        d['_id'] = ObjectId(d['_id'])
                    except Exception:
                        pass
            if docs:
                db[name].delete_many({})
                db[name].insert_many(docs)
            print(f'Imported {len(docs)} docs into {name}')


if __name__ == '__main__':
    main()


