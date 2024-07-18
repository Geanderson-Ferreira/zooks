from flask import Flask, request, render_template, flash, session
from datetime import datetime, timedelta
from src.reservations import get_reservations_by_checkout_date, get_reservations_by_ids
from src.profiles import get_profiles_by_ids
from token_manager import Token

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # Necessário para usar flash messages e sessão

# Configurações de segurança
MAX_ATTEMPTS = 90
BLOCK_TIME = timedelta(minutes=5)  # Tempo de bloqueio em minutos
def resolve_from_form():
    pass


def find_reservation_dealer(rid):
    
    # Inicializa variáveis de tentativa na sessão
    if 'attempts' not in session:
        session['attempts'] = 0
        session['blocked_until'] = None
    session['blocked_until'] = None
    flash(session['blocked_until'])
    # Checa se o usuário está bloqueado
    if session['blocked_until'] and datetime.now() < session['blocked_until']:
        flash(f'Tentativas excedidas. Tente novamente após {session["blocked_until"].strftime("%H:%M:%S")}.')
        return render_template('find_reservation.html', reservations=[])
    


    #_______________CORE DA FUNCAO

    if request.method == 'POST':
        
        confirmation_number = request.form.get('confirmation_number')
        checkout_date = request.form.get('checkout_date')
        last_name = request.form.get('last_name')
        

        if not confirmation_number and not last_name:
            flash('Por favor, preencha pelo menos o Número de Confirmação ou o Sobrenome.')
            return render_template('find_reservation.html', reservations=[])

        # Filtrar json
        reservations_data = get_reservations_by_checkout_date(rid,checkout_date,Token().get_token())
        if not reservations_data:
            return render_template('find_reservation.html', reservations=[])
        if len(reservations_data) <= 0:
            return render_template('find_reservation.html', reservations=[])
        if confirmation_number:
            filter = [x for x in reservations_data
                      if x['reservationIdList'][0]['id'] == confirmation_number or
                      x.get('externalReferences',[{}])[0].get('id',{}) == confirmation_number]
        if last_name:
            pass

        if len(filter) != 1:
            return render_template('find_reservation.html', reservations=[])

        founded_reservation = filter[0]

        if founded_reservation['sharedGuests']:
            main_resv_id = [filter[0]['reservationIdList'][0]['id']]
            shares = [x['profileId']['id'] for x in founded_reservation['sharedGuests']]

            all_resvs_data = get_reservations_by_ids(rid, shares + main_resv_id, Token().get_token())

            dados = {
                "resv_ids": shares + main_resv_id,
                "prof_ids": [x['reservationGuest']['id'] for x in all_resvs_data],
                "total_adults": sum([x['roomStay']['adultCount'] for x in all_resvs_data]),
                "total_children": sum([x['roomStay']['childCount'] for x in all_resvs_data]),
                "all_resvs_data": all_resvs_data,
                "all_profs_data": get_profiles_by_ids([x['reservationGuest']['id'] for x in all_resvs_data], rid, Token().get_token())['profiles']['profileInfo']
            }

            return render_template('fill_data.html', dados=dados)
        


        ##----------- Melhorar

        if not reservations_data:
            session['attempts'] += 1
            flash(f'Nenhuma reserva encontrada. Tentativa {session["attempts"]}/{MAX_ATTEMPTS}.')

            if session['attempts'] >= MAX_ATTEMPTS:
                session['blocked_until'] = datetime.now() + BLOCK_TIME
                session['attempts'] = 0
                flash(f'Tentativas excedidas. Tente novamente após {session["blocked_until"].strftime("%H:%M:%S")}.')

            return render_template('find_reservation.html', reservations=[])

        # Reiniciar contagem de tentativas após um sucesso
        session['attempts'] = 0
        return render_template('find_reservation.html', reservations=reservations_data)

    return render_template('find_reservation.html', reservations=[])

if __name__ == '__main__':
    app.run(debug=True)
