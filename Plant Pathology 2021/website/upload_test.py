import requests, os, traceback

BASE = os.path.dirname(os.path.abspath(__file__))
url = 'http://127.0.0.1:5000/predict'
img = os.path.join(BASE, 'static', 'examples', 'severity', '03483_frog_eye_leaf_spot_jpg.rf.6272315a73b73eeafaf25da62ae6b34b_overlay.jpg')
print('image exists:', os.path.exists(img))
try:
    with open(img, 'rb') as f:
        files = {'file': f}
        data = {'task': 'severity', 'pad': '10', 'multi_leaf': 'on'}
        print('posting to', url)
        r = requests.post(url, files=files, data=data, timeout=120)
        print('status', r.status_code)
        print('response length', len(r.text))
        open(os.path.join(BASE, 'last_response.html'), 'w', encoding='utf8').write(r.text)
        print('wrote last_response.html')
except Exception:
    traceback.print_exc()

print('\n-- uploads folder --')
up = os.path.join(BASE, 'uploads')
if os.path.exists(up):
    print('\n'.join(sorted(os.listdir(up))))
else:
    print('uploads folder not found')

print('\n-- results_predict folder --')
res = os.path.join(BASE, 'results_predict')
if os.path.exists(res):
    print('\n'.join(sorted(os.listdir(res))))
else:
    print('results_predict folder not found')
