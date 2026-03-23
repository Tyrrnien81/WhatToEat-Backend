# Architecture
Google Doc을 그대로 옮긴 파일

## Status

- In progress

## Team

- Product manager: Person
- Engineer: Person
- UX designer: Person
- UX researcher: Person

## 1. Product Overview

### 1.1 Purpose

UW-Madison 학식 메뉴를 기반으로 사용자의 영양 목표에 맞는 식단을 자동 추천하는 모바일 애플리케이션을 개발한다.

- Nutrislice에서 제공하는 학식 메뉴 데이터를 사용
- 사용자 목표(칼로리, 단백질 등)를 반영
- 실제로 선택 가능한 메뉴 조합을 계산해 추천

## 2. Problem Statement

대학생, 특히 기숙사 거주 학생들은 건강한 식단을 유지하기 어렵다.

- 선택 가능한 음식이 학식 메뉴로 제한됨
- 일반 식단 추천 앱은 집밥/외식을 가정하는 경우가 많음
- 실제 학식 메뉴와 추천 결과가 맞지 않음
- 운동하는 학생은 단백질 목표를 맞추기 어려움
- 비건, 글루텐 프리 등 특정 식단 사용자는 선택지가 더 제한됨

따라서 현재 제공되는 학식 메뉴 안에서 목표 영양을 만족하는 현실적인 식단 조합을 자동으로 계산하는 시스템이 필요하다.

## 3. Target Audience

- UW-Madison 재학생: 기숙사 거주, 학식 의존도 높음
- 운동하는 학생: 근육 증량 / 감량 목표, 단백질 중요
- 특정 식단 사용자: 비건, 글루텐 프리 등

## 4. Product Objectives

- 제공되는 메뉴 기반 추천
- 사용자의 영양 목표 자동 계산
- 실시간 학식 메뉴 반영
- 실행 가능성 높은 식단 제안

## 5. MVP

### 5.1 Menu Data Collection

Nutrislice 데이터를 기반으로 학식 메뉴를 수집한다.

- Nutrislice API 또는 크롤링
- 학식당 선택
- 아침 / 점심 / 저녁 메뉴 구분
- 메뉴 영양정보 수집

### 5.2 User Settings

사용자는 자신의 식단 목표를 설정할 수 있다.

- 한 끼 목표 칼로리
- 탄수화물 / 단백질 / 지방 비율
- 추가 영양소 목표
- 알러지 필터
- 비건 / 종교 필터
- 이용 학식당 선택

### 5.3 Meal Recommendation Algorithm

- 현재 메뉴 필터링
- 영양 정보 계산
- 메뉴 조합 생성
- 목표 영양과 가장 가까운 조합 선택

### 5.4 Meal Tracking

- 추천 식단 실제 섭취 여부 체크
- 목표 달성률 시각화

## 6. Future Features

- 식사 시간 알림
- 목표 기반 자동 영양 비율 추천
- 다른 학교 학식 지원
- 주간 / 월간 영양 통계
- 친구와 식단 공유

## 7. Technical Architecture

### 7.1 Frontend

기술 스택:

- React Native

사용 이유:

- iOS / Android 동시 개발 가능
- React 기반으로 개발 속도 빠름
- 유지보수 용이

추가 라이브러리:

- Chart.js: 영양 섭취 통계 시각화

### 7.2 Backend

Backend는 Node.js 기반 API 서버로 구성된다.

기술:

- Node.js + TypeScript

선택 이유:

- 프론트와 같은 언어(JavaScript) 사용
- 개발 속도 빠름
- TypeScript로 타입 안정성 확보

주요 역할:

- API 제공
- 인증 / 권한 관리
- 추천 요청 처리
- DB 데이터 가공

### 7.3 Recommendation Engine

추천 알고리즘은 Python으로 구현한다.

이유:

- 수학 계산 및 최적화 라이브러리가 풍부함
- 데이터 분석 및 알고리즘 구현에 적합함

### 7.4 Database

- PostgreSQL 사용

