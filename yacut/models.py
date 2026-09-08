from datetime import datetime

from flask import url_for

from . import db
from .constants import ORIGINAL_LINK_MAX_LENGTH, SHORT_LINK_MAX_LENGTH


class URLMap(db.Model):
    API_TO_MODEL_MAPPING = {
        'url': 'original',
        'custom_id': 'short'
    }

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_LINK_MAX_LENGTH), nullable=False)
    short = db.Column(
        db.String(SHORT_LINK_MAX_LENGTH),
        unique=True,
        nullable=False
    )
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            url=self.original,
            short_link=url_for(
                'redirect_view',
                short=self.short,
                _external=True
            )
        )

    def from_dict(self, data):
        for key, attr in self.API_TO_MODEL_MAPPING.items():
            if key in data:
                setattr(self, attr, data[key])
