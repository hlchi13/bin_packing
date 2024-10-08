import hexaly.optimizer
import sys
import math

if len(sys.argv) < 2:
    print("Usage: python bin_packing.py inputFile [outputFile] [timeLimit]")
    sys.exit(1)


def read_integers(filename):
    with open(filename) as f:
        return [int(elem) for elem in f.read().split()]


with hexaly.optimizer.HexalyOptimizer() as optimizer:
    # Read instance data
    file_it = iter(read_integers(sys.argv[1]))

    nb_items = int(next(file_it))
    bin_capacity = int(next(file_it))

    weights_data = [int(next(file_it)) for i in range(nb_items)]
    nb_min_bins = int(math.ceil(sum(weights_data) / float(bin_capacity)))
    nb_max_bins = min(nb_items, 2 * nb_min_bins)

    #
    # Declare the optimization model
    #
    model = optimizer.model

    # Set decisions: bin[k] represents the items in bin k
    bins = [model.set(nb_items) for _ in range(nb_max_bins)]

    # Each item must be in one bin and one bin only
    model.constraint(model.partition(bins))

    # Create an array and a function to retrieve the item's weight
    weights = model.array(weights_data)
    weight_lambda = model.lambda_function(lambda i: weights[i])

    # Weight constraint for each bin
    bin_weights = [model.sum(b, weight_lambda) for b in bins]
    for w in bin_weights:
        model.constraint(w <= bin_capacity)

    # Bin k is used if at least one item is in it
    bins_used = [model.count(b) > 0 for b in bins]

    # Count the used bins
    total_bins_used = model.sum(bins_used)

    # Minimize the number of used bins
    model.minimize(total_bins_used)
    model.close()

    # Parameterize the optimizer
    if len(sys.argv) >= 4:
        optimizer.param.time_limit = int(sys.argv[3])
    else:
        optimizer.param.time_limit = 5

    # Stop the search if the lower threshold is reached
    optimizer.param.set_objective_threshold(0, nb_min_bins)

    optimizer.solve()

    # Write the solution in a file
    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'w') as f:
            for k in range(nb_max_bins):
                if bins_used[k].value:
                    f.write("Bin weight: %d | Items: " % bin_weights[k].value)
                    for e in bins[k].value:
                        f.write("%d " % e)
                    f.write("\n")
