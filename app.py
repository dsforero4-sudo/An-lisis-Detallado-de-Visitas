FileNotFoundError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/an-lisis-detallado-de-visitas/app.py", line 16, in <module>
    df_frec = cargar_analisis_pareto()
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/caching/cache_utils.py", line 590, in __call__
    return self._get_or_create_cached_value(args, kwargs, spinner_message)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/caching/cache_utils.py", line 646, in _get_or_create_cached_value
    return self._handle_cache_miss(cache, value_key, func_args, func_kwargs)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
File "/home/adminuser/venv/lib/python3.14/site-packages/streamlit/runtime/caching/cache_utils.py", line 708, in _handle_cache_miss
    computed_value = self._info.func(*func_args, **func_kwargs)
File "/mount/src/an-lisis-detallado-de-visitas/app.py", line 7, in cargar_analisis_pareto
    df = pd.read_excel('Indicador_frecuencia_medicos.xlsx', sheet_name='Indicador_frecuencia_medico')
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/excel/_base.py", line 481, in read_excel
    io = ExcelFile(
        io,
    ...<2 lines>...
        engine_kwargs=engine_kwargs,
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/excel/_base.py", line 1604, in __init__
    ext = inspect_excel_format(
        content_or_path=path_or_buffer, storage_options=storage_options
    )
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/excel/_base.py", line 1452, in inspect_excel_format
    with get_handle(
         ~~~~~~~~~~^
        content_or_path, "rb", storage_options=storage_options, is_text=False
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ) as handle:
    ^
File "/home/adminuser/venv/lib/python3.14/site-packages/pandas/io/common.py", line 939, in get_handle
    handle = open(handle, ioargs.mode)
