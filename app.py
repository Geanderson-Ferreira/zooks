from flask import Flask, request, render_template, flash, session
from datetime import datetime, timedelta
from engines.find_reservation import find_reservation_dealer

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Necessário para usar flash messages e sessão


@app.route('/<rid>/find-reservation', methods=['GET', 'POST'])
def find_reservation(rid):
    return find_reservation_dealer(rid)

if __name__ == '__main__':
    app.run(debug=True)
