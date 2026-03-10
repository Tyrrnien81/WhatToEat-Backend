# Changelog

## Login Initialization

### Added

- Node.js + TypeScript backend scaffold for local auth testing
- PostgreSQL environment configuration with `.env.example`
- Local `.env` for immediate development testing
- Docker Compose PostgreSQL setup for local DB startup
- SQL schema for `users` and `user_credentials`
- Interactive terminal CLI for register/login/list user flows
- JWT issuing logic after successful login

### Edited Workflow Summary

1. Added backend project settings with TypeScript build and CLI scripts.
2. Added PostgreSQL connection config, local `.env`, Docker Compose setup, and DB initialization script.
3. Added `users` table for profile data and `user_credentials` table for password-based local login.
4. Added password hashing with `bcryptjs`.
5. Added JWT issuance after successful local login.
6. Added interactive terminal prompts so login can be tested manually.

### Current Login Flow

1. Run DB initialization.
2. Open the auth CLI in terminal.
3. Register with name, email, and password.
4. Login with email and password.
5. Receive a JWT and user payload on success.

### Files Added

- `package.json`
- `tsconfig.json`
- `.gitignore`
- `.env.example`
- `docker-compose.yml`
- `sql/init.sql`
- `src/config.ts`
- `src/db.ts`
- `src/auth/password.ts`
- `src/auth/jwt.ts`
- `src/auth/userRepository.ts`
- `src/auth/authService.ts`
- `src/cli.ts`
- `src/scripts/initDb.ts`