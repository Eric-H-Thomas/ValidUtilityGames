import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union


def create_random_circles(n, radius_range, board_size):
    _circles = []
    for _ in range(n):
        radius = np.random.uniform(*radius_range)
        center = (np.random.uniform(radius, board_size[0] - radius),
                  np.random.uniform(radius, board_size[1] - radius))
        _circles.append((center, radius))
    return _circles


# Function to check circles for equality
def circles_are_the_same(circle1, circle2):
    center1, radius1 = circle1
    center2, radius2 = circle2
    return center1 == center2 and radius1 == radius2


def total_covered_area(_circles):
    shapes = [Point(c[0]).buffer(c[1]) for c in _circles]
    union = unary_union(shapes)
    return union.area


# Function to visualize the circles
def plot_circles(_ax, _circles, chosen_indices=None):
    _ax.clear()
    for idx, c in enumerate(_circles):
        circle = plt.Circle(c[0], c[1], fill=True, alpha=0.5, edgecolor='black')
        if chosen_indices and idx in chosen_indices:
            circle.set_edgecolor('red')
            circle.set_linewidth(2)
        _ax.add_artist(circle)
    _ax.set_xlim(0, boardSize[0])
    _ax.set_ylim(0, boardSize[1])
    _ax.set_aspect('equal', adjustable='box')
    plt.draw()


def simulate_game(_circles, player_choices):
    chosen_circles = [_circles[i] for i in player_choices]
    social_welfare = total_covered_area(chosen_circles)

    # Calculate marginal contribution for each player
    _contributions = []
    for i in range(len(player_choices)):
        other_circles = [_circles[j] for j in player_choices if j != player_choices[i]]
        area_without = total_covered_area(other_circles)
        area_with = total_covered_area(other_circles + [_circles[player_choices[i]]])
        _contributions.append(area_with - area_without)

    return _contributions, social_welfare


# Function to calculate the Shapley value for each player
def calculate_shapley_values(_circles, player_choices):
    num_players = len(player_choices)
    shapley_values = np.zeros(num_players)
    factorial = math.factorial

    for i in range(num_players):
        # Get all possible coalitions
        for coalition in itertools.chain.from_iterable(
                itertools.combinations(range(num_players), r) for r in range(num_players + 1)):
            # Iterate over all the coalitions in which player i is absent
            if i not in coalition:
                # Get the marginal contribution of player i
                coalition_with_i = list(coalition) + [i]
                area_without = total_covered_area([_circles[player_choices[j]] for j in coalition])
                area_with = total_covered_area([_circles[player_choices[j]] for j in coalition_with_i])
                marginal_contribution = area_with - area_without
                # Add the weighted marginal contribution to player i's Shapley value
                shapley_values[i] += marginal_contribution * (
                            factorial(len(coalition)) * factorial(num_players - len(coalition) - 1)) / factorial(
                    num_players)

    return shapley_values


# Function to calculate the Shapley value for a single player
def get_shapley_value(new_circle, set_circles):
    num_players = len(set_circles) + 1
    shapley_value = 0
    factorial = math.factorial

    # Get all possible coalitions that the player in question could join
    for coalition in itertools.chain.from_iterable(
            itertools.combinations(range(num_players - 1), r) for r in range(num_players)):
        # Get the marginal contribution of the player in question
        list_circles_without = [set_circles[j] for j in coalition]
        area_without = total_covered_area(list_circles_without)
        area_with = total_covered_area(list_circles_without + [new_circle])
        marginal_contribution = area_with - area_without
        # Add the weighted marginal contribution to player i's Shapley value
        shapley_value += marginal_contribution * (
                factorial(len(coalition)) * factorial(num_players - len(coalition) - 1)) / factorial(
            num_players)
    return shapley_value


# Function to calculate the marginal contribution for a single player
def get_marginal_contribution(new_circle, set_circles):
    new_set_circles = set_circles.copy()
    new_set_circles.append(new_circle)
    return total_covered_area(new_set_circles) - total_covered_area(set_circles)


def get_circle_with_largest_marginal_contribution(_circles, circles_chosen):
    greatest_marginal_contribution = 0.0
    circle_with_largest_marginal_contribution = _circles[0]
    for circle in _circles:
        if circle not in circles_chosen:
            marginal_contribution = get_marginal_contribution(circle, circles_chosen)
            if marginal_contribution >= greatest_marginal_contribution:
                greatest_marginal_contribution = marginal_contribution
                circle_with_largest_marginal_contribution = circle
    return circle_with_largest_marginal_contribution


def get_circle_with_largest_shapley_value(_circles, circles_chosen):
    greatest_shapley_value = 0.0
    circle_with_largest_shapley_value = _circles[0]
    for circle in _circles:
        if circle not in circles_chosen:
            shapley_value = get_shapley_value(circle, circles_chosen)
            if shapley_value >= greatest_shapley_value:
                greatest_shapley_value = shapley_value
                circle_with_largest_shapley_value = circle
    return circle_with_largest_shapley_value


def calculate_optimal_social_welfare(_circles, num_players):
    max_area = 0
    # Iterate over every possible selection of num_players circles
    for subset in itertools.combinations(_circles, num_players):
        area = total_covered_area(subset)
        if area > max_area:
            max_area = area
    return max_area


