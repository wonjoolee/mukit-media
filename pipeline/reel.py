# 사용: python3 pipeline/reel.py <카드 폴더(01.jpg..)> <out.mp4> [장당 초=2.6]
# 카드(1080x1350)를 세로 1080x1920 화면 가운데에 두고 천천히 확대 + 장면 전환, 끝에 MUKIT 로고 엔딩. 무음 트랙 포함.
import glob, os, subprocess, sys, tempfile
from PIL import Image
d, out = sys.argv[1], sys.argv[2]
D = float(sys.argv[3]) if len(sys.argv) > 3 else 2.6
X, END = 0.5, 2.2
INK, PAPER = '#151515', '#F2EFE8'
cards = sorted(glob.glob(os.path.join(d, '[0-9][0-9].jpg')))
if not cards:
    sys.exit('no cards')
tmp = tempfile.mkdtemp()
frames = []
for i, c in enumerate(cards):
    im = Image.open(c).convert('RGB')
    # 카드 배경색을 그대로 위아래로 이어 붙임(어두운 카드는 어둡게)
    bg = Image.new('RGB', (1080, 1920), im.getpixel((5, 5)))
    bg.paste(im.resize((1080, 1350)), (0, 285))
    p = os.path.join(tmp, f'f{i}.png'); bg.save(p); frames.append((p, D))
logo = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'logo.png')).convert('RGB').resize((1080, 1080))
end = Image.new('RGB', (1080, 1920), INK); end.paste(logo, (0, 420))
pe = os.path.join(tmp, 'end.png'); end.save(pe); frames.append((pe, END))
args = ['ffmpeg', '-y', '-loglevel', 'error']
for p, t in frames:
    args += ['-loop', '1', '-t', str(t), '-i', p]
args += ['-f', 'lavfi', '-t', '60', '-i', 'anullsrc=r=44100:cl=stereo']
n = len(frames)
fc = ''.join(f"[{i}]scale=1080:1920,zoompan=z='1+0.0006*on':d=1:s=1080x1920:fps=30,format=yuv420p,setsar=1[v{i}];" for i in range(n))
prev, off = 'v0', 0.0
for i in range(1, n):
    off += frames[i - 1][1] - X
    lab = f'a{i}'
    fc += f'[{prev}][v{i}]xfade=transition=fade:duration={X}:offset={off:.2f}[{lab}];'
    prev = lab
fc = fc.rstrip(';')
total = sum(t for _, t in frames) - X * (n - 1)
args += ['-filter_complex', fc, '-map', f'[{prev}]', '-map', f'{n}:a', '-t', f'{total:.2f}',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', out]
subprocess.run(args, check=True)
print('reel', out, round(total, 1), 's')
