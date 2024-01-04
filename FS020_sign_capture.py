from flask import Blueprint, request, render_template, session, jsonify, redirect

signature_blueprint = Blueprint('siganture', __name__)


@signature_blueprint.route('/sign_capture/<int:signature_index>', methods=['POST', 'GET'])
def capture_signature(signature_index):
    if request.method == 'POST':
        signature_data = request.form.get('signatureData')
        h=session[f'signature_data_{signature_index}'] = signature_data
        print(h)

        return redirect(session.pop('url', None))

    else:
        return render_template('FS020_sign_capture.html', signature_index=signature_index)
