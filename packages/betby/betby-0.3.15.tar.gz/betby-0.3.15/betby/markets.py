import numpy as np
from math import exp, factorial
import markets
from markets.specifiers import format_specifiers


class Get_markets:
    def __init__(self, avg_1, avg_2, score_1=0, score_2=0, time=0,
                 time_full=93, time_block=90, time_block_asian=90,
                 matrix=None, poisson=False, result=None):
        self.avg_1 = avg_1
        self.avg_2 = avg_2
        self.score_1 = score_1
        self.score_2 = score_2
        self.time = time
        self.time_full = time_full
        self.time_block = time_block
        self.time_block_asian = time_block_asian
        self.matrix = matrix
        self.poisson = poisson
        self.result = {} if result is None else result
        self.poi_1 = len(matrix[0]) if not poisson else None
        self.betstop = 0
        self.betstop_asian = 0
        if self.time > self.time_block:
            self.betstop = 1
        if self.time > self.time_block_asian:
            self.betstop_asian = 1

    # округление кэфов
    def kf_round(self, a, max):
        if a < 3.5:
            a = np.floor(a * 100) / 100
        elif a < 10:
            a = np.floor(a * 10) / 10
        elif a < max:
            a = np.floor(a)
        else:
            a = max
        if a > max:
            a = max
        return a

    # расчет маржи, кэфы на победу низкие
    def margin(self, kf, m=0.05, max=25):

        k_0 = 22 * 0.045 / m  # убывающая прямая
        v_0 = (-m + 0.23 - 0.5 / k_0) / (0.23 - 1 / k_0)  # предельная вер
        m_0 = 0.23 * (1 - v_0)
        n_0 = (1.5 - 1 / k_0) / (1.5 - 0.23)  # показатель (производная)
        ver = 0.5 + abs(1 / kf - 0.5)
        mar_1 = m - (ver - 0.5) / k_0
        mar_2 = 1.5 * (1 - ver) - (1.5 - 0.23) * (
                1 - v_0) * ((1 - ver) / (1 - v_0)) ** n_0
        if ver >= v_0:
            kf_v = (1 - mar_2) / ver
        else:
            kf_v = (1 - mar_1) / ver
        if 1 / kf >= 0.5:
            kf = self.kf_round(kf_v, max)
        else:
            kf = self.kf_round((1 - m) * kf_v / (kf_v - 1 + m), max)
        return kf

    def get_outcome(self, *factor):
        '''

        :param factor:
        :return: correct type of data
        '''
        if factor is None:
            return {'k': '0.0', 'b': 1}
        k, b = factor
        return {
            'k': str(k),
            'b': b,
        }

    def asian_spec(self, prob_a, prob_b, s=0):
        '''

        :param prob_a: prob of win spec
        :param prob_b: prob of win spec +-1
        :param s: asian or whole
        :return: prob = 1 / odds
        '''
        asian_prob = 0
        if s == 0:
            asian_prob = 1 / ((
                    1 - max(prob_a, prob_b)) / min(prob_a, prob_b) + 1)
        return asian_prob

    def get_matrix(self):
        avg_1 = self.avg_1 * (self.time_full - self.time) / self.time_full
        avg_2 = self.avg_2 * (self.time_full - self.time) / self.time_full
        if self.poisson:
            self.matrix = np.zeros((self.poisson, self.poisson))
            for i in range(self.poisson):
                for j in range(self.poisson):
                    prob = (exp(-avg_1) * avg_1 ** i / factorial(i)) * (
                            exp(-avg_2) * avg_2 ** j / factorial(j))
                    self.matrix[i, j] = prob
        return self.matrix

    def winner_3_way(self, mar=0.05, min_prob=0.02, max_odds=250):
        prob_1 = 0
        prob_2 = 0
        for i in range(self.poisson or self.poi_1):
            for j in range(self.poisson or self.poi_1):
                if j - i < -0.5 + self.score_1 - self.score_2:
                    prob_1 += self.matrix[i, j]
                if j - i > 0.5 + self.score_1 - self.score_2:
                    prob_2 += self.matrix[i, j]
        hand_key = format_specifiers(markets.THREE_WAY_WINNER, {})
        hand_dict = {}

        if prob_1 > 0 and prob_2 > 0 and 1 - prob_1 - prob_2 > 0 and \
                prob_1 < 1 and prob_2 < 1 and 1 - prob_1 - prob_2 < 1:
            hand_dict = {
                markets.THREE_WAY_WINNER_HOME: self.get_outcome(
                    self.margin(1 / prob_1, mar, max_odds), 0),
                markets.THREE_WAY_WINNER_DRAW: self.get_outcome(
                    self.margin(1 / (1 - prob_1 - prob_2), mar, max_odds), 0),
                markets.THREE_WAY_WINNER_AWAY: self.get_outcome(
                    self.margin(1 / prob_2, mar, max_odds), 0)
            }
        if (
            not self.betstop
            and prob_1 <= 1 - min_prob
            and prob_1 >= min_prob
            and prob_2 <= 1 - min_prob
            and prob_2 >= min_prob
            and 1 - prob_1 - prob_2 <= 1 - min_prob
            and 1 - prob_1 - prob_2 >= min_prob
            and hand_dict
        ):
            if markets.THREE_WAY_WINNER not in self.result:
                self.result[markets.THREE_WAY_WINNER] = {}
            self.result[markets.THREE_WAY_WINNER].update({hand_key: hand_dict})

    def double_chance(self, mar=0.05, min_prob=0.02, max_odds=250):
        prob_1 = 0
        prob_2 = 0
        for i in range(self.poisson or self.poi_1):
            for j in range(self.poisson or self.poi_1):
                if j - i < 0.5 + self.score_1 - self.score_2:
                    prob_1 += self.matrix[i, j]
                if j - i > -0.5 + self.score_1 - self.score_2:
                    prob_2 += self.matrix[i, j]
        hand_key = format_specifiers(markets.DOUBLE_CHANCE, {})
        hand_dict = {}

        if prob_1 > 0 and prob_2 > 0 and 2 - prob_1 - prob_2 > 0 and \
                prob_1 < 1 and prob_2 < 1 and 2 - prob_1 - prob_2 < 1:
            hand_dict = {
                markets.DOUBLE_CHANCE_HOME_DRAW: self.get_outcome(
                    self.margin(1 / prob_1, mar, max_odds), 0),
                markets.DOUBLE_CHANCE_HOME_AWAY: self.get_outcome(
                    self.margin(1 / (2 - prob_1 - prob_2), mar, max_odds), 0),
                markets.DOUBLE_CHANCE_DRAW_AWAY: self.get_outcome(
                    self.margin(1 / prob_2, mar, max_odds), 0)
            }
        if (
            not self.betstop
            and prob_1 <= 1 - min_prob
            and prob_1 >= min_prob
            and prob_2 <= 1 - min_prob
            and prob_2 >= min_prob
            and 2 - prob_1 - prob_2 <= 1 - min_prob
            and 2 - prob_1 - prob_2 >= min_prob
            and hand_dict
        ):
            if markets.DOUBLE_CHANCE not in self.result:
                self.result[markets.DOUBLE_CHANCE] = {}
            self.result[markets.DOUBLE_CHANCE].update(
                {hand_key: hand_dict})

    def total(self, mar=0.05, min_prob=0.2, max_odds=25, asian=False):
        prob = 0
        prob_1 = 0
        for val in range(2 * self.poisson or 2 * self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if i + j < val + 0.5:
                        prob += self.matrix[i, j]
            total_key = format_specifiers(markets.TOTAL, {
                'total': str(val + 0.5 + self.score_1 + self.score_2)})
            total_dict = {}

            if prob > 0 and prob < 1:
                total_dict = {
                    markets.TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and total_dict:
                if markets.TOTAL not in self.result:
                    self.result[markets.TOTAL] = {}
                self.result[markets.TOTAL].update({total_key: total_dict})

            if prob > 0 and prob < 1 and prob_1 > 0 and prob_1 < 1 and asian:
                prob_asian = self.asian_spec(prob, prob_1)
                total_key_asian = format_specifiers(markets.TOTAL, {
                    'total': str(val + self.score_1 + self.score_2)})
                total_dict_asian = {
                    markets.TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob_asian), mar, max_odds), 0),
                    markets.TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob_asian, mar, max_odds), 0)
                }

                if not self.betstop and not self.betstop_asian and prob_asian \
                        <= 1 - min_prob and prob_asian >= min_prob and \
                        total_dict_asian:
                    if markets.TOTAL not in self.result:
                        self.result[markets.TOTAL] = {}
                    self.result[markets.TOTAL].update({
                        total_key_asian: total_dict_asian})

            prob_1 = prob
            prob = 0

    def handicap(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(1 - (self.poisson or self.poi_1),
                         (self.poisson or self.poi_1) - 1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j - i > val + 0.5:
                        prob += self.matrix[i, j]
                        # print(val + 0.5, i, j, prob)
            hand_key = format_specifiers(markets.HANDICAP, {
                'hcp': str(val + 0.5 - self.score_1 + self.score_2)})
            hand_dict = {}

            if prob > 0 and prob < 1:
                hand_dict = {
                    markets.HANDICAP_HOME: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.HANDICAP_AWAY: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and hand_dict:
                if markets.HANDICAP not in self.result:
                    self.result[markets.HANDICAP] = {}
                self.result[markets.HANDICAP].update({hand_key: hand_dict})
            prob = 0

    def match_rest_handicap(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(1 - (self.poisson or self.poi_1),
                         (self.poisson or self.poi_1) - 1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j - i > val + 0.5:
                        prob += self.matrix[i, j]
                        # print(val + 0.5, i, j, prob)
            hand_key = format_specifiers(markets.MATCH_REST_HANDICAP, {
                'score': str(self.score_1) + ':' + str(self.score_2),
                    'hcp': str(val + 0.5)})
            hand_dict = {}

            if prob > 0 and prob < 1:
                hand_dict = {
                    markets.MATCH_REST_HANDICAP_HOME: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.MATCH_REST_HANDICAP_AWAY: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and hand_dict:
                if markets.MATCH_REST_HANDICAP not in self.result:
                    self.result[markets.MATCH_REST_HANDICAP] = {}
                self.result[
                    markets.MATCH_REST_HANDICAP].update({hand_key: hand_dict})
            prob = 0

    def home_total(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if i < val + 0.5:
                        prob += self.matrix[i, j]
            home_total_key = format_specifiers(markets.HOME_TOTAL, {
                'total': str(val + 0.5 + self.score_1)})
            home_total_dict = {}

            if prob > 0 and prob < 1:
                home_total_dict = {
                    markets.HOME_TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.HOME_TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and home_total_dict:
                if markets.HOME_TOTAL not in self.result:
                    self.result[markets.HOME_TOTAL] = {}
                self.result[markets.HOME_TOTAL].update(
                    {home_total_key: home_total_dict})
            prob = 0

    def away_total(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j < val + 0.5:
                        prob += self.matrix[i, j]
            away_total_key = format_specifiers(markets.AWAY_TOTAL, {
                'total': str(val + 0.5 + self.score_2)})
            away_total_dict = {}

            if prob > 0 and prob < 1:
                away_total_dict = {
                    markets.AWAY_TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.AWAY_TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and away_total_dict:
                if markets.AWAY_TOTAL not in self.result:
                    self.result[markets.AWAY_TOTAL] = {}
                self.result[markets.AWAY_TOTAL].update(
                    {away_total_key: away_total_dict})
            prob = 0

    def winner_3_way_FH(self, mar=0.05, min_prob=0.02, max_odds=250):
        prob_1 = 0
        prob_2 = 0
        for i in range(self.poisson or self.poi_1):
            for j in range(self.poisson or self.poi_1):
                if j - i < -0.5 + self.score_1 - self.score_2:
                    prob_1 += self.matrix[i, j]
                if j - i > 0.5 + self.score_1 - self.score_2:
                    prob_2 += self.matrix[i, j]
        hand_key = format_specifiers(markets.FIRST_HALF_THREE_WAY_WINNER, {})
        hand_dict = {}

        if prob_1 > 0 and prob_2 > 0 and 1 - prob_1 - prob_2 > 0 and \
                prob_1 < 1 and prob_2 < 1 and 1 - prob_1 - prob_2 < 1:
            hand_dict = {
                markets.FIRST_HALF_THREE_WAY_WINNER_HOME: self.get_outcome(
                    self.margin(1 / prob_1, mar, max_odds), 0),
                markets.FIRST_HALF_THREE_WAY_WINNER_DRAW: self.get_outcome(
                    self.margin(1 / (1 - prob_1 - prob_2), mar, max_odds), 0),
                markets.FIRST_HALF_THREE_WAY_WINNER_AWAY: self.get_outcome(
                    self.margin(1 / prob_2, mar, max_odds), 0)
            }
        if (
            not self.betstop
            and prob_1 <= 1 - min_prob
            and prob_1 >= min_prob
            and prob_2 <= 1 - min_prob
            and prob_2 >= min_prob
            and 1 - prob_1 - prob_2 <= 1 - min_prob
            and 1 - prob_1 - prob_2 >= min_prob
            and hand_dict
        ):
            if markets.FIRST_HALF_THREE_WAY_WINNER not in self.result:
                self.result[markets.FIRST_HALF_THREE_WAY_WINNER] = {}
            self.result[markets.FIRST_HALF_THREE_WAY_WINNER].update(
                {hand_key: hand_dict})

    def double_chance_FH(self, mar=0.05, min_prob=0.02, max_odds=250):
        prob_1 = 0
        prob_2 = 0
        for i in range(self.poisson or self.poi_1):
            for j in range(self.poisson or self.poi_1):
                if j - i < 0.5 + self.score_1 - self.score_2:
                    prob_1 += self.matrix[i, j]
                if j - i > -0.5 + self.score_1 - self.score_2:
                    prob_2 += self.matrix[i, j]
        hand_key = format_specifiers(markets.FIRST_HALF_DOUBLE_CHANCE, {})
        hand_dict = {}

        if prob_1 > 0 and prob_2 > 0 and 2 - prob_1 - prob_2 > 0 and \
                prob_1 < 1 and prob_2 < 1 and 2 - prob_1 - prob_2 < 1:
            hand_dict = {
                markets.FIRST_HALF_DOUBLE_CHANCE_HOME_DRAW: self.get_outcome(
                    self.margin(1 / prob_1, mar, max_odds), 0),
                markets.FIRST_HALF_DOUBLE_CHANCE_HOME_AWAY: self.get_outcome(
                    self.margin(1 / (2 - prob_1 - prob_2), mar, max_odds), 0),
                markets.FIRST_HALF_DOUBLE_CHANCE_DRAW_AWAY: self.get_outcome(
                    self.margin(1 / prob_2, mar, max_odds), 0)
            }
        if (
            not self.betstop
            and prob_1 <= 1 - min_prob
            and prob_1 >= min_prob
            and prob_2 <= 1 - min_prob
            and prob_2 >= min_prob
            and 2 - prob_1 - prob_2 <= 1 - min_prob
            and 2 - prob_1 - prob_2 >= min_prob
            and hand_dict
        ):
            if markets.FIRST_HALF_DOUBLE_CHANCE not in self.result:
                self.result[markets.FIRST_HALF_DOUBLE_CHANCE] = {}
            self.result[markets.FIRST_HALF_DOUBLE_CHANCE].update(
                {hand_key: hand_dict})

    def total_FH(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(2 * self.poisson or 2 * self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if i + j < val + 0.5:
                        prob += self.matrix[i, j]
            total_key = format_specifiers(markets.FIRST_HALF_TOTAL, {
                'total': str(val + 0.5 + self.score_1 + self.score_2)})
            total_dict = {}

            if prob > 0 and prob < 1:
                total_dict = {
                    markets.FIRST_HALF_TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.FIRST_HALF_TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and total_dict:
                if markets.FIRST_HALF_TOTAL not in self.result:
                    self.result[markets.FIRST_HALF_TOTAL] = {}
                self.result[markets.FIRST_HALF_TOTAL].update(
                    {total_key: total_dict})
            prob = 0

    def handicap_FH(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(1 - (self.poisson or self.poi_1),
                         (self.poisson or self.poi_1) - 1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j - i > val + 0.5:
                        prob += self.matrix[i, j]
                        # print(val + 0.5, i, j, prob)
            hand_key = format_specifiers(markets.FIRST_HALF_HANDICAP, {
                'hcp': str(val + 0.5 - self.score_1 + self.score_2)})
            hand_dict = {}

            if prob > 0 and prob < 1:
                hand_dict = {
                    markets.FIRST_HALF_HANDICAP_HOME: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.FIRST_HALF_HANDICAP_AWAY: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and hand_dict:
                if markets.FIRST_HALF_HANDICAP not in self.result:
                    self.result[markets.FIRST_HALF_HANDICAP] = {}
                self.result[markets.FIRST_HALF_HANDICAP].update(
                    {hand_key: hand_dict})
            prob = 0

    def home_total_FH(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if i < val + 0.5:
                        prob += self.matrix[i, j]
            home_total_key = format_specifiers(markets.FIRST_HALF_HOME_TOTAL, {
                'total': str(val + 0.5 + self.score_1)})
            home_total_dict = {}

            if prob > 0 and prob < 1:
                home_total_dict = {
                    markets.FIRST_HALF_HOME_TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.FIRST_HALF_HOME_TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and home_total_dict:
                if markets.FIRST_HALF_HOME_TOTAL not in self.result:
                    self.result[markets.FIRST_HALF_HOME_TOTAL] = {}
                self.result[markets.FIRST_HALF_HOME_TOTAL].update(
                    {home_total_key: home_total_dict})
            prob = 0

    def away_total_FH(self, mar=0.05, min_prob=0.2, max_odds=25):
        prob = 0
        for val in range(self.poisson or self.poi_1):
            for i in range(self.poisson or self.poi_1):
                for j in range(self.poisson or self.poi_1):
                    if j < val + 0.5:
                        prob += self.matrix[i, j]
            away_total_key = format_specifiers(markets.FIRST_HALF_AWAY_TOTAL, {
                'total': str(val + 0.5 + self.score_2)})
            away_total_dict = {}

            if prob > 0 and prob < 1:
                away_total_dict = {
                    markets.FIRST_HALF_AWAY_TOTAL_OVER: self.get_outcome(
                        self.margin(1 / (1 - prob), mar, max_odds), 0),
                    markets.FIRST_HALF_AWAY_TOTAL_UNDER: self.get_outcome(
                        self.margin(1 / prob, mar, max_odds), 0)
                }

            if not self.betstop and prob <= 1 - min_prob and prob >= \
                    min_prob and away_total_dict:
                if markets.FIRST_HALF_AWAY_TOTAL not in self.result:
                    self.result[markets.FIRST_HALF_AWAY_TOTAL] = {}
                self.result[markets.FIRST_HALF_AWAY_TOTAL].update(
                    {away_total_key: away_total_dict})
            prob = 0
