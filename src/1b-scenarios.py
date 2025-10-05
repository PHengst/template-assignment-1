import gurobipy as gp
from gurobipy import GRB, nlfunc
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import os


def run_model_1b(
    scenario,
    Lmin_t,
    Lmax_t,
    Pt_PV,
    pt,
    Lt_ref,
    max_import_kW,
    max_export_kW,
    tau_imp,
    tau_exp,
    alpha=10,
    model_prefix="1b"
):
    """
    Runs Model 1b for a single scenario.
    """

    results_folder = "src/scenario-results"
    os.makedirs(results_folder, exist_ok=True)

    model = gp.Model("Model_1b")
    HOURS = list(range(24))
    lb = 0.0
    ub = float("inf")

    # Decision variables
    Lt = {t: model.addVar(Lmin_t, Lmax_t, vtype=GRB.CONTINUOUS, name=f"L{t}") for t in HOURS}
    ut = {t: model.addVar(lb, ub, vtype=GRB.CONTINUOUS, name=f"u{t}") for t in HOURS}
    ct = {t: model.addVar(lb, ub, vtype=GRB.CONTINUOUS, name=f"c{t}") for t in HOURS}
    gt_imp = {t: model.addVar(lb, max_import_kW, vtype=GRB.CONTINUOUS, name=f"g{t}_imp") for t in HOURS}
    gt_exp = {t: model.addVar(lb, max_export_kW, vtype=GRB.CONTINUOUS, name=f"g{t}_exp") for t in HOURS}
    HCt = {t: model.addVar(-ub, ub, vtype=GRB.CONTINUOUS, name=f"HC{t}") for t in HOURS}
    Dt = {t: model.addVar(lb, ub, vtype=GRB.CONTINUOUS, name=f"D{t}") for t in HOURS}

    model.update()

    # Constraints
    for t in HOURS:
        model.addLConstr(ut[t] + ct[t], GRB.EQUAL, Pt_PV[t], name=f"PV_allocation_{t}")
        model.addLConstr(ut[t] + gt_imp[t], GRB.EQUAL, Lt[t] + gt_exp[t], name=f"Energy_balance_{t}")
        model.addConstr((pt[t] + tau_imp) * gt_imp[t] - (pt[t] - tau_exp) * gt_exp[t] == HCt[t], name=f"Hourly_cost_{t}")
        model.addConstr(nlfunc.square(Lt_ref[t] - Lt[t]) == Dt[t], name=f"Discomfort_{t}")

    # Objective: minimize cost + discomfort
    model.setObjective(gp.quicksum(alpha * Dt[t] + HCt[t] for t in HOURS), GRB.MINIMIZE)
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print(f"Optimization {scenario} successful! Objective = {model.ObjVal:.3f}")
    elif model.status == GRB.INFEASIBLE:
        print(f"Model {scenario} is infeasible.")
    elif model.status == GRB.UNBOUNDED:
        print(f" Model {scenario} is unbounded.")
    else:
        print(f"Optimization ended with status: {model.status}")

    Lt_values = [Lt[t].X for t in HOURS]
    ut_values = [ut[t].X for t in HOURS]
    ct_values = [ct[t].X for t in HOURS]
    gt_imp_values = [gt_imp[t].X for t in HOURS]
    gt_exp_values = [gt_exp[t].X for t in HOURS]

    # --------- PLOT 1: Decision Variables ----------
    plt.figure(figsize=(12, 6))
    plt.plot(HOURS, Lt_values, label="Load Consumption (Lt)", marker="o")
    plt.plot(HOURS, ut_values, label="PV not curtailed (ut)", marker="s")
    plt.plot(HOURS, ct_values, label="PV Curtailed (ct)", marker="^")
    plt.plot(HOURS, gt_imp_values, label="Grid Import (gt_imp)", marker="x")
    plt.plot(HOURS, gt_exp_values, label="Grid Export (gt_exp)", marker="D")
    plt.plot(HOURS, Pt_PV, label="PV Production (Pt_PV)", marker="*")
    plt.plot(HOURS, Lt_ref, label="Reference Load (Lt_ref)", marker="P")
    plt.xlabel("Hour")
    plt.ylabel("Value (kWh)")
    plt.title(f"Scenario {scenario}: Model 1b Decision Variables")
    plt.xticks(HOURS)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_folder, f"{model_prefix}-scenario-{scenario}-AllDecisionVariables.png"))
    plt.show()
    plt.close()

    # --------- PLOT 2: Energy Price vs Grid ----------
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel("Hour")
    ax1.set_ylabel("Energy Price (DKK/kWh)", color="tab:red")
    ax1.plot(HOURS, pt, color="tab:red", marker="o", label="Energy Price")
    ax1.tick_params(axis="y", labelcolor="tab:red")
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Energy (kWh)", color="tab:blue")
    ax2.plot(HOURS, gt_imp_values, color="tab:blue", marker="x", linestyle="dashed", label="Grid Import")
    ax2.plot(HOURS, gt_exp_values, color="tab:green", marker="D", linestyle="dashed", label="Grid Export")
    ax2.tick_params(axis="y", labelcolor="tab:blue")

    plt.title(f"Scenario {scenario}: Energy Price vs. Grid Import/Export")
    fig.tight_layout()
    fig.legend(loc="upper right", bbox_to_anchor=(1, 1))
    plt.xticks(HOURS)
    plt.savefig(os.path.join(results_folder, f"{model_prefix}-scenario-{scenario}-EnergyPriceVsGrid.png"))
    plt.show()
    plt.close()

    return {
        "Lt": Lt_values,
        "ut": ut_values,
        "ct": ct_values,
        "gt_imp": gt_imp_values,
        "gt_exp": gt_exp_values,
        "objective": model.ObjVal if model.status == GRB.OPTIMAL else None,
    }


# ========== MAIN EXECUTION LOOP ==========
if __name__ == "__main__":
    # Load all inputs
    with open("./data/question_1b/bus_params.json", "r") as file:
        bus_params = json.load(file)
    with open("./data/question_1b/DER_production.json", "r") as file:
        der_production = json.load(file)
    with open("./data/question_1b/appliance_params.json", "r") as file:
        appl_params = json.load(file)
    with open("./data/question_1b/usage_preferences.json", "r") as file:
        usage_preference = json.load(file)
    with open("./data/scenarios.json", "r") as file:
        scenarios = json.load(file)

    Lmin_t = 0.0
    Lmax_t = appl_params["load"][0]["max_load_kWh_per_hour"]
    Pt_PV = der_production[0]["hourly_profile_ratio"]
    Lt_ref = usage_preference[0]["load_preferences"][0]["hourly_profile_ratio"]

    results_summary = []

    for sc in scenarios:
        print(f"\n--- Running {sc['scenario']} ---")
        result = run_model_1b(
            scenario=sc["scenario"],
            Lmin_t=Lmin_t,
            Lmax_t=Lmax_t,
            Pt_PV=Pt_PV,
            pt=sc["energy_price_DKK_per_kWh"],
            Lt_ref=Lt_ref,
            max_import_kW=sc["max_import_kW"],
            max_export_kW=sc["max_export_kW"],
            tau_imp=sc["import_tariff_DKK/kWh"],
            tau_exp=sc["export_tariff_DKK/kWh"],
            model_prefix="1b",
        )

        results_summary.append({
            "Scenario": sc["scenario"],
            "Primal Objective": result["objective"],
        })

    if not results_summary:
        print("No results found. Please run the scenarios first.")
    else:
        df_results = pd.DataFrame(results_summary)
        print("\n===== RESULTS SUMMARY =====")
        print(df_results)
