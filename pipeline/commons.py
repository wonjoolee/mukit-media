# 위키미디어 공용(Wikimedia Commons) 사진 찾기·받기 — 자유 이용 허락(CC0·PD·CC BY·CC BY-SA)만.
# 사용:
#   python3 -I pipeline/commons.py search "Roland TR-808" [개수=8]   → 후보 목록(파일명·라이선스·작가·크기)
#   python3 -I pipeline/commons.py get "File:Roland TR-808 (large).jpg" <저장폴더>
#        → <저장폴더>/<안전한이름>.jpg + 같은 이름 .json(출처·라이선스·작가·원문 URL) 저장
# 위키미디어는 요청이 잦으면 429를 준다. 요청 사이 3초 쉬고, 429면 60초 뒤 한 번만 다시 시도한다. 반복 재시도 금지.
import json, os, re, sys, time, urllib.parse, urllib.request

UA = "MUKITmagazineBot/1.0 (https://www.instagram.com/mukitmag/; editorial image research)"
API = "https://commons.wikimedia.org/w/api.php"
OK = re.compile(r"^(CC0|Public domain|PD|CC BY(-SA)? ?\d(\.\d)?|CC BY(-SA)?)", re.I)  # NC·ND·저작권 표시는 제외


def call(params):
    url = API + "?" + urllib.parse.urlencode(dict(params, format="json"))
    for attempt in (1, 2):
        try:
            time.sleep(3)
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 1:
                print("429 — 60초 뒤 한 번만 다시 시도", file=sys.stderr); time.sleep(60); continue
            sys.exit(f"Commons 오류 {e.code}: 지금은 쓰지 말고 다른 사진 경로로")


def clean(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def info(pages):
    out = []
    for p in pages.values():
        if "imageinfo" not in p:
            continue
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        lic = clean(m.get("LicenseShortName", {}).get("value"))
        out.append(dict(title=p["title"], license=lic, ok=bool(OK.match(lic)) and "NC" not in lic and "ND" not in lic,
                        artist=clean(m.get("Artist", {}).get("value"))[:120], credit=clean(m.get("Credit", {}).get("value"))[:120],
                        width=ii.get("width"), height=ii.get("height"), thumb=ii.get("thumburl"), page=ii.get("descriptionurl")))
    return out


def search(q, n=8):
    d = call(dict(action="query", generator="search", gsrnamespace=6, gsrsearch=q + " filetype:bitmap", gsrlimit=n,
                  prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth=2000))
    for r in info(d.get("query", {}).get("pages", {})):
        flag = "사용가능" if r["ok"] and (r["width"] or 0) >= 1200 else "제외"
        print(f"[{flag}] {r['title']} | {r['license']} | {r['artist']} | {r['width']}x{r['height']}")


def get(title, outdir):
    d = call(dict(action="query", titles=title, prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth=2000))
    rs = info(d.get("query", {}).get("pages", {}))
    if not rs or not rs[0]["ok"]:
        sys.exit("자유 이용 허락이 아닌 사진(NC/ND/저작권) — 쓰지 않는다")
    r = rs[0]; os.makedirs(outdir, exist_ok=True)
    name = re.sub(r"[^A-Za-z0-9_-]+", "_", r["title"].split(":", 1)[1].rsplit(".", 1)[0])[:60]
    time.sleep(3)
    req = urllib.request.Request(r["thumb"], headers={"User-Agent": UA})
    open(os.path.join(outdir, name + ".jpg"), "wb").write(urllib.request.urlopen(req, timeout=60).read())
    r["card_credit"] = f"PHOTO · {r['artist'] or '작가 미상'} / {r['license']} · Wikimedia Commons"
    json.dump(r, open(os.path.join(outdir, name + ".json"), "w"), ensure_ascii=False, indent=1)
    print("saved", name + ".jpg", "|", r["card_credit"])


if __name__ == "__main__":
    if sys.argv[1] == "search":
        search(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 8)
    else:
        get(sys.argv[2], sys.argv[3])
