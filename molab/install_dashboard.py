# Run inside the MoLab notebook via `marimo pair execute` to (re)create the live dashboard cells.
import marimo._code_mode as cm
CELLS = [
 ("import marimo as mo, sys, importlib\nsys.path.insert(0, '/tmp/paperlm')\nimport dash_lib\nrefresh = mo.ui.refresh(options=['2s','3s','5s','10s'], default_interval='3s', label='🔄 live refresh')\nrefresh", "pl_refresh"),
 ("refresh.value\nimportlib.reload(dash_lib)\ndash_lib.header()", "pl_header"),
 ("refresh.value\ndash_lib.training()", "pl_training"),
 ("refresh.value\ndash_lib.samples()", "pl_samples"),
 ("refresh.value\nmo.vstack([dash_lib.dataset(), dash_lib.eval_card()])", "pl_dataset"),
]
async with cm.get_context() as ctx:
    for src, name in CELLS:
        cid = ctx.create_cell(src)
        ctx.run_cell(cid)
print("dashboard cells installed")
