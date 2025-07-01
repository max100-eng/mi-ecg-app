## Running the Project with Docker

This project provides a Docker-based setup for running a Streamlit ECG analysis application. The Docker configuration builds both the Python backend (Streamlit app) and includes a JavaScript frontend file (`App.js`).

### Project-Specific Docker Requirements
- **Python version:** 3.11 (as specified in the Dockerfile)
- **Node.js version:** 20 (for frontend build, though only `App.js` is present and no build steps are run)
- **Python dependencies:**
  - `streamlit`
  - `neurokit2`
  - `matplotlib`
  - `pandas`
  - `numpy`
- **System dependencies:**
  - `build-essential`, `python3-dev`, `libglib2.0-0`, `libsm6`, `libxrender1`, `libxext6`

### Environment Variables
- No required environment variables are specified in the Dockerfile or `docker-compose.yml`.
- If you need to add environment variables, you can uncomment and use the `env_file: ./.env` line in the compose file.

### Build and Run Instructions
1. **Build and start the service:**
   ```sh
   docker compose up --build
   ```
   This will build the image and start the Streamlit app in a container named `python-ecg_app`.

2. **Access the application:**
   - Open your browser and go to [http://localhost:8501](http://localhost:8501)

### Ports
- **Streamlit app:** Exposed on port `8501` (mapped to host `8501`)

### Special Configuration
- No external services (databases, caches) are required or configured.
- No persistent volumes are needed for this project.
- The default command runs the Streamlit app (`ecg_app.py`). If you wish to run a different Python file, modify the `CMD` in the Dockerfile or override it in the compose file.

---

*This section was updated to reflect the current Docker-based setup for this project. If you add new dependencies or services, update this section accordingly.*
