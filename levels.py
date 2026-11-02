"""Level definitions: story, starter code, reference solution, and checker."""
import math
from dataclasses import dataclass
from typing import Callable

import science as sc


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _close(a, b, tol=0.01):
    return _num(a) and abs(a - b) <= tol * abs(b)


# ---------------------------------------------------------------- Level 1
L1_STARTER = '''\
# Mission: activate the base fluid.
v_particles = 0.5   # mL of magnetite (Fe3O4) nanoparticles
v_fluid = 9.5       # mL of water
k_f = 0.6           # W/m.K, thermal conductivity of water
k_p = 7.0           # W/m.K, thermal conductivity of Fe3O4

# TODO 1: volume fraction of particles in the mixture
phi = None

# TODO 2: effective thermal conductivity (Maxwell model, see the formula above)
k_eff = None

print("phi =", phi)
print("k_eff =", k_eff)
'''

L1_SOLUTION = '''\
v_particles = 0.5
v_fluid = 9.5
k_f = 0.6
k_p = 7.0

phi = v_particles / (v_particles + v_fluid)
k_eff = k_f * (k_p + 2*k_f + 2*phi*(k_p - k_f)) / (k_p + 2*k_f - phi*(k_p - k_f))

print("phi =", phi)
print("k_eff =", k_eff)
'''


def check_l1(g):
    ref_phi = sc.volume_fraction(0.5, 9.5)
    ref_k = sc.maxwell_k_eff(ref_phi)
    phi, k = g.get("phi"), g.get("k_eff")
    ok, msgs = True, []
    if not _num(phi):
        ok = False
        msgs.append("`phi` is still empty. Fill in TODO 1.")
    elif not _close(phi, ref_phi):
        ok = False
        if _close(phi, 0.5 / 9.5):
            msgs.append("Careful: the volume fraction divides by the TOTAL volume "
                        "(particles + fluid), not by the fluid alone.")
        else:
            msgs.append(f"`phi` = {phi:.4f} isn't right. "
                        "phi = V_particles / (V_particles + V_fluid).")
    if not _num(k):
        ok = False
        msgs.append("`k_eff` is still empty. Fill in TODO 2.")
    elif _num(phi) and not _close(k, ref_k):
        ok = False
        msgs.append(f"`k_eff` = {k:.4f} doesn't match the Maxwell formula. "
                    "Check your brackets: the numerator and denominator each need "
                    "their own parentheses.")
    if ok:
        msgs.append(f"phi = {phi:.4f} ({phi*100:.1f}% by volume). "
                    f"k_eff = {k:.4f} W/m.K, about {100*(k/0.6 - 1):.1f}% better at "
                    "conducting heat than plain water.")
    return ok, msgs


# ---------------------------------------------------------------- Level 2
L2_STARTER = '''\
# Mission: find the particle sizes that stay dispersed (no agglomeration).
# stability_index(d) is provided: a value >= 1 means the fluid is stable.

stable_sizes = []

for d in range(5, 61, 5):          # particle diameters in nm
    # TODO: if the stability index of d is at least 1, add d to stable_sizes
    pass

print("Stable sizes (nm):", stable_sizes)
'''

L2_SOLUTION = '''\
stable_sizes = []

for d in range(5, 61, 5):
    if stability_index(d) >= 1:
        stable_sizes.append(d)

print("Stable sizes (nm):", stable_sizes)
'''


def check_l2(g):
    expected = [d for d in range(5, 61, 5) if sc.stability_index(d) >= 1]
    got = g.get("stable_sizes")
    if not isinstance(got, list):
        return False, ["`stable_sizes` must be a list."]
    if got == expected:
        return True, [f"Stable window found: {got[0]} to {got[-1]} nm. Smaller particles "
                      "are too weak to steer; larger ones clump together and settle."]
    msgs = []
    missing = [d for d in expected if d not in got]
    extra = [d for d in got if d not in expected]
    if not got:
        msgs.append("`stable_sizes` is empty. Did you append inside the loop?")
    if missing:
        msgs.append(f"Missing stable sizes: {missing}. Is your comparison `>= 1`?")
    if extra:
        msgs.append(f"These sizes are NOT stable but are in your list: {extra}.")
    return False, msgs


