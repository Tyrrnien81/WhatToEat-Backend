import { issueAccessToken } from "./jwt";
import { hashPassword, verifyPassword } from "./password";
import {
  findLocalAuthUserByEmail,
  registerLocalUser,
  type UserRecord
} from "./userRepository";

export interface LoginResult {
  accessToken: string;
  user: UserRecord;
}

export async function registerWithPassword(name: string, email: string, password: string): Promise<UserRecord> {
  const normalizedEmail = email.trim().toLowerCase();
  const passwordHash = await hashPassword(password);

  return registerLocalUser({
    name: name.trim(),
    email: normalizedEmail,
    passwordHash
  });
}

export async function loginWithPassword(email: string, password: string): Promise<LoginResult> {
  const normalizedEmail = email.trim().toLowerCase();
  const user = await findLocalAuthUserByEmail(normalizedEmail);

  if (!user) {
    throw new Error("User not found.");
  }

  const isValid = await verifyPassword(password, user.passwordHash);
  if (!isValid) {
    throw new Error("Invalid password.");
  }

  return {
    accessToken: issueAccessToken({
      sub: user.id,
      email: user.email,
      provider: user.provider
    }),
    user
  };
}
