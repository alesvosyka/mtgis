from random import shuffle


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


def compute_round(played_pairs=(), desc_list=(), verbose=False):

    # init phase
    left_index = 0
    right_index = 1
    result = []
    count_of_players = len(desc_list)
    last_index = count_of_players - 1
    if verbose:
        print('\n' * 5)
        print("Odehrany pary: {}".format(played_pairs))
        print('Init - left_index: {}, right_index {}, count_of_players: {}, last_index: {}'.format(left_index, right_index, count_of_players, last_index))

    # start
    while True:
        if verbose:
            print("----zacatek cyklu---------------------------------------------------")
            print("Played pairs: {}".format(played_pairs))
            print("Result: {}".format(result))

        # Exit program if result is full
        if len(result) >= (count_of_players // 2):
            return result
        if verbose:
            print("Indexes - left: {}, right: {}".format(left_index, right_index))

        if verbose:
            print("Indexy po posunu - left: {}, right: {}".format(left_index, right_index))
            print("{} {}".format(desc_list[left_index], desc_list[right_index]))

        # Reset flags
        is_in_pair_list = False
        is_left_in_result = False
        is_right_in_result = False

        # Searching for collisions and setting flags
        for pair in played_pairs:
            if desc_list[left_index] in pair and desc_list[right_index] in pair:
                    if verbose:
                        print("Shoda is_in_pair_list")
                    is_in_pair_list = True
                    break

        for pair in result:
            if desc_list[left_index] in pair:
                is_left_in_result = True
                if verbose:
                    print("Shoda is_left_in_result")
                break
            if desc_list[right_index] in pair:
                if verbose:
                    print("Shoda is_right_in_result")
                is_right_in_result = True
                break

        # Push result if no flag
        if not is_in_pair_list and not is_right_in_result and not is_left_in_result:
            if verbose:
                print("Pridavam {} {}".format(desc_list[left_index], desc_list[right_index]))
            result.append((desc_list[left_index], desc_list[right_index]))
            left_index = 0
            right_index = left_index

        # Recompute indices ann pop result if is nessecary
        if right_index < last_index:
            if verbose:
                print("posouvam pravej {} > {} ".format(right_index, right_index + 1))
            right_index += 1
        elif left_index < last_index - 1:
            if verbose:
                print("posouvam levej  {} > {}, pravej {} > {} ".format(left_index, left_index + 1, right_index,
                                                                   left_index + 2))
            left_index += 1
            right_index = left_index + 1

        else:
            while True:
                left, right = result.pop()
                if verbose:
                    print("Odebiram {} {} - result: {}".format(left, right, result))
                if desc_list.index(right) < last_index:
                    left_index = desc_list.index(left)
                    right_index = desc_list.index(right)+1
                    break
                elif desc_list.index(left) < last_index - 1:
                    left_index = desc_list.index(left) + 1
                    right_index = left_index + 1
                    break


if __name__ == "__main__":
    my_players = ["G", "F", "E", "D", "C", "B" ]

    #print(function(my_played_pairs, sorted_players))

    results = []
    for i in range(len(my_players)-1):
        print(i)
        results.extend(compute_round(results, my_players,))
        print(results)

