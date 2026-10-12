# 실행 조건·확인 절차

## 기본 사항

기존 스크립트를 모두 `work/`에 보존하여 상대 경로와 `mirae_detail_revision`·`abl_phrase_scan` 등 모듈 참조를 유지합니다. 실행 시 현재 디렉터리를 저장소 루트로 지정합니다.

## 실행 전 준비

1. 원본 상품별 PDF 폴더와 보험사별 분석 대상·기준 시점을 확인합니다.
2. 코드에 있는 `C:/Users/FAS/Desktop/데이터분석` 또는 Windows 역슬래시 경로를 자신의 원본 위치에 맞춥니다.
3. `work/<보험사>/manifest.json`, 페이지 JSON, 표·구간·records JSON 등 참조 파일을 생성하거나 작업 당시 파일을 확보합니다.
4. Excel 생성·수정·검증 단계의 `outputs/...xlsx`와 `Desktop/데이터분석/...xlsx` 참조가 같은 파일인지 확인합니다.
5. 원본 파일과 기존 결과를 별도로 보존한 작업 환경에서 필요한 단계만 실행합니다. `_revise`·`_edit`·`_polish`·`_finalize` 등은 데이터·결과를 수정할 수 있습니다.

## 역할별 흐름

`원본 조사 → 텍스트·표 추출 → 구간·목차 확인 → 담보 레코드 구성 → 엑셀 작성 → 검증 → 필요 보정 → 재검증`

이는 개념적 흐름입니다. 실제 보험사별 실행 순서는 파일 안의 읽기·쓰기 경로와 검토 결과를 확인해야 합니다. 저장된 파일만으로 아직 검증되지 않은 일괄 실행 순서를 확정하지 않았습니다.

## 보조 도구

- Python: pypdf, pdfplumber, pypdfium2, lxml.
- JS PDF: pdfjs-dist의 `legacy/build/pdf.mjs`.
- JS Excel: Codex 런타임의 `@oai/artifact-tool`.
- 원문 이미지: `pdftoppm.exe` 등 Poppler 외부 도구 경로를 사용합니다.
- OCR: 미래에셋 등 보조 코드의 렌더링·OCR 명령과 외부 프로그램 설치를 확인합니다. 이 저장소는 OCR 실행 파일을 포함하지 않습니다.
- DB 예시: `review_product_coverages.py`는 pg8000과 환경변수 비밀번호, 기존 서버 설정을 사용합니다. 일반 담보 추출에 필수인 단계가 아닙니다. 연결 대상·권한을 확인하지 않고 실행하지 마세요.
- 모든 import가 설치되더라도 JSON·원본·외부 도구가 없으면 실행되지 않습니다.

## Python 설치 예시

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

DB 예시 조회가 필요한 환경에서만 `requirements-db.txt`를 사용합니다.

## 회사별 기본 코드

| 보험사 | 분석 | 엑셀 생성 |
|---|---|---|
| 교보생명 | kyobo_records.py | kyobo_workbook.mjs |
| 롯데손해보험 | lotte_records.py | lotte_workbook.mjs |
| 미래에셋생명 | mirae_records.py | mirae_workbook.mjs |
| 신한라이프 | shinhan_records.py | shinhan_workbook.mjs |
| 푸본현대생명 | fubon_records.py | fubon_workbook.mjs |
| 현대해상 | hyundai_records.py | hyundai_workbook.mjs |
| 흥국생명 | heungkuk_life_records.py | heungkuk_life_workbook.mjs |
| 흥국화재 | heungkuk_records.py | heungkuk_workbook.mjs |
| ABL생명 | build_records.py / abl_revise.py | create_workbook.mjs |
| AIG손해보험 | aig_records.py | aig_workbook.mjs |
| DB생명 | db_records.py | db_workbook.mjs |
| KB라이프생명 | kb_records.py | kb_workbook.mjs |
| NH농협생명 | nh_records.py | nh_workbook.mjs |
| NH농협손해보험 | nh_nonlife_records.py | nh_nonlife_workbook.mjs |

전체 보조·수정·검증 코드 목록은 CODE_INDEX.md에 있습니다.
