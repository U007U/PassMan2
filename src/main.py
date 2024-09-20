import uvicorn

from worker.requestListener import app

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=5555, log_level="info")
