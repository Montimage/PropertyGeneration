# Chat UI (React + Vite)

Web frontend for the property generation system. It provides a chat interface to generate properties from natural-language prompts, save them, and send them to monitoring tools through the FastAPI backend (see [`../backend`](../backend)).

## Requirements

- Node.js 18+ and npm
- The FastAPI backend running and reachable (see the main [README](../README.md#backend-fastapi))

## Configuration

The frontend reads its settings from a `.env` file in the `chat-ui/` directory. Create it from the template below:

```bash
# chat-ui/.env

# URL (including port) of the FastAPI backend
VITE_API_BASE_URL=http://localhost:8000
```

| Variable | Description | Default (if unset) |
| --- | --- | --- |
| `VITE_API_BASE_URL` | Base URL of the backend API, including protocol, host and port. All requests (`/generate-property`, `/save-property`, `/send-to-monitoring`, `/pending-messages`) are sent to this address. | `http://localhost:8001` |

Notes:

- The value must match the host and port the backend is started on (e.g. `uvicorn main:app --port 8000`).
- Do not add a trailing slash to the URL.
- Vite only exposes variables prefixed with `VITE_` to the frontend, and reads them at startup/build time: restart `npm run dev` (or rebuild) after changing `.env`.
- The backend only allows CORS requests from `http://localhost:5173`. If you serve the frontend from another origin, update `allow_origins` in [`backend/main.py`](../backend/main.py).

The variable is consumed in [`src/config.js`](src/config.js).

## Running

```bash
cd chat-ui
npm install
npm run dev
```

The app is available at `http://localhost:5173`.

## Available scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Start the development server with hot reload |
| `npm run build` | Build the production bundle into `dist/` |
| `npm run preview` | Serve the production build locally |
| `npm run lint` | Run ESLint |
