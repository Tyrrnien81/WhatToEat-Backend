import jwt from "jsonwebtoken";
import { config } from "../config";

export interface AuthTokenPayload {
  sub: string;
  email: string;
  provider: string;
}

export function issueAccessToken(payload: AuthTokenPayload): string {
  return jwt.sign(payload, config.jwtSecret, {
    expiresIn: config.jwtExpiresIn as jwt.SignOptions["expiresIn"]
  });
}
