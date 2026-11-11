import marimo._code_mode as cm
HEAD = "refresh.value\nimport importlib as _il, sys as _sys\n_sys.path.insert(0, '/tmp/paperlm')\nimport dash_judge as _dj\n_il.reload(_dj)\n"
CELLS = [HEAD + "_dj.judge()", HEAD + "_dj.gen()"]
async with cm.get_context() as ctx:
    for src in CELLS:
        cid = ctx.create_cell(src); ctx.run_cell(cid)
print("judge dashboard cells installed")
