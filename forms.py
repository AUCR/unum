"""AUCR upload plugin default page forms."""
# coding=utf-8
from flask import request
from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, SelectMultipleField, IntegerField, StringField
from flask_babel import lazy_gettext as _l
from wtforms.validators import Length, DataRequired
from aucr_app.plugins.auth.auth_globals import AVAILABLE_CHOICES
from aucr_app.plugins.unum.unum_globals import CLASSIFICATION_AVAILABLE_CHOICES


class UNUMSearchForm(FlaskForm):
    """SearchForm wtf search form builder."""
    q = StringField(_l('unum_search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta.csrf' not in kwargs:
            kwargs['meta.csrf'] = False
        super(UNUMSearchForm, self).__init__(*args, **kwargs)


class UploadFile(FlaskForm):
    """Upload New File Form."""

    description = TextAreaField(_l('Description'), validators=[Length(min=0, max=256)])
    classification = SelectMultipleField('Classification', choices=CLASSIFICATION_AVAILABLE_CHOICES)
    group_access = SelectMultipleField(_l('Group Access'), choices=AVAILABLE_CHOICES)
    submit = SubmitField(_l('Create'))


class EditUploadFile(FlaskForm):
    """Edit user profile settings."""

    upload_id = IntegerField(_l('Upload ID'), validators=[Length(min=0, max=12)])
    description = TextAreaField(_l('Description'), validators=[Length(min=0, max=256)])
    classification = SelectMultipleField('Classification', choices=CLASSIFICATION_AVAILABLE_CHOICES)
    group_access = SelectMultipleField(_l('Group Access'), choices=AVAILABLE_CHOICES)
    submit = SubmitField(_l('Save'))

    def __init__(self, upload, *args, **kwargs):
        """Edit user profile init self and return username."""
        super(EditUploadFile, self).__init__(*args, **kwargs)
        try:
            self.upload_id = upload.id
            self.description = upload.description
            self.classification = upload.classification
            self.group_access = upload.group_access
        except:
            self.description = upload["description"]
            self.classification = upload["classification"]
            self.group_access = upload["groups_access"]


class SaveUploadFile(FlaskForm):
    """Save upload Form."""

    description = TextAreaField(_l('Description'), validators=[Length(min=0, max=256)])
    submit = SubmitField(_l('Save'))

    def __init__(self, upload, *args, **kwargs):
        """Edit user profile init self and return File Info."""
        super(SaveUploadFile, self).__init__(*args, **kwargs)
        self.description = upload.description


class Unum(FlaskForm):
    """Upload New File Form."""

    uploadnewfile = SubmitField(_l("Upload New File"))
