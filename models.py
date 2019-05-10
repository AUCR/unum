"""db.py is the unum plugin database library for all task plugins to use"""
# coding=utf-8
import udatetime as datetime
from aucr_app import db
from aucr_app.plugins.auth.models import SearchableMixin, PaginatedAPIMixin
from yaml_info.yamlinfo import YamlInfo


class UNUM(SearchableMixin, PaginatedAPIMixin, db.Model):
    """Upload File data default table for aucr."""

    __searchable__ = ['id', 'description', 'classification', 'created_by', 'md5_hash', 'file_name',
                      'created_time_stamp']
    __tablename__ = 'unum'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(256), index=True)
    created_time_stamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    modify_time_stamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    classification = db.Column(db.Integer, db.ForeignKey('classification.id'))
    file_name = db.Column(db.String(512))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_access = db.Column(db.Integer, db.ForeignKey('groups.id'))
    md5_hash = db.Column(db.String(128), db.ForeignKey('uploaded_file_table.md5_hash'))

    def __repr__(self):
        return '<unum {}>'.format(self.md5_hash)

    def to_dict(self):
        """Return dictionary object type for API calls."""
        data = {
            'id': self.id,
            'md5_hash': self.md5_hash,
            'file_name': self.file_name,
            'description': self.description,
            'classification': self.classification,
            'last_seen': self.created_time_stamp.isoformat() + 'Z',
            'modify_time_stamp': self.modify_time_stamp.isoformat() + 'Z',
            'created_by': self.created_by,
            'group_access': self.group_access
        }
        return data


class Classification(db.Model):
    """Classification method data default table for aucr."""

    __tablename__ = 'classification'
    id = db.Column(db.Integer, primary_key=True)
    classification = db.Column(db.String(32), index=True)
    description = db.Column(db.String(256), index=True)
    time_stamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Classification {}>'.format(self.classification)


def insert_initial_classification_values(*args, **kwargs):
    """Insert Task category default database values from a yaml template file."""
    classification_run = YamlInfo("aucr_app/plugins/unum/classification.yml", "none", "none")
    classification_data = classification_run.get()
    for items in classification_data:
        new_classification_table_row = Classification(classification=items)
        db.session.add(new_classification_table_row)
        db.session.commit()


db.event.listen(Classification.__table__, 'after_create', insert_initial_classification_values)
