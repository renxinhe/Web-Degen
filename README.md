# Web Degen
Webpage generation from images via deep learning.

Initalization
-------------
```bash
pip install -r requirements.txt
sqlite3 app.db < schema.sql
```

Requires Keras, opencv-python, h5py, tensorflow. Model files not provided due to size limitations, but can be trained using <https://github.com/tonybeltramelli/pix2code>. The location the model should then be changed in `app/models.py`

Yuxuan (Andrew) Liu, Xinhe (Jim) Ren, Sheng Tan, Yue (Andy) Zhang
