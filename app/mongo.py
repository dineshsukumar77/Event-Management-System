from typing import Any, Dict

from bson import ObjectId


def to_str_id(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Return a shallow-copied dict where _id is converted to string id for templates."""
    if not doc:
        return doc
    d = dict(doc)
    if d.get('_id') is not None:
        d['id'] = str(d['_id'])
    return d


def to_object_id(id_str: str) -> ObjectId:
    return ObjectId(id_str)


