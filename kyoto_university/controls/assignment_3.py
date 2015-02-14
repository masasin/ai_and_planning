import itertools
import numpy as np


# Assignment details: http://goo.gl/aEMOE8
# Report: http://goo.gl/TW48Zm

def valid_combos(masses, mass_init, months_max):
    """Return and iterator for all legal combinations of removals

    Args:
        masses: A collection containing all possible removable masses.
        mass_init: The initial mass, in tonnes.
        months_max: The amount of months in which to finish the cleanup.
    """
    for p in itertools.product(masses, repeat=(months_max - 1)):
        s = sum(p)
        if s <= mass_init:
            yield p + (mass_init - s,)


def get_cost(combo, x, w):
    """Return the cost of a given sequence of actions.

    Args:
        combo: A sequence of removals.
        x: The mass at the start of the sequence, in tonnes.
        w: The weight of the environmental cost.

    Returns:
        cost: The cost of the sequence.
    """
    if len(combo) == 1:
        return combo[0]**2 + w * x**2

    return combo[-1]**2 + w * x**2 + get_cost(combo[:-1], x + combo[-1], w)


def get_leg(x_old, x_new, w):
    """Get the cost of a given movement.

    Args:
        x_old: Previous amount; can be a numpy array.
        x_new: Next amount; can be a numpy array.
        w: Weight of the environmental cost.

    Returns:
        cost: The cost of moving from one amount to another.
    """
    return (x_new - x_old)**2 + w * x_new**2


def brute_force_solution(mass_init=8, mass_res=1, months_max=3, weights=(1,)):
    """Use the brute force method to generate the solution.

    Args:
        mass_init: Initial mass, in tonnes. Default is 8.
        mass_res: The minimum mass that can be taken, in tonnes. Default is 1.
        months_max: The amount of months to finish by. Default is 3.
        weights: A tuple containing the weights to test. Even if only one
            weight is to be tested, it should be input as a tuple. Default is
            (1,).
    """
    masses = np.arange(0, mass_init + mass_res, mass_res)  # All possibilities.

    for weight in weights:
        combos = valid_combos(masses, mass_init, months_max)
        results = {}

        # Store results of each combination.
        for combo in combos:
            results[combo] = get_cost(combo, 0, weight)

        # Find combination with minimum cost.
        best = min(results, key=lambda x: results[x])
        cost = results[best]

        # Report the results.
        print("For w = {}:".format(weight))
        print("    Optimal transportation schedule: {}".format(best))
        print("    Cost: {}".format(cost))


def dynamic_solution(mass_init=8, mass_res=1, months_max=3, weights=(1,)):
    """Use dynamic programming to find the optimal solution.

    Args:
        mass_init: Initial mass, in tonnes. Default is 8.
        mass_res: The minimum mass that can be taken, in tonnes. Default is 1.
        months_max: The amount of months to finish by. Default is 3.
        weights: A tuple containing the weights to test. Even if only one
            weight is to be tested, it should be input as a tuple. Default is
            (1,).
    """
    masses = np.arange(0, mass_init + mass_res, mass_res)  # All possibilities.

    for weight in weights:
        # Initialize cost matrix.
        costs = np.zeros((months_max, len(masses), len(masses)))

        # Generate cost matrix using reverse recursion.
        costs[-1] = get_leg(masses, 0, weight)  # Last step
        for i in reversed(range(1, months_max - 1)):
            for j in range(len(masses)):
                costs[i, j] = get_leg(j, masses, weight) +\
                    costs[i+1].min(axis=0 if i+2 == months_max else 1)
        costs[0] = get_leg(mass_init, masses, weight) + costs[1].min(axis=1)

        # Calculate x.
        x = np.zeros(months_max + 1)
        x[0] = mass_init
        x[1] = np.argmin(costs[0].min(axis=0))
        for i in range(1, months_max):
            x[i+1] = np.argmin(costs[i, x[i]])

        # Calculate u.
        u = np.zeros(months_max)
        for i in range(months_max):
            u[i] = x[i] - x[i+1]

        # Report result.
        print("For w = {}:".format(weight))
        print("    Optimal transportation schedule: {}".format(u))
        print("    Cost: {}".format(costs[0].min(axis=0)[x[1]]))
