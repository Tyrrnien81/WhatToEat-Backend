# 1. User Service (로그인/회원가입)

This API handles user signin, signup, find password, google login

| Method | Endpoint | Description | JWT Required |
| --- | --- | --- | --- |
| POST | `/auth/signin` | 로그인 (이메일, 비밀번호 이용), JWT 토큰 돌려주기 | No |
| POST | `/auth/signup` | 회원가입 | No |
| POST | `/auth/google` | 구글 로그인. | No |
| POST | `/auth/forgot-pw` | mail 에 인증번호 보내서 확인 후 reset-pw 로 넘어가는걸로 | No |
| POST | `/auth/reset-pw` | 이메일 인증 이후 비밀번호를 리셋한다 | No |
| POST | `/auth/logout` | 메인화면에서 하는 것이 아닌, 나중에 환경 설정에 들어가서 | Yes |
| GET | `/auth/me` | 사용자 정보를 JWT로부터 돌려받는다 | Yes |
