from app import (
    create_app,
    database
)

app = create_app()

@app.after_request
def after_request(resp):
    resp.headers['Cache-Control'] = 'no-store'

    return resp

@app.before_first_request
def before_first_request():
    print('creating all tables')
    database.Base.metadata.create_all(bind=database.engine)
    app.db.commit()
