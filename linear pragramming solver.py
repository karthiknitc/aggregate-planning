from pulp import *

def solve_aggregate_lp(demand, hire_cost, fire_cost, prod_cost, inv_cost, initial_workers, prod_per_worker):

    T = len(demand)

    model = LpProblem("Aggregate_Planning", LpMinimize)

    P = LpVariable.dicts("Production", range(T), lowBound=0)
    I = LpVariable.dicts("Inventory", range(T), lowBound=0)
    W = LpVariable.dicts("Workers", range(T), lowBound=0)
    H = LpVariable.dicts("Hire", range(T), lowBound=0)
    F = LpVariable.dicts("Fire", range(T), lowBound=0)

    model += lpSum([
        hire_cost * H[t] +
        fire_cost * F[t] +
        prod_cost * P[t] +
        inv_cost * I[t]
        for t in range(T)
    ])

    for t in range(T):
    
        if t == 0:
            model += P[t] == demand[t] + I[t]
        else:
            model += P[t] + I[t-1] == demand[t] + I[t]

        model += P[t] == prod_per_worker * W[t]


        if t == 0:
            model += W[t] == initial_workers + H[t] - F[t]
        else:
            model += W[t] == W[t-1] + H[t] - F[t]

    model.solve()

    print("\nStatus:", LpStatus[model.status])
    print("Total Cost =", value(model.objective), "\n")

    for t in range(T):
        print(f"--- Period {t+1} ---")
        print("Production:", value(P[t]))
        print("Inventory:", value(I[t]))
        print("Workers:", value(W[t]))
        print("Hire:", value(H[t]))
        print("Fire:", value(F[t]))
        print()

if __name__ == "__main__":
    demand = [80000, 50000, 120000, 150000]
    hire_cost = 1000
    fire_cost = 5000
    prod_cost = 20
    inv_cost = 5
    initial_workers = 100
    prod_per_worker = 1000

    solve_aggregate_lp(demand, hire_cost, fire_cost, prod_cost, inv_cost, initial_workers, prod_per_worker)