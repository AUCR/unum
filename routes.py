# coding=utf-8
import udatetime
from aucr_app import db
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory, g
from flask_login import login_required, current_user
from aucr_app.plugins.auth.models import Groups, Group
from aucr_app.plugins.unum.forms import UploadFile, EditUploadFile, Unum, UNUMSearchForm
from aucr_app.plugins.unum.globals import AVAILABLE_CHOICES
from aucr_app.plugins.unum.models import UNUM, Classification
from aucr_app.plugins.analysis.routes import get_upload_file_hash
from aucr_app.plugins.analysis.file.upload import allowed_file
from aucr_app.plugins.analysis.file.zip import encrypt_zip_file
from werkzeug.utils import secure_filename
from flask_babel import get_locale

unum = Blueprint('unum', __name__, template_folder='templates')


@unum.before_app_request
def before_request():
    """Set user last seen time user."""
    if current_user.is_authenticated:
        g.unum_search_form = UNUMSearchForm()
    g.locale = str(get_locale())


@unum.route('/search')
@login_required
def unum_search():
    """UNUM search plugin flask blueprint."""
    if not g.unum_search_form.validate():
        return redirect(url_for('unum.unum_plugin_route'))
    page = request.args.get('page', 1, type=int) or 1
    posts, total = UNUM.search(g.unum_search_form.q.data, page, int(current_app.config['POSTS_PER_PAGE']))
    search_uploaded_files, total = \
        UNUM.search(g.unum_search_form.q.data, page, int(current_app.config['POSTS_PER_PAGE']))
    next_url = url_for('unum.unum_search', q=g.unum_search_form.q.data, page=page + 1) \
        if total["value"] > page * int(current_app.config['POSTS_PER_PAGE']) else None
    prev_url = url_for('unum.unum_search', q=g.unum_search_form.q.data, page=page - 1) if page > 1 else None
    return render_template('unum_search.html', title='UNUM Search', page=page, search_url='unum.unum_search',
                           next_url=next_url, prev_url=prev_url, posts=posts, file_results=search_uploaded_files)


@unum.route('/unum_file_download/<path:md5_hash>')
@login_required
def unum_file_download(md5_hash):
    """File Download web call."""
    _id = UNUM.query.filter_by(md5_hash=md5_hash).first()
    group_access_value = Group.query.filter_by(username_id=current_user.id, groups_id=_id.group_access).first()
    if group_access_value:
        encrypt_zip_file("infected", str(md5_hash + ".zip"), [current_app.config['FILE_FOLDER'] + md5_hash])
        return send_from_directory("/tmp/", str(md5_hash + ".zip"), as_attachment=True)


@unum.route('/unum', methods=['GET', 'POST'])
@login_required
def unum_plugin_route():
    """the tasks function returns the plugin framework for the unum default task view"""
    # TODO show current unum in the database
    if request.method == 'POST':
        return redirect("/unum/create")
    form = Unum(request.form)
    classification_choices = []
    for items in Classification.query.all():
        classification_choices.append((int(items.id), items.classification))
    page = request.args.get('page', 1, type=int) or 1
    count = page * 10
    upload_dict = {}
    total = 0
    while total < 10:
        total += 1
        id_item = count - 10 + total
        item = UNUM.query.filter_by(id=id_item).first()
        if item:
            group_ids = Group.query.filter_by(username_id=current_user.id).all()
            for group_items in group_ids:
                if item.group_access == group_items.groups_id:
                    if len(item.file_name) >= 32:
                        table_file_name_formatted = str(item.file_name[:26] + "..." + item.file_name[-8:])
                    else:
                        table_file_name_formatted = item.file_name
                    classification_value = Classification.query.filter_by(id=item.classification).first()
                    item_dict = {"id": item.id, "description": item.description, "md5_hash": item.md5_hash,
                                 "file_name": table_file_name_formatted,
                                 "classification": classification_value.classification}
                    upload_dict[str(item.id)] = item_dict
    prev_url = '?page=' + str(page - 1)
    next_url = '?page=' + str(page + 1)
    return render_template('unum.html', title='Unum Search', page=page, table_dict=upload_dict,
                           form=form, search_url='unum.unum_search', next_url=next_url, prev_url=prev_url)


