from random import shuffle
from operator import itemgetter


def rotate(my_list, shift, start_of_sublist=0):
    return my_list[:start_of_sublist] + my_list[start_of_sublist+shift:] + my_list[start_of_sublist:start_of_sublist+shift]


def shuffle_list(my_list):
    shuffle(my_list)
    return my_list


def generator_each_vs_each(player_list):
    # copy list
    players = player_list[:]

    # completion to even list
    if len(players) % 2 == 1:
        players.append(None)

    count_of_round = len(players)-1
    rounds_dict = dict()

    for tournament_round in range(count_of_round):
        this_round = list()
        for index in range(len(players) // 2):
            match = (players[index], players[len(players)-1-index])
            if None not in match:
                this_round.append(match)
        players = rotate(players, 1, 1)
        rounds_dict[tournament_round+1] = this_round
    return rounds_dict


def function(played_pairs, desc_list):

    left_index = 0
    right_index = 1
    result = []
    count_of_players = len(desc_list)
    last_index = count_of_players - 1

    while True:
        if len(result) >= (count_of_players // 2):
            return result

        is_in_pair_list = False
        is_left_in_restult = False
        is_right_in_restult = False

        #Kontrola jedinecnosti
        for pair in played_pairs:
            if desc_list[left_index] in pair and desc_list[right_index]:
                if right_index < last_index:
                    is_in_pair_list = True
                    break

        for pair in result:
            if desc_list[left_index] in pair:
                is_left_in_restult = True
            if desc_list[right_index] in pair:
                is_right_in_restult = True

        if not is_in_pair_list and not is_right_in_restult and not is_left_in_restult:
            result.append((desc_list[left_index], desc_list[right_index]))








if __name__ == "__main__":
    my_played_pairs = [("A", "B"), ("C", "D"), ("E", "F")]
    ranked_players = {'A': 1, 'B ': 3, "C": 2, 'D': 5, 'E': 8, 'F': 15}
    sorted_players = sorted(ranked_players.items(), reverse=True, key=itemgetter(1))

    sorted_players = [x[0] for x in sorted_players]

    print(function(my_played_pairs, sorted_players))
    result = []
    for i in range(5):

        result.extend(function(result, sorted_players))
        print(result)