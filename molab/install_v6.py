# Run inside the MoLab notebook via `marimo pair execute` to add the v6 live cards.
import marimo._code_mode as cm

CELLS = [
    ("refresh.value\nimport importlib, sys\nsys.path.insert(0, '/tmp/paperlm')\nimport dash_v6\nimportlib.reload(dash_v6)\ndash_v6.verifier()", "pl_verifier"),
    ("refresh.value\nimportlib.reload(dash_v6)\ndash_v6.library()", "pl_library"),
    ("refresh.value\nimportlib.reload(dash_v6)\ndash_v6.audit()", "pl_audit"),
    ("refresh.value\nimportlib.reload(dash_v6)\ndash_v6.items()", "pl_items"),
    ("refresh.value\nimportlib.reload(dash_v6)\ndash_v6.system()", "pl_system"),
]
async with cm.get_context() as ctx:
    for src, name in CELLS:
        cid = ctx.create_cell(src)
        ctx.run_cell(cid)
print("v6 dashboard cells installed")