def is_nash_equilibrium_marginal_utility(circles_chosen, all_circles):
    # Convert the tuple to a list for manipulation
    circles_chosen_list = list(circles_chosen)

    for i, circle in enumerate(circles_chosen_list):
        # Get the circles chosen by all players other than the one in question
        circles_from_other_players = circles_chosen_list[:i] + circles_chosen_list[i + 1:]

        # Find the best option for the current player
        best_option = get_circle_with_largest_marginal_contribution(all_circles, circles_from_other_players)

        # If the best option is not the one chosen by the player, it's not a Nash Equilibrium
        if not circles_are_the_same(best_option, circle):
            return False
    return True


def is_nash_equilibrium_shapley_utility(circles_chosen, all_circles):
    # Convert the tuple to a list for manipulation
    circles_chosen_list = list(circles_chosen)

    for i, circle in enumerate(circles_chosen_list):
        # Get the circles chosen by all players other than the one in question
        circles_from_other_players = circles_chosen_list[:i] + circles_chosen_list[i + 1:]

        # Find the best option for the current player
        best_option = get_circle_with_largest_shapley_value(all_circles, circles_from_other_players)

        # If the best option is not the one chosen by the player, it's not a Nash Equilibrium
        if not circles_are_the_same(best_option, circle):
            return False
    return True


def calculate_worst_NE_with_marginal_utility(_circles, num_players):
    # Brute force approach; Has a time complexity of (circles)^(players).
    min_area = math.inf
    # Iterate over every possible selection of num_players circles
    for subset in itertools.combinations(_circles, num_players):
        if is_nash_equilibrium_marginal_utility(subset, _circles):
            area = total_covered_area(subset)
            if area < min_area:
                min_area = area
    return min_area


def calculate_worst_NE_with_shapley_utility(_circles, num_players):
    # Brute force approach; Has a time complexity of (circles)^(players).
    min_area = math.inf
    # Iterate over every possible selection of num_players circles
    for subset in itertools.combinations(_circles, num_players):
        if is_nash_equilibrium_shapley_utility(subset, _circles):
            area = total_covered_area(subset)
            if area < min_area:
                min_area = area
    return min_area


def approximate_optimal_social_welfare(_circles, num_players):
    circlesChosen = []
    for _ in range(num_players):
        choice = get_circle_with_largest_marginal_contribution(_circles, circlesChosen)
        circlesChosen.append(choice)
    return total_covered_area(circlesChosen)


def calculate_price_of_anarchy_with_marginal_utility(_circles, num_players):
    # Calculate the optimal_social_welfare
    optimal_social_welfare = calculate_optimal_social_welfare(_circles, num_players)

    # Calculate the worst equilibrium welfare using marginal utility
    worst_NE_welfare = calculate_worst_NE_with_marginal_utility(_circles, num_players)

    # Calculate the POA using marginal utility
    return optimal_social_welfare / worst_NE_welfare


def calculate_price_of_anarchy_with_shapley_utility(_circles, num_players):
    # Calculate the optimal_social_welfare
    optimal_social_welfare = calculate_optimal_social_welfare(_circles, num_players)

    # Calculate the worst equilibrium welfare using marginal utility
    worst_NE_welfare = calculate_worst_NE_with_shapley_utility(_circles, num_players)

    # Calculate the POA using marginal utility
    return optimal_social_welfare / worst_NE_welfare


# Parameters
numPlayers = 3
numCircles = 10
radiusRange = (1, 3)
boardSize = (10, 10)

# Create random circles
circles = create_random_circles(numCircles, radiusRange, boardSize)

# Interactive part
chosenIndices = []


def onclick(event):
    global chosenIndices
    for i, c in enumerate(circles):
        distance = np.sqrt((c[0][0] - event.xdata) ** 2 + (c[0][1] - event.ydata) ** 2)
        if distance <= c[1]:
            if i not in chosenIndices:
                chosenIndices.append(i)
            else:
                chosenIndices.remove(i)
            break
    plot_circles(ax, circles, chosenIndices)


# Plot the circles and set up the event handler
fig, ax = plt.subplots()
plot_circles(ax, circles)

cid = fig.canvas.mpl_connect('button_press_event', onclick)

# Show the plot and wait for user interaction
plt.show()

# Simulate the game after selection is complete
contributions, socialWelfare = simulate_game(circles, chosenIndices)

# Calculate Shapley values
shapleyValues = calculate_shapley_values(circles, chosenIndices)

# Calculate/approximate optimal social welfare
smallGame = True
if numCircles > 20:
    smallGame = False

optimalSocialWelfare = 0.0
if smallGame:
    optimalSocialWelfare = calculate_optimal_social_welfare(circles, numPlayers)
else:
    optimalSocialWelfare = approximate_optimal_social_welfare(circles, numPlayers)


# Calculate Price of Anarchy
poaMarginal = calculate_price_of_anarchy_with_marginal_utility(circles, numPlayers)
poaShapley = calculate_price_of_anarchy_with_shapley_utility(circles, numPlayers)

# Display results
if numPlayers != len(chosenIndices):
    raise Exception("\nGame was set to have {0} players, but only {1} circles were chosen".format(numPlayers, len(chosenIndices)))


print("Player Contributions:", contributions)
print("Social Welfare:", socialWelfare)
print("Shapley Values:", shapleyValues)
if smallGame:
    print("Optimal Social Welfare:", optimalSocialWelfare)
    print("Price of Anarchy (Marginal):", poaMarginal)
    print("Price of Anarchy (Shapley):", poaShapley)
else:
    print("Approximate Social Welfare:", optimalSocialWelfare)
