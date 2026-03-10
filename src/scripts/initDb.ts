import { readFile } from "node:fs/promises";
import path from "node:path";
import { closePool, pool } from "../db";

async function main(): Promise<void> {
  const sqlPath = path.resolve(__dirname, "../../sql/init.sql");
  const sql = await readFile(sqlPath, "utf8");

  await pool.query(sql);
  console.log("Database initialization completed.");
}

main().catch(async (error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown error";
  console.error(`Failed to initialize database: ${message}`);
  process.exitCode = 1;
}).finally(async () => {
  await closePool();
});
