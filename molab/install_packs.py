import marimo._code_mode as cm
HEAD = "import sys as _s, importlib as _il\n_s.path.insert(0, '/tmp/paperlm')\nimport dash_packs as _dp\n_il.reload(_dp)\n"
CELLS = ["import marimo as mo\nrefresh = mo.ui.refresh(default_interval='3s', label='live (3 s)')\nrefresh",
         HEAD + "refresh.value\n_dp.gpu()", HEAD + "refresh.value\n_dp.teacher()", HEAD + "refresh.value\n_dp.training()", HEAD + "refresh.value\n_dp.samples()"]
async with cm.get_context() as ctx:
    for src in CELLS:
        cid = ctx.create_cell(src); ctx.run_cell(cid)
print("pack dashboard installed")
