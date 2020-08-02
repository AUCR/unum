# coding=utf-8
from sqlalchemy.exc import ProgrammingError
from yaml_info.yamlinfo import YamlInfo

from aucr_app import db, create_app
from aucr_app.plugins.unum.models import Classification


app = create_app()
db.init_app(app)
CLASSIFICATION_AVAILABLE_CHOICES = None
with app.app_context():
    count = 0
    items_available_choices_list = []
    try:
        classification_data = Classification.query.all()
    except:
        classification_data = YamlInfo("aucr_app/plugins/unum/classification.yml", "none", "none").get()
    for items in classification_data:
        count += 1
        new_list = (str(count), items)
        items_available_choices_list.append(new_list)
    CLASSIFICATION_AVAILABLE_CHOICES = items_available_choices_list
