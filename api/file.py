"""UNUM file plugin api functionality."""
# coding=utf-8
import udatetime
from flask import jsonify, g, current_app, send_from_directory, abort, request
from aucr_app import db
from aucr_app.plugins.unum.models import UNUM
from aucr_app.plugins.apiv2.auth import token_auth
from aucr_app.plugins.apiv2.routes import api_page
from aucr_app.plugins.auth.models import Group
from aucr_app.plugins.analysis.routes import get_upload_file_hash


@api_page.route('/unum_file_report/<string:file_hash>', methods=['GET'])
@token_auth.login_required
def unum_file_report(file_hash):
    """Return group list API call."""
    _id = UNUM.query.filter_by(upload_file=file_hash).first()
    api_current_user = g.current_user
    group_access_value = Group.query.filter_by(username_id=api_current_user.id, groups_id=_id.group_access).first()
    if group_access_value:
        return jsonify(UNUM.query.get_or_404(_id.id).to_dict())
    else:
        error_data = {"error": "Not authorized to view this file.", "error_code": 403}
        return jsonify(error_data)


@api_page.route('/unum_file_download/<path:file_hash>')
@token_auth.login_required
def unum_file_download(file_hash):
    """Return group list API call."""
    _id = UNUM.query.filter_by(upload_file=file_hash).first()
    api_current_user = g.current_user
    group_access_value = Group.query.filter_by(username_id=api_current_user.id, groups_id=_id.group_access).first()
    if group_access_value:
        return send_from_directory(current_app.config['FILE_FOLDER'], file_hash, as_attachment=True)
    else:
        error_data = {"error": "Not authorized to view this file.", "error_code": 403}
        return jsonify(error_data)


@api_page.route('/unum_file_upload/', methods=['POST'])
@token_auth.login_required
def unum_file_upload():
    """Return group list API call."""
    request_args = request.args
    file = request.data
    if len(file) < 1:
        request_args = request.form
        file = request.files['filename']
    if '/' == request_args['filename'][-1:]:
        # Return 400 BAD REQUEST
        abort(400, 'no subdirectories directories allowed')
    if file:
        file_hash = get_upload_file_hash(file)
        duplicate_file = UNUM.query.filter_by(md5_hash=file_hash).first()
        if duplicate_file:
            error_data = {"error": "This file has already been uploaded.", "error_code": 500}
            return jsonify(error_data)

        new_upload = UNUM(description=request_args['description'], created_by=g.current_user.id,
                          classification=request_args['classification'],
                          group_access=request_args['group_access'],
                          created_time_stamp=udatetime.utcnow(),
                          modify_time_stamp=udatetime.utcnow(),
                          md5_hash=file_hash, file_name=str(request_args['filename']))
        db.session.add(new_upload)
        db.session.commit()
        return jsonify({"file_id": new_upload.id, "md5": file_hash})
    error_data = {"error": "This file type is now allowed.", "error_code": 503}
    return jsonify(error_data)
