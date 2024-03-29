import deck
import participant
import view
import dbmanager

import copy
from datetime import datetime 

class BlackjackGame:
    DECK_VALUES = {"A":11, "2": 2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":10, "Q":10, "K":10}

    def __init__(self, bot=False, bot_balance=100, bot_bet = 10, bot_rounds=10) -> None:
        # Modeler
        self.deck = deck.Deck()
        self.croupier = participant.Croupier()
        if bot:
            self.player = participant.Bot()
            self.player.balance = bot_balance
            self.bot_bet = bot_bet
            self.bot_rounds = bot_rounds
        else:
            self.player = participant.Player()
        # View
        self.view = view.BlackjackView()
        # DB Manager
        self.db_manager = dbmanager.DBManager()
        self.game_id = 0
        self.round_id = 0

    # SET THE CONDITIONS OF THE GAME AND THE LOOP FOR ALL THE GAME
    def play(self):
        self.db_manager.games_update('start_time', datetime.now()) # Register games start_time
        round_number = 0
        if isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.db_manager.games_update('bot', True) # Register games start_time
            self.db_manager.games_update('initial_balance', self.player.balance) # Register games initial_balance
            game_id = self.db_manager.insert_games() # INSERT 1
            self.game_id = game_id
            while self.bot_rounds != 0:
                if self.player.balance < self.bot_bet:
                    print("No more chips to play")
                    break
                else:
                    self.start_game()
                    #DB MANAGER
                    round_number += 1 # Register rounds round_number
                    self.db_manager.rounds_update('round_number', round_number) # Register rounds round_number
                    self.round_id = self.db_manager.insert_rounds() # INSERT 1
                    #---------
                    self.play_game()
                    #DB MANAGER
                    self.db_manager.insert_rounds_final(self.round_id) # Register rounds round_number
                    self.db_manager.rounds_restart()
                    #---------
                    self.new_game()
                    self.bot_rounds -= 1
            print("Games completed!")
        else:
            self.view.show_welcome_message()
            balance = self.view.get_balance()
            self.player.balance = balance
            self.db_manager.games_update('bot', False) # Register games start_time
            self.db_manager.games_update('initial_balance', self.player.balance) # Register games initial_balance
            game_id = self.db_manager.insert_games() # Register games1
            self.game_id = game_id
            input("Press Enter to start...")
            # loop for the game
            continue_playing = "y"
            while continue_playing != "e":
                if self.player.balance == 0:
                    print("You have no chips")
                    new_balance = self.view.get_balance()
                    self.player.balance = new_balance
                else:
                    self.start_game()
                    #DB MANAGER
                    round_number += 1 # Register rounds round_number
                    self.db_manager.rounds_update('round_number', round_number) # Register rounds round_number
                    self.round_id = self.db_manager.insert_rounds() # INSERT 1
                    #---------
                    self.play_game()
                    #DB MANAGER
                    self.db_manager.insert_rounds_final(self.round_id) # Register rounds round_number
                    self.db_manager.rounds_restart()
                    #---------
                    self.view.show_current_balance(self.player.balance)
                    self.new_game()
                    continue_playing = self.view.ask_continue_playing()
                    if continue_playing == "a":
                        add_balance = self.view.add_balance()
                        self.player.balance += add_balance
        self.db_manager.games_update('end_time', datetime.now()) # Register games end_time
        self.db_manager.games_update('final_balance', self.player.balance) # Register games final_balance
        self.db_manager.insert_games_final(self.game_id) # INSERT 2
        self.db_manager.disconnect # Close connection to db


    def new_game(self):
        self.player.cards = []
        self.croupier.cards = []

    def start_game(self):
        # Get the initial bet from the player
        if isinstance(self.player, participant.Bot):  # BOT VALIDATION
            self.current_bet = self.bot_bet
        else:
            self.current_bet = self.view.get_initial_bet(self.player.balance)
        # Deal de cards
        self.player.add_card(self.deck.draw_card())
        self.croupier.add_card(self.deck.draw_card())
        self.player.add_card(self.deck.draw_card())
        # Show cards if player is not a bot
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
            self.view.show_player_hand(self.player.cards, self.player.values)
        # DB MANAGER
        self.db_manager.rounds_update('game_id', self.game_id) # Register rounds game_id
        self.db_manager.rounds_update('p_initial_cards', self.player.cards) # Register rounds p_initial_cards
        self.db_manager.rounds_update('p_initial_value', self.player.values) # Register rounds p_initial_value
        self.db_manager.rounds_update('c_initial_cards', self.croupier.cards) # Register rounds c_initial_cards
        self.db_manager.rounds_update('c_initial_value', self.croupier.values) # Register rounds c_initial_value
        self.db_manager.rounds_update('initial_balance', self.player.balance) # Register rounds initial_balance
        self.db_manager.rounds_update('initial_bet', self.current_bet) # Register rounds initial_bet
    
    # ACTIONS OF THE PLAYER
    def hit(self):
        self.player.add_card(self.deck.draw_card())
        # Show cards
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
            self.view.show_player_hand(self.player.cards, self.player.values)
        # DB MANAGER
        self.moves_register('h', self.player.cards, self.player.values, self.croupier.cards, self.croupier.values, self.current_bet)

    def stand(self):
        # DB MANAGER
        self.moves_register('s', self.player.cards, self.player.values, self.croupier.cards, self.croupier.values, self.current_bet)
    
    def double(self):
        # double the bet
        self.current_bet += self.current_bet
        # play the card
        self.player.add_card(self.deck.draw_card())
        # DB MANAGER
        self.moves_register('d', self.player.cards, self.player.values, self.croupier.cards, self.croupier.values, self.current_bet)

    def moves_register(self, move, p_cards, p_value, c_cards, c_value, bet, h2=False): # DB MANAGER METHOD TO REGISTER NEW MOVE
        # moves number variable
        self.move_number += 1
        # registers on the moves table
        self.db_manager.moves_update('round_id', self.round_id)
        self.db_manager.moves_update('move_number', self.move_number)
        self.db_manager.moves_update('move', move)
        self.db_manager.moves_update('p_cards', p_cards)
        self.db_manager.moves_update('p_value', p_value)
        self.db_manager.moves_update('c_cards', c_cards)
        self.db_manager.moves_update('c_value', c_value)
        self.db_manager.moves_update('bet', bet)
        self.db_manager.moves_update('h2', h2)
        # insert moves register
        self.db_manager.insert_moves()
        # delete of current values for a new register
        self.db_manager.moves_update('round_id', None)
        self.db_manager.moves_update('move_number', None)
        self.db_manager.moves_update('move', None)
        self.db_manager.moves_update('p_cards', None)
        self.db_manager.moves_update('p_value', None)
        self.db_manager.moves_update('c_cards', None)
        self.db_manager.moves_update('c_value', None)
        self.db_manager.moves_update('bet', None)
        self.db_manager.moves_update('h2', False)

    # STANDARD FOR THE GAME AFTER THE FIRST HAND
    def game_standard(self):
        while self.player.values <= 21:
            if isinstance(self.player, participant.Bot): # BOT VALIDATION
                action = self.player.decide_action(self.croupier.cards, self.player.cards, self.player.values, allow_double=False, allow_split=False)
            else:
                action = self.view.actions_player(False, False)
            # decision in action based on player or bot
            if action == "h": 
                self.hit()
            elif action == "s":
                self.stand()
                break

    # FIRST HAND OF THE GAME
    def play_game(self):
        # DB MANAGER
        self.move_number = 0
        #---
        if (self.DECK_VALUES[self.player.cards[0]] == self.DECK_VALUES[self.player.cards[1]]) and (self.player.balance >= self.current_bet*2):
            # Player choice on pairs with enough balance
            if isinstance(self.player, participant.Bot): # BOT VALIDATION
                action = self.player.decide_action(self.croupier.cards, self.player.cards, self.player.values, allow_double=True, allow_split=True)
            else:
                action = self.view.actions_player(True, True)
            # decision in action based on player or bot
            if action == 'h': #hit
                self.hit()
                self.game_standard()
                self.croupier_play()
                self.finish_game(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
            elif action == 's': #stand
                self.stand()
                self.croupier_play()
                self.finish_game(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
            elif action == 'd': #double
                self.double()
                self.croupier_play()
                self.finish_game(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
            elif action == 'p': #split
                self.split()
        else:
            # Player choice on regular cards and validation of the amount
            if self.player.balance >= self.current_bet*2:
                if isinstance(self.player, participant.Bot): # BOT VALIDATION
                    action = self.player.decide_action(self.croupier.cards, self.player.cards, self.player.values, allow_double=True, allow_split=False)
                else:
                    action = self.view.actions_player(True, False)
            else: 
                if isinstance(self.player, participant.Bot): # BOT VALIDATION
                    action = self.player.decide_action(self.croupier.cards, self.player.cards, self.player.values, allow_double=False, allow_split=False)
                else:
                    action = self.view.actions_player(False, False)
            # Actions of the player
            if action == 'h': #hit
                self.hit()
                self.game_standard()
                self.croupier_play()
                self.finish_game(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
            elif action == 's': #stand
                self.stand()
                self.croupier_play()
                self.finish_game(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
            elif action == 'd': #double
                self.double()
                self.croupier_play()
                self.finish_game(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
        # DB MANAGER
        self.db_manager.rounds_update('p_final_cards', self.player.cards) # Register rounds p_final_cards
        self.db_manager.rounds_update('p_final_value', self.player.values) # Register rounds p_final_value
        self.db_manager.rounds_update('c_final_cards', self.croupier.cards) # Register rounds c_final_cards
        self.db_manager.rounds_update('c_final_value', self.croupier.values) # Register rounds c_final_value
        self.db_manager.rounds_update('final_balance', self.player.balance) # Register rounds final_balance
        self.db_manager.rounds_update('final_bet', self.current_bet) # Register rounds final_bet

    # THE CROUPIER PLAYS HIS HAND
    def croupier_play(self):
        while self.croupier.values < 17:
            self.croupier.add_card(self.deck.draw_card())
        # Show cards
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
            self.view.show_player_hand(self.player.cards, self.player.values)

    # RETURN WINNER -1=HOUSE_WINS 0=PUSH 1=PLAYER_WINS
    def set_winner(self, croupier_cards, croupier_values, player_cards, player_values):
        if croupier_values > 21 or player_values > 21: # someone exceeded 21
            if player_values > 21: # Player has +21
                winner = -2
            elif croupier_values > 21: # Croupier has +21
                winner = 1
        elif croupier_values == 21 and player_values == 21: # both have 21
            if len(croupier_cards) == 2 and len(player_cards) == 2: # both have blackjack
                winner = 0
            elif len(croupier_cards) == 2 and len(player_cards) != 2: # croupier has blackjack
                winner = -1
            elif len(croupier_cards) != 2 and len(player_cards) == 2: # player has blackjack
                winner = 2
            elif len(croupier_cards) != 2 and len(player_cards) != 2: # no one have blackjack
                winner = 0
        elif croupier_values == player_values: # both have same value
            winner = 0
        elif croupier_values > player_values: # croupier more than player
            winner = -1
        elif croupier_values < player_values: # croupier less than player
            winner = 1
        return winner
    
    # CONTROLS THE PAYMENTS
    def payments(self, winner, split=False):
        # Result of the bet
        if winner == 2 and split:
            self.player.balance += self.current_bet
        elif winner == 2:
            blackjack = self.current_bet + (self.current_bet//2)
            self.player.balance += blackjack
        elif winner == 1:
            self.player.balance += self.current_bet
        elif winner <= -1:
            self.player.balance -= self.current_bet

    def finish_game(self, croupier_cards, croupier_values, player_cards, player_values):
        winner = self.set_winner(croupier_cards, croupier_values, player_cards, player_values)
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_winner(winner)
        self.payments(winner)
        #DB MANAGER
        self.db_manager.rounds_update('outcome', winner) # Register rounds outcome

    # GAME AFTER A SPLIT
    def split(self):
        # DB MANAGER
        self.moves_register('p', self.player.cards, self.player.values, self.croupier.cards, self.croupier.values, self.current_bet)
        # Double the bet on different hands
        self.current_bet_h2 = self.current_bet
        # Split of hand
        split_player = copy.deepcopy(self.player)
        del self.player.cards[-1]
        del split_player.cards[0]
        self.player.add_card(self.deck.draw_card())
        split_player.add_card(self.deck.draw_card())

        # HAND 1 PLAY
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            print("-------")
            print("HAND 1")
        # Show hands
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
            self.view.show_player_hand(self.player.cards, self.player.values)
            # Validation of the balance for double
        if self.player.balance >= ((self.current_bet*2) + self.current_bet_h2):
            if isinstance(self.player, participant.Bot): # BOT VALIDATION
                action = self.player.decide_action(self.croupier.cards, self.player.cards, self.player.values, allow_double=True, allow_split=False)
            else:
                action = self.view.actions_player(True, False)
        else: 
            if isinstance(self.player, participant.Bot): # BOT VALIDATION
                action = self.player.decide_action(self.croupier.cards, self.player.cards, self.player.values, allow_double=False, allow_split=False)
            else:
                action = self.view.actions_player(False, False)
        # Actions of the player
        if action == "h": 
            self.hit()
            self.game_standard()
        elif action == "s":
            self.stand()
        elif action == "d":
            self.double()
        
        # HAND 2 PLAY
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            print("-------")
            print("HAND 2")
        # Show hands
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
            self.view.show_player_hand(split_player.cards, split_player.values)
        # Game standard adjusted
        # Validation for double
        if self.player.balance >= (self.current_bet + (self.current_bet_h2*2)):
            if isinstance(self.player, participant.Bot): # BOT VALIDATION
                action = self.player.decide_action(self.croupier.cards, split_player.cards, split_player.values, allow_double=True, allow_split=False)
            else:
                action = self.view.actions_player(True, False)
        else:
            if isinstance(self.player, participant.Bot): # BOT VALIDATION
                action = self.player.decide_action(self.croupier.cards, split_player.cards, split_player.values, allow_double=False, allow_split=False)
            else:
                action = self.view.actions_player(False, False)
        # Action of the player/bot
        if action == "h":
            split_player.add_card(self.deck.draw_card())
            # Show cards
            if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
                self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
                self.view.show_player_hand(split_player.cards, split_player.values)
            # DB MANAGER
            self.moves_register('h', split_player.cards, split_player.values, self.croupier.cards, self.croupier.values ,self.current_bet_h2, True)
            # Game standard modified
            while split_player.values <= 21:
                if isinstance(split_player, participant.Bot): # BOT VALIDATION
                    action = split_player.decide_action(self.croupier.cards, split_player.cards, split_player.values, allow_double=False, allow_split=False)
                else:
                    action = self.view.actions_player(False, False)
                # decision in action based on player or bot
                if action == "h": 
                    split_player.add_card(self.deck.draw_card())
                    # Show cards
                    if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
                        self.view.show_croupier_hand(self.croupier.cards, self.croupier.values)
                        self.view.show_player_hand(split_player.cards, split_player.values)
                    # DB MANAGER
                    self.moves_register('h', split_player.cards, split_player.values, self.croupier.cards, self.croupier.values, self.current_bet_h2, True)
                elif action == "s":
                    self.moves_register('s', split_player.cards, split_player.values, self.croupier.cards, self.croupier.values, self.current_bet_h2, True)
                    break
        elif action == "s":
            # DB MANAGER
            self.moves_register('s', split_player.cards, split_player.values, self.croupier.cards, self.croupier.values, self.current_bet_h2, True)
        elif action == "d":
            # double the bet
            self.current_bet_h2 += self.current_bet_h2
            # play the card
            split_player.add_card(self.deck.draw_card())
            # DB MANAGER
            self.moves_register('d', split_player.cards, split_player.values, self.croupier.cards, self.croupier.values, self.current_bet_h2, True)

        # FINISH GAME
        # Show croupier hands and player hands 
        self.croupier_play()
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_player_hand(split_player.cards, split_player.values)
        # FINISH GAME HAND1
        winner = self.set_winner(self.croupier.cards, self.croupier.values, self.player.cards, self.player.values)
        # DB MANAGER
        self.db_manager.rounds_update('outcome', winner) # Register rounds outcome
        #---
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            print("--------------")
            print("HAND 1 WINNER:") # show winner on console
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_winner(winner)
        self.payments(winner, split=True) # bet of first hand
        # FINISH GAME HAND2
        winner = self.set_winner(self.croupier.cards, self.croupier.values, split_player.cards, split_player.values)
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            print("--------------")
            print("HAND 2 WINNER:") # show winner on console
        if isinstance(self.player, participant.Player) and not isinstance(self.player, participant.Bot): # BOT VALIDATION
            self.view.show_winner(winner)
        if winner >= 1:  # bet of second hand
            self.player.balance += self.current_bet_h2
        elif winner <= -1:
            self.player.balance -= self.current_bet_h2

        # DB MANAGER
        self.db_manager.rounds_update('split', True) # Register rounds split
        self.db_manager.rounds_update('h2_cards', split_player.cards) # Register rounds h2_cards
        self.db_manager.rounds_update('h2_value', split_player.values) # Register rounds h2_value
        self.db_manager.rounds_update('h2_bet', self.current_bet_h2) # Register rounds h2_bet
        self.db_manager.rounds_update('h2_outcome', winner) # Register rounds h2_outcome