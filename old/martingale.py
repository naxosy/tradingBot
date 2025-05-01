import random

def run_simul(starting_bet) :
    iterations = 1
    current_bet = starting_bet

    losses = 0
    earnings = 0

    tirage = random.randint(0, 1)

    while tirage == 0 : #tirage perdant
        iterations += 1
        losses += current_bet # on a perdu le current bet
        current_bet = current_bet*2 # on rebet le double
        #print(f"Perdu : on a perdu au total {losses}, on parie maintenant {current_bet}")
        tirage = random.randint(0,1)

    losses += current_bet
    earnings = current_bet*2

    return iterations, losses, earnings

for i in range(10) :
    iterations, losses, earnings = run_simul(5)
    print(f"Simulation {i+1} : Won after {iterations} iterations, dépenses totales : {losses} pour un profit de {earnings-losses}")