# ---------------------------------------------------------------- Level 3
L3_STARTER = '''\
# Mission: decide if a dose + magnetic field is safe AND therapeutic.
# Provided for you:
#   body_temperature(conc, field)  -> tissue temperature in deg C
#   TOXIC_CONC                     -> dose limit in mg/mL
#
# Return exactly one of: "TOXIC", "TOO_COLD", "THERAPEUTIC", "TOO_HOT"
# Therapeutic window is 42 to 45 deg C (inclusive). Check toxicity FIRST.

def check_therapy(conc, field):
    temp = body_temperature(conc, field)
    # TODO: use if / elif / else
    return "?"

print(check_therapy(2, 15))
'''

L3_SOLUTION = '''\
def check_therapy(conc, field):
    if conc > TOXIC_CONC:
        return "TOXIC"
    temp = body_temperature(conc, field)
    if temp < 42:
        return "TOO_COLD"
    elif temp <= 45:
        return "THERAPEUTIC"
    else:
        return "TOO_HOT"

print(check_therapy(2, 15))
'''

L3_CASES = [(2, 15), (1, 10), (3, 15), (5, 10), (4.5, 15),
            (1.5, 15), (2, 16), (3.5, 12), (4, 15)]


def check_l3(g):
    fn = g.get("check_therapy")
    if not callable(fn):
        return False, ["Define a function called `check_therapy(conc, field)`."]
    msgs = []
    for conc, field in L3_CASES:
        want = sc.reference_therapy(conc, field)
        got = fn(conc, field)
        if got != want:
            temp = sc.body_temperature(conc, field)
            msgs.append(f"conc={conc} mg/mL, field={field} mT: tissue reaches {temp:.1f} C. "
                        f"Expected {want!r} but your function returned {got!r}.")
            if want == "TOXIC":
                msgs.append("Hint: toxicity must be checked before temperature.")
            return False, msgs
    return True, ["All 9 test cases pass. Therapeutic dose found without harming "
                  "healthy tissue."]


# ---------------------------------------------------------------- Level 4
L4_STARTER = '''\
# Mission: show how drug release speeds up with nanoparticle concentration.
# Provided: np, plt (matplotlib), and release_fraction(t, conc)
# which returns the fraction of drug released (0 to 1) at time t (hours).

t = np.linspace(0, 24, 100)         # hours
concentrations = [0.5, 1, 2, 4]     # mg/mL

for c in concentrations:
    # TODO: compute release = release_fraction(t, c)
    #       then plt.plot(t, release, label=...)
    pass

# TODO: add axis labels (plt.xlabel, plt.ylabel) and a legend (plt.legend)
'''

L4_SOLUTION = '''\
t = np.linspace(0, 24, 100)
concentrations = [0.5, 1, 2, 4]

for c in concentrations:
    release = release_fraction(t, c)
    plt.plot(t, release, label=f"{c} mg/mL")

plt.xlabel("Time (h)")
plt.ylabel("Drug released (fraction)")
plt.legend()
'''


def check_l4(g):
    import numpy as np
    plt = g["plt"]
    if not plt.get_fignums():
        return False, ["No plot found. Call `plt.plot(...)` inside the loop."]
    ax = plt.gcf().axes[0]
    lines = ax.get_lines()
    msgs = []
    if len(lines) < 3:
        msgs.append(f"Plot at least 3 concentrations (found {len(lines)} curve(s)).")
    if not ax.get_xlabel().strip() or not ax.get_ylabel().strip():
        msgs.append("Add axis labels with `plt.xlabel(...)` and `plt.ylabel(...)`.")
    if ax.get_legend() is None:
        msgs.append("Add a legend (give each curve a `label=` and call `plt.legend()`).")
    ys = [np.asarray(l.get_ydata(), dtype=float) for l in lines]
    if any(len(y) and (y.min() < -1e-9 or y.max() > 1 + 1e-9) for y in ys):
        msgs.append("Release should stay between 0 and 1. Use `release_fraction(t, c)`.")
    if len(ys) >= 2 and all(len(y) == len(ys[0]) for y in ys):
        spread = max(float(np.max(np.abs(a - b))) for a in ys for b in ys)
        if spread < 0.01:
            msgs.append("All curves are identical. Use the loop variable `c` in "
                        "`release_fraction(t, c)`.")
    if msgs:
        return False, msgs
    return True, ["Higher concentration means faster release. This is how you tune "
                  "the dose schedule so the drug arrives at the tumor on time."]


