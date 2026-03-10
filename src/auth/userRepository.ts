import { randomUUID } from "node:crypto";
import { pool } from "../db";

export interface UserRecord {
  id: string;
  email: string;
  name: string;
  provider: string;
  token: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface LocalAuthUser extends UserRecord {
  passwordHash: string;
}

export interface RegisterLocalUserInput {
  email: string;
  name: string;
  passwordHash: string;
}

function mapUserRecord(row: Record<string, unknown>): UserRecord {
  return {
    id: String(row.id),
    email: String(row.email),
    name: String(row.name),
    provider: String(row.provider),
    token: row.token === null ? null : String(row.token),
    createdAt: new Date(String(row.created_at)),
    updatedAt: new Date(String(row.updated_at))
  };
}

export async function registerLocalUser(input: RegisterLocalUserInput): Promise<UserRecord> {
  const client = await pool.connect();

  try {
    await client.query("BEGIN");

    const existingResult = await client.query(
      `SELECT id FROM users WHERE provider = $1 AND email = $2`,
      ["local", input.email]
    );

    if (existingResult.rowCount && existingResult.rowCount > 0) {
      throw new Error("A local user with that email already exists.");
    }

    const userId = randomUUID();

    const userResult = await client.query(
      `
        INSERT INTO users (id, email, name, provider, token)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, email, name, provider, token, created_at, updated_at
      `,
      [userId, input.email, input.name, "local", null]
    );

    await client.query(
      `
        INSERT INTO user_credentials (user_id, password_hash)
        VALUES ($1, $2)
      `,
      [userId, input.passwordHash]
    );

    await client.query("COMMIT");

    return mapUserRecord(userResult.rows[0] as Record<string, unknown>);
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    client.release();
  }
}

export async function findLocalAuthUserByEmail(email: string): Promise<LocalAuthUser | null> {
  const result = await pool.query(
    `
      SELECT
        u.id,
        u.email,
        u.name,
        u.provider,
        u.token,
        u.created_at,
        u.updated_at,
        c.password_hash
      FROM users u
      INNER JOIN user_credentials c ON c.user_id = u.id
      WHERE u.provider = $1 AND u.email = $2
    `,
    ["local", email]
  );

  if (result.rowCount === 0) {
    return null;
  }

  const row = result.rows[0] as Record<string, unknown>;
  return {
    ...mapUserRecord(row),
    passwordHash: String(row.password_hash)
  };
}

export async function listUsers(): Promise<UserRecord[]> {
  const result = await pool.query(
    `
      SELECT id, email, name, provider, token, created_at, updated_at
      FROM users
      ORDER BY created_at ASC
    `
  );

  return result.rows.map((row: Record<string, unknown>) => mapUserRecord(row));
}