이유:

- 안정적인 관계형 데이터베이스
- 복잡한 데이터 관계 처리 가능
- JSON 지원

저장 데이터:

- 메뉴 데이터
- 영양 정보
- 사용자 설정
- 식단 기록

### 7.5 Cache

- Redis 사용

역할:

- 자주 조회되는 데이터를 메모리에 저장하여 빠르게 제공

대표 캐시 데이터:

- 오늘 메뉴
- 인기 식당
- 식당 리스트

### 7.6 Object Storage

- AWS S3 사용

용도:

- Nutrislice API 원본 데이터 저장
- 파싱 결과 스냅샷 저장
- 디버깅 및 재처리

## 8. System Architecture

### 8.1 Main Components

#### Client (Web / Mobile)

사용자가 직접 사용하는 애플리케이션.

기술:

- React Native
- Swift (iOS)
- Kotlin (Android)

#### API Gateway / BFF (Node.js / TypeScript)

역할:

- 인증 / 권한 관리
- Google 로그인
- JWT 발급 / 검증
- 사용자별 데이터 접근 통제
- 조회 API 제공
- Redis 캐시 우선 조회 후, 없으면 DB 조회
- 프론트에서 쓰기 좋은 형태로 데이터 가공
- Rate limit / 로깅 / 에러 처리
- 특정 IP 과도 호출 방지
- 장애 분석용 로그 / 추적

Node.js + TypeScript 사용 이유:

- 프론트(React)와 언어 통일
- 개발 속도 확보

#### Ingestion Worker

Nutrislice에서 메뉴 데이터를 주기적으로 수집하고, 정규화한 뒤 DB에 저장한다.

역할:

- 식당 목록 / slug 갱신
- 오늘 ~ N일 메뉴 데이터 수집
- 응답 파싱 후 우리 DB 스키마로 변환
- 실패 시 재시도 / 백오프 / 장애 로그 기록
- 캐시 무효화

분리 이유:

- 성능 / 안정성 확보
- 사용자가 조회할 때마다 Nutrislice를 직접 호출하지 않도록 함
- 워커가 미리 DB에 저장해두면 조회 응답이 빨라짐
- Nutrislice 구조 변경 시 워커만 수정하면 됨
- Nutrislice 장애 시에도 마지막 성공 데이터를 제공 가능

#### DB (PostgreSQL)

역할:

- 정규화된 영구 저장소

저장 대상:

- 메뉴: 식당 / 날짜 / 끼니 / 스테이션 / 아이템 / 알레르기 / 영양
- 사용자 데이터: 즐겨찾기, 설정

#### Cache (Redis)

역할:

- 자주 조회되는 결과를 메모리에 저장하고 바로 반환

대표 캐시 대상:

- 오늘 메뉴
- 인기 식당
- 식당 리스트

#### Object Storage (S3)

역할:

- 원본 수집 데이터 보관
- 파싱 결과 스냅샷 저장
- 디버깅 및 재처리 지원

## 9. Data Flow

### Flow 1: Login

1. User
2. Frontend에서 로그인 요청
3. Backend 처리
4. DB에서 사용자 정보 확인
5. Backend에서 인증 성공 처리
6. Frontend에 로그인 완료 응답
7. User

### Flow 2: Menu Data Fetching

1. Scheduler가 매일 1회 실행
2. Ingestion Worker 동작
3. Nutrislice API 호출
4. Worker가 JSON 파싱 및 정규화
5. PostgreSQL DB 저장
6. 로그 / 모니터링 기록

### Flow 3: Recommendation

1. User
2. Frontend에서 추천 요청
3. API Gateway / BFF 수신
4. Redis Cache 확인
5. Cache miss 시 PostgreSQL DB 조회
6. Recommendation Engine (Python) 호출
7. 추천 메뉴 생성
8. API Gateway / BFF 응답 구성
9. Frontend에서 추천 결과 및 영양정보 표시
10. User가 선택 / 확인

## 10. Open Question

- cron job 사용 여부 검토 필요