# ---------------------------------------------------------------- Boss
BOSS_STARTER = '''\
# BOSS: targeted delivery simulation. 4 bugs are hiding in this script.
# The magnet should steer ONE nanoparticle to the tumor and release the drug
# there, and only there. Find and fix the bugs to cure the patient!

tumor_x, tumor_y = 7, 3     # tumor location on the tissue grid
x, y = 0, 0                 # injection site
max_steps = 5               # the magnet stays on for 20 steps
off_target_hits = 0         # drug released on healthy tissue (must be 0)
doses_released = 0          # total releases (must be exactly 1)
steps_taken = 0
delivered = False

for step in range(max_steps):
    steps_taken += 1

    # steer the particle toward the tumor
    if x < tumor_x:
        x += 1
    elif x > tumor_x:
        x -= 1
    if y < tumor_y:
        y -= 1
    elif y > tumor_y:
        y -= 1

    # release the drug when the particle is on the tumor
    if x == tumor_x or y == tumor_y:
        doses_released += 1
        if x == tumor_x and y == tumor_y:
            delivered = True
        else:
            off_target_hits += 1

print("Position:", (x, y), "| delivered:", delivered,
      "| off-target hits:", off_target_hits, "| doses:", doses_released)
'''

BOSS_SOLUTION = BOSS_STARTER \
    .replace("max_steps = 5 ", "max_steps = 20") \
    .replace("    if y < tumor_y:\n        y -= 1", "    if y < tumor_y:\n        y += 1") \
    .replace("if x == tumor_x or y == tumor_y:", "if x == tumor_x and y == tumor_y:") \
    .replace("            off_target_hits += 1\n",
             "            off_target_hits += 1\n        break\n")


def check_boss(g):
    msgs = []
    pos = (g.get("x"), g.get("y"))
    if (g.get("tumor_x"), g.get("tumor_y")) != (7, 3):
        return False, ["Don't move the tumor! Fix the simulation, not the target."]
    if g.get("off_target_hits", 1) > 0:
        msgs.append(f"Off-target damage: drug was released on healthy tissue "
                    f"{g.get('off_target_hits')} time(s). Check the release condition.")
    if g.get("doses_released", 0) > 1:
        msgs.append(f"Overdose: {g.get('doses_released')} doses released. "
                    "The simulation should stop once the drug is delivered.")
    if not g.get("delivered"):
        if _num(pos[1]) and pos[1] < 0:
            msgs.append(f"The particle drifted off to y={pos[1]}. Check the y-axis steering.")
        elif pos != (7, 3):
            msgs.append(f"The particle ended at {pos}, not (7, 3). Does it get enough "
                        "time to arrive?")
        else:
            msgs.append("The particle never released the drug on the tumor.")
    if not msgs and g.get("steps_taken") != 7:
        msgs.append(f"Delivery should take exactly 7 steps (took {g.get('steps_taken')}).")
    if msgs:
        return False, msgs
    return True, ["Drug delivered to the tumor in 7 steps with zero off-target damage. "
                  "Patient cured!"]


# ---------------------------------------------------------------- registry
def _env_l1():
    return {"math": math}


def _env_l2():
    return {"math": math, "stability_index": sc.stability_index}


def _env_l3():
    return {"math": math, "body_temperature": sc.body_temperature,
            "TOXIC_CONC": sc.TOXIC_CONC}


def _env_l4():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    plt.close("all")
    return {"math": math, "np": np, "plt": plt,
            "release_fraction": sc.release_fraction}


def _env_boss():
    return {}


@dataclass
class Level:
    id: str
    short: str
    title: str
    skill: str
    story: str
    science: str
    starter: str
    solution: str
    hints: list
    make_env: Callable
    check: Callable
    xp: int = 100
    formula: str = ""
    wants_figure: bool = False


