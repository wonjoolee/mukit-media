# 사용: python3 pipeline/to_jpg.py <폴더>  — NN.png → NN.jpg 변환 후 png 삭제 + 미리보기 /tmp/mukit_preview/<날짜>_<슬롯>.jpg
import sys, glob, os
from PIL import Image
d = sys.argv[1]
fs = sorted(glob.glob(os.path.join(d, '[0-9][0-9].png')))
ims = []
for f in fs:
    im = Image.open(f).convert('RGB'); im.save(f[:-4] + '.jpg', quality=92); os.remove(f); ims.append(im)
w, h = 432, 540
s = Image.new('RGB', (20 + (w + 20) * len(ims), h + 40), '#cccccc')
for i, im in enumerate(ims):
    s.paste(im.resize((w, h), Image.LANCZOS), (20 + i * (w + 20), 20))
os.makedirs('/tmp/mukit_preview', exist_ok=True)
p = f'/tmp/mukit_preview/{os.path.basename(os.path.dirname(os.path.abspath(d)))}_{os.path.basename(os.path.abspath(d))}.jpg'
s.save(p, quality=85)
print('ok', len(ims), p)
