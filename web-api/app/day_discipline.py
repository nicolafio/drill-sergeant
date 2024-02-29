from flask import current_app as app, make_response

@app.route("/<int:year>/<int:month>/<int:day>/discipline", methods=['GET'])
def get_day_discipline(year, month, day):
    return make_response("1")
