from operator import itemgetter




def compute_points(matches=(), players=(), point_system=None, with_score=True):
    """
    Compute player's score in "matches".

    :param matches:   iterable container of <app.models.model_schedule.RoundMatch1vs1>
    :param players:   iterable container of <app.model.model_tournament.Player>
    :param point_system: <app.models.model_schedule.PointSystem>
    :param with_score:  True or False
    :return:  list of [ player=<app.model.model_tournament.Player>, count_of_points=<int> ]
    """

    point_table = {player: 0 for player in players}

    for match in matches:
        if match.result1.wins == match.result2.wins:
            point_table[match.player1] += point_system.draw
            point_table[match.player2] += point_system.draw
        elif match.result1.wins > match.result2.wins:
            if match.result2.wins == 0:
                point_table[match.player1] += point_system.pure_win
                point_table[match.player2] += point_system.pure_lose
            else:
                point_table[match.player1] += point_system.win
                point_table[match.player2] += point_system.lose
        else:
            if match.result1.wins == 0:
                point_table[match.player1] += point_system.pure_lose
                point_table[match.player2] += point_system.pure_win
            else:
                point_table[match.player1] += point_system.lose
                point_table[match.player2] += point_system.win

    # sort by value
    sorted_players = sorted(point_table.items(), key=itemgetter(1), reverse=True)
    # tuples to lists
    if with_score:
        sorted_players = [[player, value] for player, value in sorted_players]
    # only players
    else:
        sorted_players = [player for player, _ in sorted_players]
    return sorted_players


if __name__ == "__main__":
    pass