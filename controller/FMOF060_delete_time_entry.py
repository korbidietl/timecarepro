from flask import Blueprint, request, flash, redirect, render_template, session, url_for
from model.mailserver_connection import send_email
from model.person import get_firstname_by_email, get_lastname_by_email
from model.zeiteintrag import check_booked, delete_zeiteintrag, get_email_by_zeiteintrag

delete_time_entry_blueprint = Blueprint("delete_te", __name__)


@delete_time_entry_blueprint.route('/delete_te/<int:zeiteintrags_id>', methods=['POST', 'GET'])
def delete_te(zeiteintrags_id):
    if 'user_id' in session:
        user_role = session['user_role']
        if user_role == 'Steuerbüro' or user_role == 'Sachbearbeiter/Kostenträger':
            flash('Sie sind nicht berechtigt diese Seite aufzurufen.')
            return redirect(session['secure_url'])
        else:
            # Rückleitung bei unerlaubter Seite
            session['secure_url'] = url_for('delete_te.delete_te', zeiteintrags_id=zeiteintrags_id)

            return_url = session.get('url')
            session_role = session.get('user_role')
            email = get_email_by_zeiteintrag(zeiteintrags_id)
            firstname = get_firstname_by_email(email)
            lastname = get_lastname_by_email(email)
            if request.method == 'POST':
                # Zeiteintrag wurde schon gebucht
                if check_booked(zeiteintrags_id):
                    error = ("Die Stundennachweise für diesen Monat wurden bereits gebucht."
                             " Der Eintrag kann nicht mehr gelöscht werden.")
                    flash(error, 'error')
                    render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id)

                else:
                    # Löschen der Zeiteinträge und dazugehörigen Fahrten
                    delete_zeiteintrag(zeiteintrags_id)
                    # wenn rolle verwaltung löscht, muss E-Mail gesendet werden
                    if session_role == "Verwaltung":
                        send_email_delete_time_entry(email, firstname, lastname, zeiteintrags_id)
                    # Erfolgsmeldung
                    success_message = "Eintrag erfolgreich gelöscht."
                    flash(success_message, 'success')

                    # Rückleitungen zur Herkunftsfunktion und löschen aus der Session
                    return redirect(session.pop('url', None))
            return render_template('FMOF060_delete_time_entry.html', zeiteintrags_id=zeiteintrags_id,
                                   return_url=return_url)
    else:
        # Wenn der Benutzer nicht angemeldet ist, umleiten zur Login-Seite
        flash('Sie müssen sich anmelden.')
        return redirect(url_for('login.login'))


def send_email_delete_time_entry(email, firstname, lastname, zeiteintrag_id):
    subject = "Gelöschter Zeiteintrag"
    body = (f"Sehr geehrte/r {firstname} {lastname}, \n\n"
            f"Ihr Zeiteintrag {zeiteintrag_id} wurde von der Verwaltung gelöscht.\n\n"
            f"Freundliche Grüße\n"
            f"Ihr TimeCare Pro-Team")
    send_email(email, subject, body)
