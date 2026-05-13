# NSLab PR Dashboard — 배포 가이드

## 파일 구조

```
nslab-pr-deploy/
├── index.html                          ← 웹앱 (이 파일 하나로 완전 동작)
├── netlify.toml                        ← Netlify 배포 설정
├── scholar_monitor.py                  ← GitHub Actions 백엔드 스크립트
├── .github/
│   └── workflows/
│       └── scholar-monitor.yml         ← 매일 09:00 KST 자동 실행
└── README.md
```

---

## ─── 방법 A: GitHub Pages (무료, 가장 간단) ───────────────

### 1단계 — 저장소 만들기

1. github.com 로그인
2. 우상단 **+** → **New repository**
3. Repository name: `nslab-pr-dashboard`
4. **Public** 선택 (GitHub Pages 무료 사용)
5. **Create repository** 클릭

### 2단계 — 파일 업로드

**방법 1: 웹에서 직접 업로드 (가장 쉬움)**
1. 저장소 메인 화면 → **Add file** → **Upload files**
2. `index.html`, `scholar_monitor.py` 를 드래그 업로드
3. `.github/workflows/scholar-monitor.yml` 은 수동으로:
   - **Add file** → **Create new file**
   - 파일명: `.github/workflows/scholar-monitor.yml`
   - 내용 붙여넣기 → **Commit changes**

**방법 2: Git 사용**
```bash
git clone https://github.com/YOUR_ID/nslab-pr-dashboard
# 파일 4개를 폴더에 복사
git add .
git commit -m "init: NSLab PR Dashboard"
git push
```

### 3단계 — GitHub Pages 활성화

1. 저장소 → **Settings** 탭
2. 좌측 메뉴 **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** / **/ (root)** → **Save**
5. 1~2분 후 URL 발급: `https://YOUR_ID.github.io/nslab-pr-dashboard`

### 4단계 — Secrets 등록 (GitHub Actions 자동화용)

1. 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 으로 아래 4개 추가:

| 이름 | 값 |
|------|----|
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` (console.anthropic.com) |
| `WP_SITE_URL` | `https://nslab.tech` |
| `WP_USERNAME` | WordPress 관리자 아이디 |
| `WP_APP_PASSWORD` | WordPress 앱 비밀번호 (아래 참고) |

### 5단계 — 첫 실행 테스트

1. 저장소 → **Actions** 탭
2. **NSLab Scholar Monitor** 클릭
3. **Run workflow** → `test_mode: true` 로 먼저 실행
4. 로그 확인 후 이상 없으면 `test_mode: false` 로 실운영

---

## ─── 방법 B: Netlify (무료, HTTPS 자동) ─────────────────────

### 1단계 — Netlify 계정 (이미 있으면 생략)

- netlify.com → **Sign up** → GitHub 계정으로 로그인

### 2단계 — 사이트 배포

**방법 1: GitHub 연동 (권장)**
1. Netlify 대시보드 → **Add new site** → **Import an existing project**
2. **Deploy with GitHub** → 저장소 선택 (`nslab-pr-dashboard`)
3. Build settings: 모두 기본값 유지 → **Deploy site**
4. 자동 HTTPS URL 발급: `https://nslab-pr-XXXX.netlify.app`
5. Site settings → **Change site name** → `nslab-pr-dashboard` 로 변경

**방법 2: 드래그 & 드롭 (GitHub 없이)**
1. Netlify 대시보드 → **Sites** 탭
2. **index.html** 파일을 화면에 직접 드래그 드롭
3. 즉시 배포 완료!

### 3단계 — 커스텀 도메인 (선택)

Site settings → Domain management → **Add custom domain**
- `pr.nslab.tech` 형식으로 서브도메인 연결 가능

---

## ─── WordPress 앱 비밀번호 발급 ─────────────────────────────

nslab.tech WordPress에 자동 게시하려면:

1. `https://nslab.tech/wp-admin` 로그인
2. 우상단 프로필 → **프로필 편집**
3. 하단 **애플리케이션 비밀번호** 섹션
4. 이름: `NSLab Scholar Bot` → **새 애플리케이션 비밀번호 추가**
5. 발급된 비밀번호 복사 → GitHub Secrets에 `WP_APP_PASSWORD` 로 저장

---

## ─── 웹앱 사용법 ──────────────────────────────────────────────

배포 후 URL에 접속하면:

1. **설정 탭** → Anthropic API 키 입력 → 저장
2. 상단 **API 상태** 버튼이 🟢로 바뀌면 준비 완료
3. **Scholar 스캔** 버튼 → 논문 감지 시뮬레이션
4. **✦ 홍보 생성** 버튼 → Claude AI가 5채널 한국어 홍보문 즉시 생성
5. **↑ nslab.tech 게시** → WordPress Draft 자동 업로드
6. 이후 nslab.tech 관리자에서 검토 후 Publish

GitHub Actions가 설정되면 → **매일 09:00 KST 자동 실행**,
신규 논문 감지 시 홍보문 생성 + nslab.tech 자동 게시 + 이메일 알림까지 완전 자동화 완성.

---

## ─── 자동화 완성 후 일상 워크플로우 ───────────────────────────

```
매일 09:00 KST 자동 실행
    신규 없음 → 1분 내 종료, 아무 일 없음

    신규 논문 있음:
        ① 교수님 이메일 수신
            "NSLab PR — 신규 논문 홍보문 승인 요청"
        ② 이메일의 WP 편집 링크 클릭
        ③ 홍보문 5채널 내용 확인
        ④ "게시" 클릭 → nslab.tech 즉시 공개
```

---

nslab.tech | nslab@nslab.tech
