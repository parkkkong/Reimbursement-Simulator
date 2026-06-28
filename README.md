# Reimbursement Simulator

## 개요
이 프로젝트는 PySide6 기반의 데스크톱 앱으로, 엑셀/CSV 데이터를 불러와 그리드로 검토한 뒤 SQLite 데이터베이스에 저장하고, 저장된 데이터를 그룹별로 확인할 수 있도록 구성한 예시입니다.

## 주요 기능
- 탭 기반 메인 윈도우
- Import 탭: 파일 선택, 데이터 미리보기, 행 삭제, 데이터베이스 저장
- Group 탭: DB에 저장된 데이터의 그룹별 확인
- Analysis 탭: 향후 기능 확장을 위한 placeholder

## 실행 방법
1. Python 3.14 이상 환경 준비
2. 필요한 패키지 설치
   - `pip install PySide6 SQLAlchemy openpyxl pandas`
3. 실행
   - `python main.py`

## 구조
- main.py: 앱 진입점
- app/main_window.py: 메인 UI 및 로직
- app/models.py: SQLAlchemy 모델 및 DB 초기화
- app/main_window.ui: Qt Designer용 UI 파일
- docs/PROJECT_DOCUMENTATION.md: 상세 개발 문서