from flask import Blueprint, request, render_template, session

signature_blueprint = Blueprint('siganture', __name__)


@signature_blueprint.route('/sign_capture', methods=['POST','GET'])
def capture_signature():
    if request.method == 'POST':
        data = request.json
        signature_data = data.get('signatureData', '')
        target_function = request.form.get('origin_function')

        if target_function == 'create_time_entry':
            return render_template('create_time_entry.html', signature_data=signature_data)
        elif target_function == 'edit_time_entry':
            return render_template('edit_time_entry.html', signature_data=signature_data)
        elif target_function == 'login':  # FV100:
            return render_template('login')  # FV100, signature_date=signature_data)

    else:
        return render_template('/sign_capture.html')