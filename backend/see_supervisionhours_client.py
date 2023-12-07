from flask import render_template


@app.route('/edit_time_entry')
def edit_time_entry():
    return render_template('edit_time_entry.html')
