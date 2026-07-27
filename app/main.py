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
        <title>TabFM Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 30px auto; padding: 20px; background-color: #f8f9fa; }
            h1 { text-align: center; color: #333; }
            .card { background: white; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
            .card h2 { margin-top: 0; color: #007bff; border-bottom: 2px solid #e9ecef; padding-bottom: 8px; }
            label { display: block; margin-top: 10px; font-weight: bold; }
            input, select { margin-top: 5px; width: 100%; padding: 8px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }
            button { background: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; font-weight: bold; width: 100%; }
            button:hover { background: #0056b3; }
            .status { margin-top: 15px; font-weight: bold; color: #555; }
            pre { background: #272822; color: #f8f8f2; padding: 12px; border-radius: 4px; overflow-x: auto; max-height: 250px; font-size: 13px; }
        </style>
    </head>
    <body>
        <h1>TabFM Interactive Client</h1>

        <!-- 1. FIT CARD -->
        <div class="card">
            <h2>1. Fit / Train Model (/fit/)</h2>
            <form id="fitForm">
                <label>User ID: <input type="text" id="fitUserId" value="user_123" required></label>
                <label>Task Type: 
                    <select id="fitTaskType" required>
                        <option value="classification">Classification</option>
                        <option value="regression">Regression</option>
                    </select>
                </label>
                <label>Training CSV File (Target column must be last): <input type="file" id="fitCsvFile" accept=".csv" required></label>
                <button type="submit">Start Training</button>
            </form>
            <div id="fitStatus" class="status"></div>
            <pre id="fitOutput"></pre>
        </div>

        <!-- 2. PREDICT CARD -->
        <div class="card">
            <h2>2. Predict (/predict/)</h2>
            <form id="predictForm">
                <label>User ID: <input type="text" id="predictUserId" value="user_123" required></label>
                <label>CSV File: <input type="file" id="predictCsvFile" accept=".csv" required></label>
                <button type="submit">Start Prediction</button>
            </form>
            <div id="predictStatus" class="status"></div>
            <pre id="predictOutput"></pre>
        </div>

        <!-- 3. PREDICT PROBA CARD -->
        <div class="card">
            <h2>3. Predict Proba (/predict/proba)</h2>
            <form id="probaForm">
                <label>User ID: <input type="text" id="probaUserId" value="user_123" required></label>
                <label>CSV File (Classification only): <input type="file" id="probaCsvFile" accept=".csv" required></label>
                <button type="submit">Start Predict Proba</button>
            </form>
            <div id="probaStatus" class="status"></div>
            <pre id="probaOutput"></pre>
        </div>

        <script>
            // Helper function to handle async task polling
            async function handleTaskSubmission({ endpoint, formData, statusDiv, outputPre, statusEndpoint = '/predict/status/' }) {
                statusDiv.innerText = "Submitting task...";
                outputPre.innerText = "";

                try {
                    const startRes = await fetch(endpoint, {
                        method: 'POST',
                        body: formData
                    });
                    const startData = await startRes.json();

                    if (!startRes.ok) throw new Error(startData.detail || "Request failed");

                    const taskId = startData.task_id;
                    statusDiv.innerText = `Task started (ID: ${taskId}). Polling status...`;

                    const pollInterval = setInterval(async () => {
                        const statusRes = await fetch(`${statusEndpoint}${taskId}`);
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
            }

            // 1. Fit Handler
            document.getElementById('fitForm').addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData();
                formData.append('user_id', document.getElementById('fitUserId').value);
                formData.append('task_type', document.getElementById('fitTaskType').value);
                formData.append('file', document.getElementById('fitCsvFile').files[0]);

                handleTaskSubmission({
                    endpoint: '/fit/',
                    formData: formData,
                    statusDiv: document.getElementById('fitStatus'),
                    outputPre: document.getElementById('fitOutput'),
                    statusEndpoint: '/predict/status/'
                });
            });

            // 2. Predict Handler
            document.getElementById('predictForm').addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData();
                formData.append('user_id', document.getElementById('predictUserId').value);
                formData.append('file', document.getElementById('predictCsvFile').files[0]);

                handleTaskSubmission({
                    endpoint: '/predict/',
                    formData: formData,
                    statusDiv: document.getElementById('predictStatus'),
                    outputPre: document.getElementById('predictOutput'),
                    statusEndpoint: '/predict/status/'
                });
            });

            // 3. Predict Proba Handler
            document.getElementById('probaForm').addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData();
                formData.append('user_id', document.getElementById('probaUserId').value);
                formData.append('file', document.getElementById('probaCsvFile').files[0]);

                handleTaskSubmission({
                    endpoint: '/predict_proba/',
                    formData: formData,
                    statusDiv: document.getElementById('probaStatus'),
                    outputPre: document.getElementById('probaOutput'),
                    statusEndpoint: '/predict/status/'
                });
            });
        </script>
    </body>
    </html>
    """