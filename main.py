import itertools
import math
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from shapely.ops import unary_union


# Function to create random circles
def create_random_circles(n, radius_range, board_size):
    _circles = []
    for _ in range(n):
        radius = np.random.uniform(*radius_range)
        center = (np.random.uniform(radius, board_size[0] - radius),
                  np.random.uniform(radius, board_size[1] - radius))
        _circles.append((center, radius))
    return _circles


# Function to calculate the total covered area of given circles
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


# Function to simulate the game
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
        for coalition in itertools.chain.from_iterable(
                itertools.combinations(range(num_players), r) for r in range(num_players + 1)):
            if i not in coalition:
                coalition_with_i = list(coalition) + [i]
                area_without = total_covered_area([_circles[player_choices[j]] for j in coalition])
                area_with = total_covered_area([_circles[player_choices[j]] for j in coalition_with_i])
                marginal_contribution = area_with - area_without
                shapley_values[i] += marginal_contribution * (
                            factorial(len(coalition)) * factorial(num_players - len(coalition) - 1)) / factorial(
                    num_players)

    return shapley_values


# Function to calculate the optimal social welfare
def calculate_optimal_social_welfare(_circles):
    return total_covered_area(_circles)


# Function to calculate the Price of Anarchy
def calculate_price_of_anarchy(_circles, player_choices):
    _, social_welfare_marginal = simulate_game(_circles, player_choices)
    shapley_values = calculate_shapley_values(_circles, player_choices)

    sorted_indices_by_shapley = np.argsort(-shapley_values).tolist()
    _, social_welfare_shapley = simulate_game(_circles, sorted_indices_by_shapley)

    optimal_social_welfare = calculate_optimal_social_welfare(_circles)

    poa_marginal = optimal_social_welfare / social_welfare_marginal
    poa_shapley = optimal_social_welfare / social_welfare_shapley

    return poa_marginal, poa_shapley


# Parameters
numCircles = 6
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

# Calculate Price of Anarchy
poaMarginal, poaShapley = calculate_price_of_anarchy(circles, chosenIndices)

# Display results
print("Player Contributions:", contributions)
print("Social Welfare:", socialWelfare)
print("Shapley Values:", shapleyValues)
print("Price of Anarchy (Marginal):", poaMarginal)
print("Price of Anarchy (Shapley):", poaShapley)
