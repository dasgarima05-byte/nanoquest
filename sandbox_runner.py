"""Child process that runs the player's code. Called by sandbox.py.
Classroom-grade guard, not a hardened security sandbox."""
import base64
import builtins
import contextlib
import io
import json
import os
import sys
import traceback

os.environ["MPLBACKEND"] = "Agg"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
except Exception:
    pass  # e.g. on Windows

SAFE_NAMES = [
    "abs", "all", "any", "bool", "dict", "divmod", "enumerate", "filter", "float",
    "int", "isinstance", "len", "list", "map", "max", "min", "pow", "print", "range",
    "reversed", "round", "set", "sorted", "str", "sum", "tuple", "zip",
    "Exception", "ValueError", "TypeError", "ZeroDivisionError", "IndexError",
    "KeyError", "NameError", "StopIteration",
]


def _blocked_import(*args, **kwargs):
    raise ImportError("Imports are disabled in NanoQuest. math, np and plt are "
                      "already loaded for you where needed.")


def make_builtins():
    b = {n: getattr(builtins, n) for n in SAFE_NAMES}
    b["__import__"] = _blocked_import
    return b


def describe_error(e):
    if isinstance(e, SyntaxError):
        return f"SyntaxError (line {e.lineno}): {e.msg}"
    tb = traceback.extract_tb(e.__traceback__)
    line = next((f.lineno for f in reversed(tb) if f.filename == "<your code>"), None)
    where = f" (line {line})" if line else ""
    return f"{type(e).__name__}{where}: {e}"


def main():
    payload = json.loads(sys.stdin.read())
    from levels import LEVELS_BY_ID
    level = LEVELS_BY_ID[payload["level"]]

    g = {"__builtins__": make_builtins(), "__name__": "__player__"}
    g.update(level.make_env())

    result = {"passed": False, "messages": [], "stdout": "", "error": None, "figure": None}
    out = io.StringIO()
    ran_ok = False

    with contextlib.redirect_stdout(out):
        try:
            exec(compile(payload["code"], "<your code>", "exec"), g)
            ran_ok = True
        except BaseException as e:
            result["error"] = describe_error(e)
        if ran_ok:
            try:
                result["passed"], result["messages"] = level.check(g)
            except BaseException as e:
                result["messages"] = ["Your code ran, but the checker hit an error: "
                                      + describe_error(e)]

    result["stdout"] = out.getvalue()[:3000]

    if level.wants_figure:
        try:
            import matplotlib.pyplot as plt
            if plt.get_fignums():
                buf = io.BytesIO()
                plt.gcf().savefig(buf, format="png", dpi=110, bbox_inches="tight")
                result["figure"] = base64.b64encode(buf.getvalue()).decode()
        except Exception:
            pass

    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
