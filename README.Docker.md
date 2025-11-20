# Global Chemical Space Viewer

A Dockerized Streamlit application for exploring chemical-space data.

---

## Running the Application

### 1. Install Docker (if you haven't)
Download Docker from:  
https://docs.docker.com/get-docker/

### 2. Clone the repo
```
git clone https://github.com/BoCHemia/global-chemical-space.git
cd global-chemical-space
```

### 2. Download the data & models

Download data & models from our repo ()
Save them in seperate folders in the same level (but outside) the cloned repo
Example:
Parent Folder
    - global-chemical-space   -> This is the repo
    - global-chemical-space-data
    - global-chemical-space-models

### 3. Build the Docker to run the app

```
docker build -t global-chemical-space-app .
```

The application will be available at:
http://localhost:8501
