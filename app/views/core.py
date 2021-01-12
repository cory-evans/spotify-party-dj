from flask import (
    Blueprint,
    render_template,
    current_app
)

from flask_login import current_user
from app import models

bp = Blueprint('core', __name__)

@bp.route('/')
def index():
    parties = current_app.db.query(models.PartyTable).all()
    parties_models = [
        models.Party.from_orm(p)
        for p in parties
    ]

    return render_template('index.html', user=current_user, parties=parties_models)
