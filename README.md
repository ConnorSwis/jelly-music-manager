run `uvicorn main:app` and the server will start on port 8000

endpoint:

- `GET /` -> web interface
- `GET /query/?url={url}` -> get album info
- `POST /download/?url={url}` -> download album
