import dotenv from "dotenv";

dotenv.config();

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

function parseSaltRounds(value: string | undefined): number {
  const parsed = Number(value ?? "10");
  if (!Number.isInteger(parsed) || parsed < 4) {
    throw new Error("BCRYPT_SALT_ROUNDS must be an integer >= 4");
  }
  return parsed;
}

export const config = {
  databaseUrl: requireEnv("DATABASE_URL"),
  jwtSecret: requireEnv("JWT_SECRET"),
  jwtExpiresIn: process.env.JWT_EXPIRES_IN ?? "1h",
  bcryptSaltRounds: parseSaltRounds(process.env.BCRYPT_SALT_ROUNDS)
};
