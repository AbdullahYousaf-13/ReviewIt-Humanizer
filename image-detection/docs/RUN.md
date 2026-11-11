# Image detector: how to run it

Install (once):

```
cd ReviewIt\backend
venv\Scripts\activate
pip install -r imagedetector\requirements-bombek1.txt
```

Start the backend (PowerShell):

```
cd ReviewIt\backend
venv\Scripts\activate
$env:IMAGE_PRELOAD="1"
python app.py
```

Check an image (after `http://127.0.0.1:5000/api/imagedetector/status` says `ready`):

```
curl -X POST -F "file=@photo.jpg" http://127.0.0.1:5000/api/imagedetector/detect
```

Or check a folder of photos (put them in `backend\imagedetector\inbox\` first):

```
python -m imagedetector.check_folder
```
