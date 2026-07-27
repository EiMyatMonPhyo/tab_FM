from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routers.predict import router as predict_router
from app.routers.fit import router as fit_router
from app.routers.predict_proba import router as predict_proba_router

app = FastAPI(title="tabFM API")

app.include_router(fit_router)
app.include_router(predict_router)
app.include_router(predict_proba_router)

@app.get("/")
async def root():
    return {"message": "Welcome to tabFM!"}

@app.get("/client", response_class=HTMLResponse)
async def serve_client_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TabFM Model Predictor</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
            .card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; }
            button { background: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; }
            #status { margin-top: 15px; font-weight: bold; }
            pre { background: #f4f4f4; padding: 10px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>TabFM Prediction Client</h2>
            <form id="uploadForm">
                <p><label>User ID: <input type="text" id="userId" value="user_123" required></label></p>
                <p><label>CSV File: <input type="file" id="csvFile" accept=".csv" required></label></p>
                <button type="submit">Start Prediction</button>
            </form>

            <div id="status"></div>
            <pre id="output"></pre>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async (e) => {
                e.preventDefault();

                const userId = document.getElementById('userId').value;
                const fileInput = document.getElementById('csvFile');
                const statusDiv = document.getElementById('status');
                const outputPre = document.getElementById('output');

                const formData = new FormData();
                formData.append('user_id', userId);
                formData.append('file', fileInput.files[0]);

                statusDiv.innerText = "Starting prediction task...";
                outputPre.innerText = "";

                try {
                    // Step 1: Call /predict/ (Returns immediately with task_id)
                    const startRes = await fetch('/predict/', {
                        method: 'POST',
                        body: formData
                    });
                    const startData = await startRes.json();

                    if (!startRes.ok) throw new Error(startData.detail || "Failed to start");

                    const taskId = startData.task_id;
                    statusDiv.innerText = `Task started (ID: ${taskId}). Polling status...`;

                    // Step 2: Poll /predict/status/{task_id} every 5 seconds inside the browser
                    const pollInterval = setInterval(async () => {
                        const statusRes = await fetch(`/predict/status/${taskId}`);
                        const statusData = await statusRes.json();

                        if (statusData.status === 'completed') {
                            clearInterval(pollInterval);
                            statusDiv.innerText = "Status: Completed!";
                            outputPre.innerText = JSON.stringify(statusData.result, null, 2);
                        } else if (statusData.status === 'failed') {
                            clearInterval(pollInterval);
                            statusDiv.innerText = "Status: Failed!";
                            outputPre.innerText = JSON.stringify(statusData, null, 2);
                        } else {
                            statusDiv.innerText = `Status: ${statusData.status}... (${statusData.message || ''})`;
                        }
                    }, 5000);

                } catch (err) {
                    statusDiv.innerText = "Error: " + err.message;
                }
            });
        </script>
    </body>
    </html>
    """
