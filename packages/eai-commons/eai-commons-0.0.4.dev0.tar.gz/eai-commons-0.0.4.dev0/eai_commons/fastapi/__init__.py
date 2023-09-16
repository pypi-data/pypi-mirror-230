try:
    import fastapi
except ImportError:
    raise ImportError(
        "Could not import fastapi python package. "
        "This is needed in order to for ExceptionHandler. "
        "Please install it with `pip install fastapi`."
    )
