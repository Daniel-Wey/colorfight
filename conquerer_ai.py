from colorfight import Colorfight
import time
import random
from colorfight.constants import BLD_GOLD_MINE, BLD_ENERGY_WELL, BLD_FORTRESS, BUILDING_COST

game = Colorfight()

# Connect to the server. Designate argument for the room
game.connect(room = 'Musikverein')

# game.register should return True if succeed.
# input relevant username and pw
if game.register(username = "Hybezz", password = "danw6824151"):

    # Determines the growth of the colony
    # Increments by one every X number of rounds for which no command is executed
    scaling_factor = 100

    # Counts number of turns where no commands were executed
    no_growth = 0

    # number of turns spent scaling
    growth_turn_ceiling = 170

    # number of cells spent scaling
    growth_cell_ceiling = 300

    # This is the game loop
    while True:
        # The command list we will send to the server
        cmd_list = []


        # The list of cells that we want to attack
        my_attack_list = []

        # update_turn() is required to get the latest information from the
        # server. This will halt the program until it receives the updated
        # information. 
        # After update_turn(), game object will be updated.   
        last_turn = game.turn
        game.update_turn()

        # Turn number does not go back. So if it is going back, that means
        # a new game. You can add a infinite loop to continuously register
        # to the latest game and play.
        if game.turn < last_turn:
            game.connect(room = 'Musikverein')
            game.register(username = "Hybezz", password = "danw6824151")

        # Check if you exist in the game. If not, wait for the next round.
        # You may not appear immediately after you join. But you should be 
        # in the game after one round.
        if game.me == None:
            continue

        me = game.me

        """ Game Commands Begin Here: """

        # game.me.cells is a dict, where the keys are Position and the values
        # are MapCell. Get all my cells.

        # searches for home cell among current cells
        # and saves  position of  home cell
        home_pos = 0
        for cell in game.me.cells.values():
            if cell.building.name == 'home':
                home_pos = cell.position.info()

        # places the different cells into a dicitonary based off their manhattan
        # distance from the home cell
        new_order = {}
        for cell in game.me.cells.values():
            cell_pos = cell.position.info()
            distance = str(abs(cell_pos[0] - home_pos[0]) + abs(cell_pos[1] - home_pos[1]))
            if new_order.__contains__(distance):
                new_order[distance].append(cell)
            else:
                new_order[distance] = [cell]
        
        # iterate through the list of cells in sorted order from lowest-largest distance away
        sorted_cells = sorted(new_order)

        # if turn exceeds 200, iterate from largest-lowest distance away
        if game.turn > growth_turn_ceiling
            sorted_cells = reversed(sorted_cells)

        for distances in sorted_cells:
            list_dist = new_order[distances]
            for cell in list_dist:
                    # Check the surrounding position
                for pos in cell.position.get_surrounding_cardinals():
                    # Get the MapCell object of that position
                    c = game.game_map[pos]

                    # Attack if the cost is less than what I have, and the owner
                    # is not mine, and I have not attacked it in this round already
                    # [DW] buffer attack_cost with additional constant for forcefield
                    buffer_cost = 10

                    # determines the growth of capacity per unit of scaling_factor
                    advancement_factor = 80

                    if (c.attack_cost + buffer_cost) < me.energy and c.owner != game.uid \
                            and c.position not in my_attack_list \
                            and len(me.cells) < advancement_factor * scaling_factor:
                        # Add the attack command in the command list
                        # Subtract the attack cost and the buffer cost manually so I can keep track
                        # of the energy I have.
                        # Add the position to the attack list so I won't attack
                        # the same cell
                        cmd_list.append(game.attack(pos, c.attack_cost + buffer_cost))
                        print("We are attacking ({}, {}) with {} energy".format(pos.x, pos.y, c.attack_cost))
                        game.me.energy -= c.attack_cost + buffer_cost
                        my_attack_list.append(c.position)


                # [Determine relevant behavior for choosing which buildings to upgrade based on home / type of building / resource bounds]
                # If we can upgrade the building, upgrade it.
                # Notice can_update only checks for upper bound. You need to check
                # tech_level by yourself. 
                if cell.building.can_upgrade and \
                        (cell.building.is_home or cell.building.level < me.tech_level) and \
                        cell.building.upgrade_gold < me.gold and \
                        cell.building.upgrade_energy < me.energy:
                    cmd_list.append(game.upgrade(cell.position))
                    print("We upgraded ({}, {})".format(cell.position.x, cell.position.y))
                    me.gold   -= cell.building.upgrade_gold
                    me.energy -= cell.building.upgrade_energy
                    

                

                # [Eventually determine which building to build given the position of cell / demands / strategy at hand]
                # [Eventually determine the proportions of the different buildings for energy, gold, protection/power]
                # Build a random building if we have enough gold
                if cell.owner == me.uid and cell.building.is_empty and me.gold >= BUILDING_COST[0]:
                    building = None
                    if game.turn < growth_turn_ceiling and len(me.cells) < growth_cell_ceiling:
                        building = random.choice([BLD_ENERGY_WELL, BLD_GOLD_MINE])
                    else:
                        building = random.choice([BLD_FORTRESS, BLD_GOLD_MINE, BLD_ENERGY_WELL])
                    cmd_list.append(game.build(cell.position, building))
                    print("We build {} on ({}, {})".format(building, cell.position.x, cell.position.y))
                    me.gold -= 100

        # Send the command list to the server
        result = game.send_cmd(cmd_list)
        print(result)
        print("This is the scaling factor: {}".format(scaling_factor))
else:
    print("The username and password you entered is invalid.")