LEVELS = [
    Level(
        id="L1", short="Level 1: Activate the fluid", title="Activate the Base Fluid",
        skill="Python skills: variables and arithmetic",
        story="You are a nano-engineer. Your patient has a tumor that is hard to reach. "
              "Your plan: a magnetic nanofluid, water carrying Fe3O4 nanoparticles that "
              "you can steer with a magnet and heat with an alternating field. First, "
              "work out how much of the mixture is nanoparticles and how well it "
              "conducts heat.",
        science="Adding highly conductive nanoparticles to water raises its thermal "
                "conductivity. The **Maxwell model** estimates the effective value from "
                "the particle volume fraction φ. This is the same mixing-rule idea used "
                "for composites in MSE.",
        formula=r"\phi=\frac{V_p}{V_p+V_f}\qquad "
                r"k_{eff}=k_f\,\frac{k_p+2k_f+2\phi(k_p-k_f)}{k_p+2k_f-\phi(k_p-k_f)}",
        starter=L1_STARTER, solution=L1_SOLUTION,
        hints=["φ is the particle volume divided by the TOTAL volume of the mixture.",
               "Write the Maxwell formula in two steps: compute `num` and `den`, "
               "then `k_eff = k_f * num / den`."],
        make_env=_env_l1, check=check_l1, xp=100),
    Level(
        id="L2", short="Level 2: Keep it stable", title="Keep the Fluid Stable",
        skill="Python skills: for loops, if statements, lists",
        story="Your fluid is active, but if the nanoparticles clump together "
              "(agglomerate) they will block blood vessels. Sweep through candidate "
              "particle sizes and find which ones stay dispersed.",
        science="**Colloidal stability:** large magnetic particles attract each other "
                "and settle out, while very small ones barely respond to the magnet. "
                "Real stability comes from DLVO theory, where van der Waals and magnetic "
                "attraction compete with electrostatic and steric repulsion. Here a "
                "simplified `stability_index(d)` captures the trade-off.",
        starter=L2_STARTER, solution=L2_SOLUTION,
        hints=["Loop over `range(5, 61, 5)` and test each `d` with an `if`.",
               "`if stability_index(d) >= 1:` then `stable_sizes.append(d)`."],
        make_env=_env_l2, check=check_l2, xp=150),
    Level(
        id="L3", short="Level 3: Dose the patient", title="Heat the Tumor, Spare the Patient",
        skill="Python skills: functions, return values, conditionals",
        story="Time to treat. Alternating magnetic fields make the nanoparticles heat up "
              "(magnetic hyperthermia). Tumor cells die at 42 to 45 °C, but too much "
              "heat hurts healthy tissue, and too much iron oxide is toxic. Write the "
              "decision function the treatment planner will use.",
        science="**Magnetic hyperthermia** needs tissue at about 42 to 45 °C. Below that "
                "the treatment is ineffective, above it healthy cells are damaged. The "
                "dose must also stay under a toxicity limit. Values here are simplified "
                "for learning; real limits come from nanomedicine literature.",
        starter=L3_STARTER, solution=L3_SOLUTION,
        hints=["Check toxicity first: `if conc > TOXIC_CONC: return \"TOXIC\"`.",
               "Then compare `temp` against 42 and 45 with `elif`."],
        make_env=_env_l3, check=check_l3, xp=200),
    Level(
        id="L4", short="Level 4: Plot the release", title="Plot the Drug Release",
        skill="Python skills: loops + matplotlib plotting",
        story="The doctors need to know how fast the drug leaves the carriers at "
              "different nanoparticle concentrations. Plot the release curves so the "
              "dosing schedule can be chosen.",
        science="Drug release from nanocarriers is often modeled as **first-order "
                "kinetics**: released fraction = 1 − e^(−kt). A higher particle "
                "concentration gives a larger rate constant k, so the drug is released "
                "sooner.",
        formula=r"R(t)=1-e^{-kt}",
        starter=L4_STARTER, solution=L4_SOLUTION,
        hints=["Inside the loop: `release = release_fraction(t, c)`.",
               "Then `plt.plot(t, release, label=f\"{c} mg/mL\")`. After the loop add "
               "`plt.xlabel`, `plt.ylabel`, `plt.legend()`."],
        make_env=_env_l4, check=check_l4, wants_figure=True, xp=200),
    Level(
        id="BOSS", short="BOSS: Escape the lab", title="Boss: Debug the Delivery Simulation",
        skill="Python skills: debugging loops and conditionals",
        story="Alarm! The targeted-delivery simulation is broken. The particle wanders "
              "off, the drug lands on healthy tissue, and the patient is getting "
              "overdosed. Four bugs are hiding in the script. Fix them to deliver the "
              "drug to the tumor at (7, 3) and cure the patient.",
        science="Targeted delivery uses an external magnet to guide particles to the "
                "tumor. Off-target release causes side effects, and repeat doses cause "
                "toxicity. Debugging a simulation is how engineers validate a design "
                "before it ever reaches a patient.",
        starter=BOSS_STARTER, solution=BOSS_SOLUTION,
        hints=["Run it and read the printed output. Where does the particle end up? "
               "Look at the y-axis steering first.",
               "Four bugs: the number of steps, the sign of a y move, `or` vs `and`, "
               "and a missing `break` once the drug is delivered."],
        make_env=_env_boss, check=check_boss, xp=300),
]

LEVELS_BY_ID = {lv.id: lv for lv in LEVELS}
