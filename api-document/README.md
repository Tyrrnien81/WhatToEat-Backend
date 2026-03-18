# API Documentation

## HTTP Method Guide

- `GET` = 데이터 가져오기
- `POST` = 데이터 만들기
- `PATCH` = 데이터 수정하기
- `DELETE` = 데이터 삭제하기

## Authentication Header

개인화된 정보가 필요한 API들은 요청 헤더에 JWT token이 있어야 합니다.

```http
Authorization: Bearer <JWT token>
```

## Services

| # | Service | File | Description |
|---|---------|------|-------------|
| 1 | User Service | [auth.md](auth.md) | 로그인/회원가입/구글 로그인/비밀번호 찾기 |
| 2 | Questionnaire | [questionnaire.md](questionnaire.md) | 유저 정보 수집 및 preferences 관리 |
| 3 | Homescreen | [homescreen.md](homescreen.md) | 추천 메뉴, 영양 목표, 메뉴 저장 |
| 4 | Dining Hall | [dining-hall.md](dining-hall.md) | 다이닝 홀 및 메뉴 조회 |
| 5 | Scan | [scan.md](scan.md) | 음식 사진 인식 및 영양소 기록 |
| 6 | Community | [community.md](community.md) | 커뮤니티 포스트 CRUD |
| 7 | Profile | [profile.md](profile.md) | 유저 프로필 및 식사 기록 관리 |
