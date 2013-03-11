from aggrerate import app

if __name__ == '__main__':
    try:
        from local_config import run_params
    except ImportError:
        run_params = {}
    app.run(**run_params)
