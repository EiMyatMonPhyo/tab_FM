# TabFM FastAPI Service

This project provides a FastAPI service for training and inference using TabFM models.

---

# Project Setup

## 1. Clone the repository

```bash
git clone <repository-url>
cd tabFM
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start MongoDB

This project stores model metadata in MongoDB.

If you do not already have a MongoDB instance running, start one with Docker:

```bash
docker run -d \
  --name tabfm-mongodb \
  -p 27018:27017 \
  mongo
```

The application is configured to connect to:

```
mongodb://localhost:27018
```

You can inspect the database using MongoDB Compass:

```
mongodb://localhost:27018
```

---

## 5. Run the FastAPI server

From the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```
http://127.0.0.1:8000
```

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

# API Endpoints

| Endpoint               | Description                              |
| ---------------------- | ---------------------------------------- |
| POST `/fit/`           | Train a TabFM model                      |
| POST `/predict/`       | Predict using a previously trained model |
| POST `/predict_proba/` | Return prediction probabilities          |

---

# Input File Naming Convention

The training and prediction files **must** follow the naming convention below.

## Training

```
<dataset_name>_train.csv
```

Example:

```
water_network_train.csv
```

## Prediction

```
<dataset_name>_test.csv
```

Example:

```
water_network_test.csv
```

The API automatically removes the `_train` or `_test` suffix when generating the model ID so that both files map to the same trained model.

Example:

```
water_network_train.csv
water_network_test.csv
```

Both generate the same model ID:

```
<user_id>_water_network
```

---

# Model Storage

After a successful `/fit` request:

* The trained TabFM model is saved under:

```
saved_models/
```

Example:

```
saved_models/
└── user123_water_network.joblib
```

* Model metadata is stored in MongoDB.

Example document:

```json
{
  "model_id": "user123_water_network",
  "user_id": "user123",
  "filename": "water_network_train.csv",
  "model_path": "saved_models/user123_water_network.joblib",
  "task_type": "classification"
}
```

During `/predict` and `/predict_proba`, the service:

1. Generates the same model ID from the uploaded filename and user ID.
2. Retrieves the model metadata from MongoDB.
3. Loads the saved model.
4. Performs inference.

---

