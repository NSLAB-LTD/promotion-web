#!/usr/bin/env python3
"""NSLab Scholar Monitor — GitHub Actions 백엔드"""
import os, json, hashlib, datetime, time, sys
from pathlib import Path

ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY","")
WP_SITE_URL     = os.environ.get("WP_SITE_URL","https://nslab.tech").rstrip("/")
WP_USERNAME     = os.environ.get("WP_USERNAME","")
WP_APP_PASSWORD = os.environ.get("WP_APP_PASSWORD","")
TEST_MODE       = os.environ.get("TEST_MODE","false").lower()=="true"

IDENTITY_KW = ["nslab","kumoh","kit","ict-crc","dong-seong","금오"]
FIELD_KW = {
    "AI / ML":    ["machine learning","deep learning","federated","ai-driven","predictive","neural"],
    "IoT / 5G":   ["iot","internet of things","5g","6g","sensor"],
    "Blockchain": ["blockchain","distributed ledger","smart contract","purechain"],
    "Defense S/W":["naval","defense","military","fieldbus","dds","combat","uav"],
    "Metaverse":  ["metaverse","virtual reality","xr","vr","digital twin"],
    "Security":   ["security","intrusion detection","authentication","privacy","cryptograph"],
}
SEEN   = Path("seen_papers.json")
RESDIR = Path("results"); RESDIR.mkdir(exist_ok=True)

def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def log(lv,msg): print(f"[{now()}] {'✓✗⚠ℹ📡'[['OK','ERR','WARN','INFO','NEW'].index(lv)] if lv in ['OK','ERR','WARN','INFO','NEW'] else '·'} {msg}",flush=True)
def ph(t): return hashlib.md5(t.strip().lower().encode()).hexdigest()[:12]
def field_of(p):
    t=json.dumps(p,ensure_ascii=False).lower()
    for f,kws in FIELD_KW.items():
        if any(k in t for k in kws): return f
    return "AI / ML"

def scan():
    log("INFO","Scholar 스캔 시작")
    try:
        from scholarly import scholarly as sch
        author = sch.fill(next(sch.search_author("Dong-Seong Kim")),sections=["publications"])
        papers=[]
        for pub in author.get("publications",[]):
            try:
                f=sch.fill(pub); bib=f.get("bib",{})
                p={"title":bib.get("title","").strip(),"authors":bib.get("author",""),
                   "journal":bib.get("journal") or bib.get("booktitle") or "",
                   "year":str(bib.get("pub_year") or ""),"doi":f.get("pub_url",""),
                   "abstract":bib.get("abstract","")[:300],"cites":f.get("num_citations",0)}
                if p["title"] and any(k in json.dumps({**p,**bib},ensure_ascii=False).lower() for k in IDENTITY_KW):
                    p["field"]=field_of(p); papers.append(p)
                time.sleep(0.3)
            except: continue
        log("OK",f"{len(papers)}편 확인 (동일인물 검증 완료)")
        return papers
    except Exception as e:
        log("ERR",f"Scholar 오류: {e}"); return []

def find_new(papers):
    seen={}
    if SEEN.exists():
        try: seen=json.loads(SEEN.read_text())
        except: pass
    new=[]
    for p in papers:
        h=ph(p["title"])
        if h not in seen:
            new.append(p); seen[h]={"title":p["title"],"detected":now()}
    SEEN.write_text(json.dumps(seen,ensure_ascii=False,indent=2))
    if new: log("NEW",f"신규 {len(new)}편: "+", ".join(p['title'][:40] for p in new))
    else: log("OK","신규 없음")
    return new

def gen_pr(paper):
    if not ANTHROPIC_KEY: log("WARN","ANTHROPIC_API_KEY 없음"); return None
    import anthropic
    log("INFO",f"AI 홍보문 생성: {paper['title'][:48]}...")
    client=anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    prompt=(f"연구실 홍보 전문가로서 5채널 한국어 홍보 콘텐츠를 JSON으로만 생성하세요.\n\n"
            f"제목: {paper['title']}\n저자: {paper['authors']}\n저널: {paper['journal']} ({paper['year']})\n"
            f"기관: 금오공과대학교 NSLab, 지도교수 김동성, (주)앤에스랩\n\n"
            'JSON만 반환:\n{"blog":"기술블로그 200자","linkedin":"LinkedIn 100자 #해시태그3개",'
            '"press":"보도자료 150자 공식체","twitter":"트위터 75자 #해시태그","newsletter":"뉴스레터 120자"}')
    msg=client.messages.create(model="claude-sonnet-4-20250514",max_tokens=1000,messages=[{"role":"user","content":prompt}])
    text=msg.content[0].text.strip().replace("```json","").replace("```","").strip()
    pr=json.loads(text); log("OK","홍보문 5채널 완료"); return pr

def post_wp(paper, pr):
    if not WP_APP_PASSWORD: log("WARN","WP_APP_PASSWORD 없음"); return None
    if TEST_MODE: log("INFO","[TEST] WP 게시 건너뜀"); return {"test":True}
    import requests
    log("INFO",f"WordPress 게시: {paper['title'][:45]}...")
    r=requests.post(f"{WP_SITE_URL}/wp-json/nslab/v1/new-paper",
        json={"title":paper["title"],"authors":paper["authors"],"journal":paper["journal"],
              "year":paper["year"],"doi":paper.get("doi",""),"field":paper.get("field",""),"pr":pr},
        auth=(WP_USERNAME,WP_APP_PASSWORD),timeout=30)
    if r.status_code in(200,201):
        d=r.json(); log("OK",f"게시 완료 ID:{d.get('post_id','?')}"); return d
    log("ERR",f"WP {r.status_code}: {r.text[:150]}"); return None

def main():
    print("="*60); print(f"  NSLab Scholar Monitor | {now()}"); print("="*60)
    papers=scan()
    if not papers: sys.exit(0)
    new=find_new(papers)
    if not new: sys.exit(0)
    for p in new:
        pr=gen_pr(p)
        if pr:
            wp=post_wp(p,pr)
            (RESDIR/f"pr_{ph(p['title'])}_{datetime.date.today()}.json").write_text(
                json.dumps({"processed_at":now(),"paper":p,"pr":pr,"wp":wp},ensure_ascii=False,indent=2))
        time.sleep(2)
    log("OK",f"완료: {len(new)}편")

if __name__=="__main__": main()
