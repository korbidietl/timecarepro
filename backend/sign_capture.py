from flask import Blueprint, request, render_template, session

signature_blueprint = Blueprint('siganture', __name__)


@signature_blueprint.route('/sign_capture', methods=['POST'])
def capture_signature(target_function):
    if request.method == 'POST':
        data = request.json
        signature_data = data.get('signatureData', '')
        target_function = request.form.get('origin_function')


        if target_function == 'create_time_entry':
            return render_template('create_time_entry.html', signature_data=signature_data)
        elif target_function == 'edit_time_entry':
            return render_template('edit_time_entry.html', signature_data=signature_data)
        elif target_function == #FV100:
            return render_template(#FV100, signature_date=signature_data)