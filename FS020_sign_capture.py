from flask import Blueprint, request, render_template, session, jsonify

signature_blueprint = Blueprint('siganture', __name__)


@signature_blueprint.route('/sign_capture', methods=['POST', 'GET'])
def capture_signature():
    if request.method == 'POST':
        signature_data = request.form.get('signatureData')
        target_function = request.form.get('origin_function')

        if target_function == 'create_time_entry':
            return render_template('FMOF030_create_time_entry.html', signature_data=signature_data)
        elif target_function == 'edit_time_entry':
            return render_template('FMOF050_edit_time_entry.html', signature_data=signature_data)
        elif target_function == 'login':  # FV100:
            return render_template('FNAN010_login.html', signature_data=signature_data)  # FV100


    else:
        return render_template('FS020_sign_capture.html')
