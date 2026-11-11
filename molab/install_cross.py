import marimo._code_mode as cm
HEAD = "refresh.value\nimport importlib as _il, sys as _sys\n_sys.path.insert(0, '/tmp/paperlm')\nimport dash_judge as _dj\n_il.reload(_dj)\n"
async with cm.get_context() as ctx:
    cid = ctx.create_cell(HEAD + "_dj.cross()"); ctx.run_cell(cid)
print("cross card installed")
