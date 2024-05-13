from fastapi import Depends, FastAPI, Request

def get_db(request: Request):
    return request.app.state.db