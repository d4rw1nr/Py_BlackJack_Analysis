import Actions as act

# Strategies
def hard_total(deck: list, croupier: list, player: list):
    if player[1] >= 17:
        result=act.stand(deck, croupier, player)
        return(result)
    elif player[1] >= 13:
        if croupier[1] >= 7:
            act.hit(deck, player)
        else:
            result=act.stand(deck, croupier, player)
            return(result)
    elif player[1] == 12:
        if croupier[1] in (4,5,6):
            result=act.stand(deck, croupier, player)
            return(result)
        else:
            act.hit(deck, player)
    elif player[1] == 11:
        if croupier[1] == 11:
            act.hit(deck, player)
        else:
            result=act.double(deck, croupier, player)
            return(result)
    elif player[1] == 10:
        if croupier[1] in (10,11):
            act.hit(deck, player)
        else:
            result=act.double(deck, croupier, player)
            return(result)
    elif player[1] == 9:
        if croupier[1] in (3,4,5,6):
            result=act.double(deck, croupier, player)
            return(result)
        else:
            act.hit(deck, player)
    elif player[1] < 9:
        act.hit(deck, player)


def soft_total(deck: list, croupier: list, player: list): # CHANGE FOR THE TOTAL OF THE HAND WITHOUT THE AS
    if player[1] >= 20: # 10,9
        result=act.stand(deck, croupier, player)
        return(result)
    elif player[1] == 19: # 8
        if croupier[1] == 6:
            result=act.double(deck, croupier, player)
            return(result)
        else:
            result=act.stand(deck, croupier, player)
            return(result)
    elif player[1] == 18: # 7
        if croupier[1] < 7:
            result=act.double(deck, croupier, player)
            return(result)
        elif croupier[1] >= 9:
            act.hit(deck, player)
        else:
            result=act.stand(deck, croupier, player)
            return(result)
    elif player[1] == 17: # 6
        if croupier[1] in (3,4,5,6):
            result=act.double(deck, croupier, player)
            return(result)
        else:
            act.hit(deck, player)
    elif player[1] in (15,16): # 4 & 5
        if croupier[1] in (4,5,6):
            result=act.double(deck, croupier, player)
            return(result)
        else:
            act.hit(deck, player)
    elif player[1] in (13,14): # 2 & 3
        if croupier[1] in (5,6):
            result=act.double(deck, croupier, player)
            return(result)
        else:
            act.hit(deck, player)


def game(deck: list, croupier: list, player: list):
    result = None
    while result == None:
        if ("A" in player[0]) and (len(player[0]) == 2):
            result=soft_total(deck, croupier, player)
            print("Croupier 1:" + str(croupier))
            print("Player 1:" + str(player))
        else:
            result=hard_total(deck, croupier, player)
            print("Croupier 1:" + str(croupier))
            print("Player 1:" + str(player))
    return(result)

def pairs(deck: list, croupier: list, player: list):
    if player[0][0] == "A":
        players = act.split(deck, player)
        player1 = game(deck, croupier, players[0])
        player2 = game(deck, croupier, players[1])
        return([player1,player2])

    elif player[0][0] in ("10","J","Q","K"):
        result=act.stand(deck, croupier, player)
        return(result)
    
    elif player[0][0] == "9":
        if croupier[1] in (7,10,11):
            result=act.stand(deck, croupier, player)
            return(result)
        else:
            players = act.split(deck, player)
            player1 = game(deck, croupier, players[0])
            player2 = game(deck, croupier, players[1])
            return([player1,player2])

    elif player[0][0] == "8":
        players = act.split(deck, player)
        player1 = game(deck, croupier, players[0])
        player2 = game(deck, croupier, players[1])
        return([player1,player2])

    elif player[0][0] == "7":
        if croupier[1] >= 8:
            act.hit(deck, player)
        else:
            players = act.split(deck, player)
            player1 = game(deck, croupier, players[0])
            player2 = game(deck, croupier, players[1])
            return([player1,player2])

    elif player[0][0] == "6":
        if croupier[1] >= 7:
            act.hit(deck, player)
        else:
            players = act.split(deck, player)
            player1 = game(deck, croupier, players[0])
            player2 = game(deck, croupier, players[1])
            return([player1,player2])

    elif player[0][0] == "5":
        if croupier[1] in (10,11):
            act.hit(deck, player)
        else:
            result=act.double(deck, croupier, player)
            return(result)
    
    elif player[0][0] == "4":
        if croupier[1] in (5,6):
            players = act.split(deck, player)
            player1 = game(deck, croupier, players[0])
            player2 = game(deck, croupier, players[1])
            return([player1,player2])
        else:
            act.hit(deck, player)
    
    elif player[0][0] in ("2","3"):
        if croupier[1] >= 8:
            act.hit(deck, player)
        else:
            players = act.split(deck, player)
            player1 = game(deck, croupier, players[0])
            player2 = game(deck, croupier, players[1])
            return([player1,player2])
