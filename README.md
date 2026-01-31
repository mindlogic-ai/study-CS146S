# CS146S Study - Mindlogic

Stanford CS146S: The Modern Software Developer 스터디

> Original course: [CS146S: The Modern Software Developer](https://themodernsoftware.dev)

---

## 스터디 운영 방식

### 과제 제출
- **마감**: 스터디 당일 7PM
- **제출 방법**: GitHub PR
- **PR 제목 형식**: `[Week{N} - {이니셜}]` (예: `[Week1 - jhs]`)

### 발표 & 공유
- 메인 발표자 1명
- Workflow 공유 시간 (clawdbot, Claude Code 세팅, 유용한 MCP 서버 등)
- 경험담 자유 공유

### 페널티
- 2번 연속 미제출 OR 참석 X → 스터디 아웃 (불가피한 사유 제외)

---

## 폴더 구조

```
study-CS146S/
├── week1/                    # 원본 과제 (참고용)
├── week2/
├── ...
└── submissions/              # 제출 폴더
    ├── jhs/
    │   ├── week1/            # jhs의 week1 제출
    │   └── week2/
    ├── abc/
    │   ├── week1/
    │   └── ...
```

---

## 과제 제출 방법

### 1. 브랜치 생성
```bash
git checkout main
git pull origin main
git checkout -b week{N}-{이니셜}
# 예: git checkout -b week1-jhs
```

### 2. 주차 폴더 복사
```bash
# 본인 submissions 폴더가 없으면 생성
mkdir -p submissions/{이니셜}

# 해당 주차 폴더 복사
cp -r week{N} submissions/{이니셜}/

# 예시
mkdir -p submissions/jhs
cp -r week1 submissions/jhs/
```

### 3. 과제 진행
- `submissions/{이니셜}/week{N}/` 폴더에서 과제 작업
- 예: `submissions/jhs/week1/`

### 4. 커밋 & 푸시
```bash
git add submissions/{이니셜}/week{N}
git commit -m "[Week{N} - {이니셜}] 과제 완료"
git push origin week{N}-{이니셜}

# 예시
git add submissions/jhs/week1
git commit -m "[Week1 - jhs] 과제 완료"
git push origin week1-jhs
```

### 5. PR 생성
- GitHub에서 Pull Request 생성
- **제목**: `[Week{N} - {이니셜}]` (예: `[Week1 - jhs]`)
- **Base**: `main`

---

## Repo Setup

Python 3.12 환경에서 진행합니다.

1. **Anaconda 설치**
   - [Anaconda Individual Edition](https://www.anaconda.com/download) 다운로드 및 설치

2. **Conda 환경 생성**
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

3. **Poetry 설치**
   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

4. **의존성 설치**
   ```bash
   poetry install --no-interaction
   ```

---

## 멤버

| 이니셜 | 이름 |
|--------|------|
| jhs | 신재호 |
| shp | 박상현 |
| | |

---

## 주차별 과제

| 주차 | 주제 | 마감 |
|------|------|------|
| Week 1 | - | - |
| Week 2 | - | - |
| Week 3 | - | - |
| Week 4 | - | - |
| Week 5 | - | - |
| Week 6 | - | - |
| Week 7 | - | - |
| Week 8 | - | - |
