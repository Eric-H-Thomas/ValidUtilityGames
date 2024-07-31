import numpy as np
import pandas as pd

class WelfareFunction:
    def compute_welfare(self, *args, **kwargs):
        raise NotImplementedError("Subclasses should implement this method.")

class TotalPlayerWelfare(WelfareFunction):
    def __init__(self, action_set):
        self.action_set = action_set

    def compute_welfare(self, action_profile):
        """
        action set: the set of all possible actions
        """
        utility = 0
        for action in self.action_set:
            utility += self.resource_welfare(action_profile, action)
        return utility

    def resource_welfare(self, action_profile, resource):
        """
        calculates the welfare function for a given resource
        """
        players_who_chose_resource = self.get_players_chose_resource(action_profile, resource)
        resource_welfare = len(players_who_chose_resource)
        return resource_welfare

    def get_players_chose_resource(self, action_profile, resource):
        """
        Returns a list of players who chose a given resource
        """
        players_chose_resource = []
        for player, player_action in action_profile.iterrows():
            if resource in player_action:
                players_chose_resource.append(player)

        return players_chose_resource
    
class RouteGameWelfare:
    def __init__(self):
        resource_welfare = np.array([[0, 5, 1, 10],
                                     [0, 1, 4, 6],
                                     [0, 1, 2, 4],
                                     [0, 1, 2, 4],
                                     [0, 1, 2, 4]])

        self.action_set = ['AD', 'CB', 'AB', 'BD', 'CD']
        self.resource_welfare = pd.DataFrame(resource_welfare, index=self.action_set)
        
    def compute_welfare(self, action_profile):
        """
        action set: the set of all possible actions
        """
        welfare = 0
        # get the players who chose each resource
        action_counts = [[] for i in range(len(self.action_set))]
        for i, action in enumerate(self.action_set):
            for player, player_action in action_profile.iterrows():
                if action in player_action:
                    action_counts[i] += 1

        # calculate the welfare for each resource
        for i, action in enumerate(self.action_set):
            welfare += self.resource_welfare.loc[action, action_counts[i]]

        return welfare

class Valid_Utility_Game():
    def __init__(self, action_set, welfare):
        """
        action_set: the set of all possible actions
        welfare: the welfare function used to calculate the utility of the game
        """
        self.action_set = action_set
        self.welfare = welfare

    def ind_util_marg_cont(self, action_profile, player):
        """
        Calculates the marginal contribution of a player to the welfare function
        """
        action_prof_sans_player = action_profile.drop(player)
        utility = (self.welfare.compute_welfare(self.action_set, action_profile) 
                   - self.welfare.compute_welfare(self.action_set, action_prof_sans_player))
        return utility
    
    def price_of_anarchy():
        """
        Calculates the price of anarchy of the game
        """


# make the action profile (as a dataframe) for the route game
action_profile = pd.DataFrame({'player1': ['AB', 'BD'],
                                'player2': ['CD', 'AD', 'AB'],})

# create the welfare function
welfare = RouteGameWelfare()

# create the game
game = Valid_Utility_Game(welfare.action_set, welfare)

poa = game.price_of_anarchy(action_profile)