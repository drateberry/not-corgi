# Not Corgi

**Video demo:** [Watch on YouTube](https://youtu.be/wJDeKZGFFsM)

---

## 1. What this is

"Not Corgi" is an homage to Jian-Yang's "Not Hotdog." It is a three-class image classifier to identify Cardigan Welsh Corgi, Pembroke Welsh Corgi, or Not Corgi based on an image uploaded to a local Flask API either through a direct POST request or via the React Native app.

While the classification of corgi vs not corgi is relatively trivial, the identification of Cardigan vs Pembroke is quite hard. Lacking known objects for scale, Cardigan only coat colors, and clear ear images, it is very difficult to classify the two breeds based on a single photo.

## 2. Repository layout

| Path        | What it is                                       |
|-------------|--------------------------------------------------|
| `model/`    | Dataset assembly, training, evaluation, Grad-CAM |
| `api/`      | Flask service — `/health` and `/predict`         |
| `mobile/`   | Expo / React Native client                       |
| `DESIGN.md` | The technical writeup (why, not how-to-run)      |

## 3. Prerequisites

- Python 3.10+ (developed on 3.10.16)
- Node + npm for the Expo client.
- **Expo SDK 54 and Expo Go 54.0.7 on the phone.** This matches the version of Expo SDK supported by the Expo Go app available at the time of development
- A **physical phone**. The camera and the shared-network conditions this app is built for do not exist in a simulator.
- Laptop and phone must be on the same network (the app talks to a LAN address).
- No GPU required — inference is CPU-only by design.

## 4. Downloads: trained model and dataset

Neither the weights nor the images are in the Github Repo. Both are
gitignored and both blow the ~15 MB ZIP budget.

Local-only execution was chosen for reproducibility, so a user can download the source images to tweak train.py, review training classifications, or modify the contents of the training data.

### 4.1 Trained model — required to run anything

**Download:** [`not_corgi.keras` (27.5 MB)](https://drive.google.com/file/d/1IHftrD2xFVHyGTxtnzsrUewggr5vZdBE/view?usp=sharing)

The downloaded keras model file should be placed at `api/artifacts/` but it is possible to place the file anywhere and update the location in `api/.env`. 

If not placed in the api directory, it is best to specify an absolute path.

### 4.2 Raw dataset — only needed to retrain

**Download:** [raw data](https://drive.google.com/drive/folders/1rVGHxy8xXxLmijSaBLVwBTr6PgAslOyZ?usp=sharing)

Not needed to run the app. This is the unsplit source data, useful only to review the training data and run additional training runs of the model.

The raw dataset should be placed at `model/data/raw` so the layout is:
`model/data/raw/Cardigan`
`model/data/raw/Not_Corgi`
`model/data/raw/Pembroke`

The raw data is grouped as follows:
| Class     | Image Count |
|-----------|-------------|
| Cardigan  | 154         |
| Not_Corgi | 436         |
| Pembroke  | 181         |

Then run `python prepare_data.py` from the `model/src` directory. This performs the near-duplicate check, splits the data, writes to `model/data/processed/` and records the result in splits.json.

## 5. Running the API

1. venv + `pip install -r api/requirements.txt` 
2. `cp api/.env.example api/.env` `MODEL_PATH` points at the model from 4.1; `PORT` defaults to 5001 and can be changed; `HOST` defaults to `0.0.0.0` and should be left alone. Flask's own default is `127.0.0.1` which accepts connections only from the computer itself, cutting the Expo Go app off from the API.
3. Start the API: `python api/app.py`
4. Find your computer's LAN address with `ipconfig getifaddr en0` on macOS. Open `http://<your-LAN-address>:5001/health` in the phone's browser. A JSON response with `"model_loaded": true` confirms that the phone can reach the API and the model is loaded. Do this before anything else to isolate network problems from app problems. 

### API reference

- `GET /health` → status, whether the model loaded, class names.
- `POST /predict` → multipart form field named **`image`**; returns per-class probabilities and a Grad-CAM overlay.
- Error codes as implemented: `no_file` / `bad_image` / `bad_request` (400), `too_large` (413, 10 MB cap), `server_error` (500).

The API can be used from the Terminal like:
`curl -X POST -F "image=@some-corgi.jpg" http://localhost:5001/predict`

The response contains `predicted_class`, `confidence`, a `probabilities` object with all three classes, `is_corgi` boolean, and `gradcam` as a base64-encoded PNG of the heatmap overlay.

## 6. Running the mobile app

1. `npm install` in `mobile/`
2. `cp mobile/.env.example mobile/.env` and set `EXPO_PUBLIC_API_URL` to `http://<your-LAN-address>:5001` using the address you found in step 5. This will change with every network you join. The fallback in `src/constants.js` is `http://localhost:5001` which works on a computer, but never from a phone
3. `npm start` then scan the QR code to launch the app in Expo Go. The computer and phone must be on the same network.
4. Capture a photo or pick one from the phone's library. The result screen shows the classification verdict, three class probabilities, and a toggle to view the Grad-CAM heatmap
5. Requests time out after 15 seconds. A timeout likely means the wrong IP address is set in `.env`, a firewall blocking the inbound connections to Flask, or that the devices are on different networks. Check `http://<your-LAN-address>:5001/health` from the phone's browser to verify connection.

## 7. Results

| Metric              | Value           |
|---------------------|-----------------|
| Overall             | 0.913 (105/115) |
| Corgi vs. not-corgi | 0.974 (112/115) |
| Breed given corgi   | 0.840 (42/50)   |

Full per-class precision and recall, the confusion matrix, and the error analysis are in `DESIGN.md` sections 5 and 6. Fractions are given alongside percentages because on the limited image set, a single image is worth two percentage points.

## 8. Known limitations

- **Cardigan recall is 0.652** — the weakest class by a wide margin, and every test-set Cardigan error went to Pembroke. Expect Cardigans to get called Pembrokes.
- **Several errors are confidently wrong** (0.96–0.99). A confidence threshold cannot filter these, so the UI does not promise one.
- **235 corgi training images total.** Published fine-grained work uses thousands per class.
- **Dataset label noise** on exactly the Pembroke/Cardigan boundary, at least one confirmed. So the reported breed number is arguably a floor.