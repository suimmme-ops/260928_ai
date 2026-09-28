# 🍎 Hello, Teacher! — 자기소개 웹페이지

잡지 콜라주 스타일의 선생님 자기소개 페이지입니다. 가운데에는 SVG로 그린 3D 느낌의 선생님 캐릭터가 있고, 모든 타이틀과 내용은 사이드바에서 바로 고칠 수 있습니다.

- `==문장==` → 형광펜 하이라이트, `**문장**` → 굵게
- 타이틀 밑줄 색은 팔레트에서 고를 수 있습니다.

## 실행 방법

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 내용 편집 · 저장

1. 사이드바(왼쪽 위 `>` 버튼)를 열고 비밀번호를 입력하면 편집 모드가 켜집니다.
2. 내용을 고친 뒤 **💾 저장하기** 를 누르면 `profile.json` 에 저장되고, 사이트에 접속하는 모든 사람에게 그 내용이 보입니다.
3. 재시작·재배포 후에도 유지하려면 `profile.json` 을 GitHub에 커밋하세요.
   (배포된 사이트에서 편집했다면 **⬇️ profile.json 내려받기** 로 받은 파일을 저장소에 올리면 됩니다.)

### 비밀번호 설정

- 로컬: `.streamlit/secrets.toml` 파일에 `admin_password = "원하는 비밀번호"` (git에 올라가지 않음)
- Streamlit Cloud: 앱 설정 → **Secrets** 에 같은 줄을 추가
