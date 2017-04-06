class SchedulePlayer:
    def __init__(self, player=None, pure_wins=0, wins=0, score=0, group_score=0, reverse_order=0):
        self.score = score
        self.group_score = group_score
        self.player = player
        self.pure_wins = pure_wins
        self.wins = wins
        self.reverse_order = reverse_order


def compute_points(matches=(), point_table=(), point_system=None, only_group=False):

    for match in matches:
        if match.result1.wins == match.result2.wins:
            if not only_group:
                point_table[match.player1].score += point_system.draw
                point_table[match.player2].score += point_system.draw
            else:
                point_table[match.player1].group_score += point_system.draw
                point_table[match.player2].group_score += point_system.draw

        elif match.result1.wins > match.result2.wins:
            if match.result2.wins == 0:
                if not only_group:
                    point_table[match.player1].score += point_system.pure_win
                    point_table[match.player1].pure_wins += 1
                    point_table[match.player2].score += point_system.pure_lose
                else:
                    point_table[match.player1].group_score += point_system.pure_win
                    point_table[match.player2].group_score += point_system.pure_lose
            else:
                if not only_group:
                    point_table[match.player1].score += point_system.win
                    point_table[match.player1].wins += 1
                    point_table[match.player2].score += point_system.lose
                else:
                    point_table[match.player1].group_score += point_system.win
                    point_table[match.player2].group_score += point_system.lose
        else:
            if match.result1.wins == 0:
                if not only_group:
                    point_table[match.player1].score += point_system.pure_lose
                    point_table[match.player2].pure_wins += 1
                    point_table[match.player2].score += point_system.pure_win
                else:
                    point_table[match.player1].group_score += point_system.pure_lose
                    point_table[match.player2].group_score += point_system.pure_win
            else:
                if not only_group:
                    point_table[match.player1].score += point_system.lose
                    point_table[match.player2].wins += 1
                    point_table[match.player2].score += point_system.win
                else:
                    point_table[match.player1].group_score += point_system.lose
                    point_table[match.player2].group_score += point_system.win


def get_sorted_players(matches=(), point_table={}, point_system=None, with_score=True,
                       return_list_of_schedule_players=False):
    compute_points(matches=matches, point_table=point_table, point_system=point_system)

    # find players with same score
    groups = {}
    for _, schedule_player in point_table.items():
        if schedule_player.score not in groups:
            groups[schedule_player.score] = [schedule_player]
        else:
            groups[schedule_player.score].append(schedule_player)

    for _, group in groups.items():
        if len(group) > 1:
            group_matches = []
            group_players = [schedule_player.player for schedule_player in group]
            for player in group_players[:-1]:
                player1 = player
                for other_player in group_players[group_players.index(player):]:
                    player2 = other_player
                    for match in matches:
                        if (match.player1_id == player1.id and match.player2_id == player2.id) \
                                or (match.player2_id == player1.id and match.player1_id == player2.id):
                            group_matches.append(match)
                            break
            compute_points(matches=group_matches, point_table=point_table, point_system=point_system, only_group=True)

    sorted_players = sorted(point_table.items(), key=lambda item: (item[1].score,
                                                                   item[1].group_score,
                                                                   item[1].pure_wins,
                                                                   item[1].wins,
                                                                   item[1].reverse_order), reverse=True)
    # return list of schedule players
    if return_list_of_schedule_players:
        sorted_players = [schedule_player for _, schedule_player in sorted_players]
        return sorted_players
    # tuples to lists
    if with_score:
        sorted_players = [[player, schedule_player.score] for player, schedule_player in sorted_players]
    # only players
    else:
        sorted_players = [player for player, _ in sorted_players]
    return sorted_players


if __name__ == "__main__":
    pass