@unum.route('/create', methods=['GET', 'POST'])
@login_required
def unum_file_route():
    """Create upload default view."""
    group_info = Groups.query.all()
    if request.method == 'POST':
        form = UploadFile(request.form)
        form.classification.choices = AVAILABLE_CHOICES
        md5_hash = None
        if form.validate_on_submit():
            try:
                file = request.files['file']
            except KeyError:
                file = None
            if file and allowed_file(file.filename):
                secure_filename(file.filename)
                md5_hash = get_upload_file_hash(file)
            classification_selection = None
            for items in AVAILABLE_CHOICES:
                if items[0] == form.classification.data[0]:
                    classification_selection = items
            duplicate_file = UNUM.query.filter_by(md5_hash=md5_hash).first()
            if duplicate_file:
                flash("The upload file has already been uploaded.")
                return redirect(url_for('unum.unum_plugin_route'))
            new_upload = UNUM(description=form.description.data, created_by=current_user.id,
                              classification=classification_selection[0], file_name=str(file.filename),
                              group_access=form.group_access.data[0], created_time_stamp=udatetime.utcnow(),
                              modify_time_stamp=udatetime.utcnow(),
                              md5_hash=md5_hash)
            db.session.add(new_upload)
            db.session.commit()
            flash("The upload file has been created and we started processing it for you.")
            return redirect(url_for('unum.unum_plugin_route'))
    form = UploadFile(request.form)
    return render_template('unum_upload_file.html', title='Upload New File', form=form, groups=group_info,
                           classification=AVAILABLE_CHOICES)


@unum.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_upload_file_route():
    """Edit Uploaded File view."""
    group_info = Groups.query.all()
    submitted_upload_id = request.args.get("id")
    upload = UNUM.query.filter_by(id=submitted_upload_id).first()
    group_access_value = Group.query.filter_by(username_id=current_user.id, groups_id=upload.group_access).first()
    if group_access_value:
        group_ids = Group.query.filter_by(username_id=current_user.id).all()
        user_groups = []
        for user_group in group_ids:
            user_groups.append(user_group.groups_id)
        group_choices = []
        for group in Groups.query.all():
            group_choices.append((int(group.id), group.name))
        if request.method == 'POST':
            if upload:
                form = EditUploadFile(request.form)
                if form.validate_on_submit():
                    if upload is not None:
                        upload.description = request.form["description"]
                        upload.classification = int(request.form["classification"])
                        upload.group_access = int(request.form["groups_access"])
                        db.session.commit()
            return redirect(url_for('unum.unum_plugin_route'))
        if request.method == "GET":
            if upload:
                form = EditUploadFile(upload)
                assigned_group_value = None
                classification_choices = []
                assigned_classification_value = None
                for items in Classification.query.all():
                    classification_choices.append((int(items.id), items.classification))
                for items in group_choices:
                    if items[0] == upload.group_access:
                        assigned_group_value = items[1]
                for items in classification_choices:
                    if items[0] == upload.classification:
                        assigned_classification_value = items[1]
                table_dict = {"id": upload.id, "description": upload.description, "md5": upload.md5_hash,
                              "classification": assigned_classification_value, "group_access": assigned_group_value}
                return render_template('edit_upload_file.html', title='Edit Upload File', form=form, groups=group_info,
                                       classification=AVAILABLE_CHOICES, table_dict=table_dict,
                                       groups_access=group_choices)
            else:
                return unum_plugin_route()
    flash("You don't have permissions to edit this object! Please ask an admin for assistance.")
    return unum_plugin_route()
