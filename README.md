# Insurance Coverage Analysis

14개 보험사의 2025년 7월 공시 자료 담보분석 엑셀을 작성·검토하는 과정에서 저장된 Python·JavaScript 작업 코드를 모은 비공개 아카이브입니다.

## 범위

- 보험사별 원본 목록·PDF 텍스트·표·목차·OCR 보조·담보 레코드 구성.
- 엑셀 생성·서식·원문 연결, 검증·보정·문구 수정·최종 점검.
- DB 예시 조회 및 실행 환경 점검 보조 코드.
- 총 145개 기존 스크립트. 원본 파일명과 내용을 그대로 보존했습니다.

[보험사별 전체 코드 목록](docs/CODE_INDEX.md)과 [실행 안내](docs/RUNNING.md)를 참고하세요.

## 구조

```text
work/                   기존 분석 코드 (원래 상대 경로와 Python 모듈 참조 유지)
docs/CODE_INDEX.md      보험사별·용도별 전체 목록
docs/source-index.json 원본 출처·SHA-256·크기·import 목록
docs/RUNNING.md         의존성·경로·재실행 조건
requirements.txt       PDF·XML 분석 Python 의존성
requirements-db.txt    선택 DB 조회 의존성
package.json           pdfjs-dist 의존성 및 안내
tools/check_archive.py 정적 검증 도구 (새로 추가)
```

## 보관 대상과 실행 상태

원본 PDF·최종 XLSX·중간 JSON·텍스트·OCR 결과·미리보기 이미지·DB 결과·인증정보·라이브러리 본체는 포함하지 않았습니다. 코드에 직접 작성된 담보 규칙·분석 설명은 코드의 일부로 보존합니다.

이 코드는 완성된 범용 분석 엔진이나 한 번 실행하면 모든 보험사의 결과를 자동 재생성하는 파이프라인이 아닙니다. 특정 원본 페이지·표·중간 파일을 기준으로 작성된 작업 코드이며 검토 후 추가된 수정 단계가 있습니다. 원본과 작업 당시 중간 데이터·검토 조건을 확보해야 결과를 재현할 수 있습니다.

Python 구문·JavaScript 구문·원본 해시를 정적으로 확인합니다. PDF 분석·DB 연결·OCR·엑셀 재생성은 이번 업로드 과정에서 실행하지 않았습니다. 보조 코드가 저장되어 있다는 사실이 모든 파일의 완전한 실행 로그를 증명하지는 않습니다.

## 코드 확인

저장소 루트에서 실행합니다. 코드를 import하거나 분석 작업을 실행하지 않습니다.

```powershell
pythontools/check_archive.py
pythontools/check_archive.py --node node
```

두 번째 명령은 Node가 설치된 경우 `.mjs` 구문도 검사합니다.

## 환경·의존성

Python 3.10 이상과 Node ES modules 환경을 사용합니다. 일반 Python 의존성은 `requirements.txt`, DB 조회는 `requirements-db.txt`로 분리했습니다. 정확한 기존 라이브러리 잠금 파일은 남아 있지 않아 고정 버전을 새로 꾸며내지 않았습니다.

엑셀 작성 코드가 사용하는 `@oai/artifact-tool`은 작업 당시 Codex 제공 런타임에 있던 라이브러리입니다. 일반 npm에서 받을 수 있다고 가정하지 않으며 패키지 본체를 이 저장소에 복사하지 않았습니다. 해당 라이브러리를 사용할 수 있는 환경에서만 기존 생성 코드를 실행할 수 있고, 그 외 환경에서는 XLSX 작성 부분을 다른 라이브러리로 변환하는 별도 작업이 필요합니다.

Poppler·OCR 도구의 외부 실행 경로는 `docs/RUNNING.md`에 설명했습니다. 현재 작업 경로를 그대로 사용하는 코드가 있으므로 실행 전 확인하세요.

현재 포장 환경에서 확인한 버전은 `docs/runtime-observed.json`에 별도 기록했습니다. 원래 모든 작업이 이 버전에서 실행되었다는 뜻은 아닙니다. `pdfjs-dist`는 이 환경에서 확인한 버전으로 지정했습니다.
