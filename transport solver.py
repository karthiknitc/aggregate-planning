from pulp import *

def solve_transport():

    # -----------------------------
    # DATA (from your question)
    # -----------------------------

    demand = [900, 1500, 1600, 3000]

    regular_cap = [1000, 1200, 1300, 1300]
    overtime_cap = [100, 150, 200, 200]
    subcontract_cap = [500, 500, 500, 500]

    prod_cost = {
        "R": 20,
        "O": 25,
        "S": 28
    }

    inv_cost = 3
    begin_inventory = 300

    T = 4  # number of periods

    # -----------------------------
    # MODEL
    # -----------------------------
    model = LpProblem("Transport_Aggregate", LpMinimize)

    # Decision variables
    # x[type, i, j] → produced in period i used in period j
    x = {}

    types = ["R", "O", "S"]

    for t in types:
        for i in range(T):
            for j in range(i, T):  # only forward
                x[(t, i, j)] = LpVariable(f"x_{t}_{i}_{j}", lowBound=0)

    # Beginning inventory variables
    inv = {}
    for j in range(T):
        inv[j] = LpVariable(f"inv_{j}", lowBound=0)

    # -----------------------------
    # OBJECTIVE FUNCTION
    # -----------------------------
    model += lpSum([
        x[(t, i, j)] * (prod_cost[t] + (j - i) * inv_cost)
        for t in types
        for i in range(T)
        for j in range(i, T)
    ]) + lpSum([
        inv[j] * (j * inv_cost)
        for j in range(T)
    ])

    # -----------------------------
    # SUPPLY CONSTRAINTS
    # -----------------------------
    for i in range(T):
        model += lpSum([x[("R", i, j)] for j in range(i, T)]) <= regular_cap[i]
        model += lpSum([x[("O", i, j)] for j in range(i, T)]) <= overtime_cap[i]
        model += lpSum([x[("S", i, j)] for j in range(i, T)]) <= subcontract_cap[i]

    # Beginning inventory constraint
    model += lpSum([inv[j] for j in range(T)]) <= begin_inventory

    # -----------------------------
    # DEMAND CONSTRAINTS
    # -----------------------------
    for j in range(T):
        model += (
            lpSum([x[(t, i, j)] for t in types for i in range(j + 1)])
            + inv[j]
            == demand[j]
        )

    # -----------------------------
    # SOLVE
    # -----------------------------
    model.solve()

    # -----------------------------
    # OUTPUT
    # -----------------------------
    print("\nStatus:", LpStatus[model.status])
    total_cost = value(model.objective)
    print("Total Cost =", round(total_cost, 2) if total_cost else "Not computed")

    types_full = {"R": "Regular", "O": "Overtime", "S": "Subcontract"}

    # Header
    print(f"{'Period of Production':<25}", end="")
    for j in range(T):
        print(f"{'Q'+str(j+1):<10}", end="")
    print(f"{'Unused':<10}{'Available':<10}")

    print("-" * 80)

    # Beginning Inventory row
    print(f"{'Beginning Inventory':<25}", end="")
    for j in range(T):
        val = value(inv[j])
        val = round(val, 2) if val else 0
        print(f"{val:<10}", end="")
    print(f"{'-':<10}{begin_inventory:<10}")

    print("-" * 80)

    # Production rows
    for i in range(T):
        for t in ["R", "O", "S"]:
            row_name = f"{i+1} {types_full[t]}"
            print(f"{row_name:<25}", end="")

            used = 0

            for j in range(T):
                if j >= i:
                    val = value(x[(t, i, j)])
                    val = round(val, 2) if val else 0
                else:
                    val = 0

                used += val
                print(f"{val:<10}", end="")

            # Capacity
            if t == "R":
                cap = regular_cap[i]
            elif t == "O":
                cap = overtime_cap[i]
            else:
                cap = subcontract_cap[i]

            unused = cap - used

            print(f"{round(unused,2):<10}{cap:<10}")

        print("-" * 80)

    # Demand row
    print(f"{'Demand':<25}", end="")
    for j in range(T):
        print(f"{demand[j]:<10}", end="")
    print()

# Run
if __name__ == "__main__":
    solve_transport()