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
| 1 | User Service | [auth/auth.md](auth/auth.md) | 로그인/회원가입/구글 로그인/비밀번호 찾기 |
| 2 | Questionnaire | [questionnaire/questionnaire.md](questionnaire/questionnaire.md) | 유저 정보 수집 및 preferences 관리 |
| 3 | Homescreen | [homescreen/homescreen.md](homescreen/homescreen.md) | 추천 메뉴, 영양 목표, 메뉴 저장 |
| 4 | Dining Halls | [dining-halls/dining-halls.md](dining-halls/dining-halls.md) | 다이닝 홀 및 메뉴 조회 |
| 5 | Scan | [scan/scan.md](scan/scan.md) | 음식 사진 인식 및 영양소 기록 |
| 6 | Community | [community/community.md](community/community.md) | 커뮤니티 포스트 CRUD |
| 7 | Profile | [profile/profile.md](profile/profile.md) | 유저 프로필 및 식사 기록 관리 |
