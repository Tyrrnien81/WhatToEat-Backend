import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { Writable } from "node:stream";
import { closePool, pool } from "./db";
import { listUsers } from "./auth/userRepository";
import { loginWithPassword, registerWithPassword } from "./auth/authService";

type MenuAction = "1" | "2" | "3" | "4";

class MutedOutput extends Writable {
  private muted = false;

  unmute(): void {
    this.muted = false;
  }

  mute(): void {
    this.muted = true;
  }

  override _write(
    chunk: string | Buffer,
    encoding: BufferEncoding,
    callback: (error?: Error | null) => void
  ): void {
    const text = typeof chunk === "string" ? chunk : chunk.toString("utf8");

    if (!this.muted || text.includes("\n") || text.includes("\r")) {
      output.write(text);
    }

    callback();
  }
}

function createInterface(): {
  rl: readline.Interface;
  mutedOutput: MutedOutput;
} {
  const mutedOutput = new MutedOutput();
  const rl = readline.createInterface({
    input,
    output: mutedOutput,
    terminal: true
  });

  return { rl, mutedOutput };
}

async function ask(rl: readline.Interface, mutedOutput: MutedOutput, question: string): Promise<string> {
  mutedOutput.unmute();
  return rl.question(question);
}

async function askHidden(rl: readline.Interface, mutedOutput: MutedOutput, question: string): Promise<string> {
  mutedOutput.unmute();
  output.write(question);
  mutedOutput.mute();

  try {
    return await rl.question("");
  } finally {
    mutedOutput.unmute();
    output.write("\n");
  }
}

async function ensureDbConnection(): Promise<void> {
  await pool.query("SELECT 1");
}

function printMenu(): void {
  console.log("\n=== WhatToEat Auth CLI ===");
  console.log("1. Register local user");
  console.log("2. Login local user");
  console.log("3. List users");
  console.log("4. Exit");
}

async function handleRegister(rl: readline.Interface, mutedOutput: MutedOutput): Promise<void> {
  const name = await ask(rl, mutedOutput, "Name: ");
  const email = await ask(rl, mutedOutput, "Email: ");
  const password = await askHidden(rl, mutedOutput, "Password: ");
  const user = await registerWithPassword(name, email, password);
  console.log("\nUser registered successfully.");
  console.log(JSON.stringify(user, null, 2));
}

async function handleLogin(rl: readline.Interface, mutedOutput: MutedOutput): Promise<void> {
  const email = await ask(rl, mutedOutput, "Email: ");
  const password = await askHidden(rl, mutedOutput, "Password: ");
  const result = await loginWithPassword(email, password);
  console.log("\nLogin succeeded.");
  console.log(JSON.stringify(result, null, 2));
}

async function handleListUsers(): Promise<void> {
  const users = await listUsers();
  console.log("\nRegistered users:");
  console.log(JSON.stringify(users, null, 2));
}

async function main(): Promise<void> {
  await ensureDbConnection();
  const { rl, mutedOutput } = createInterface();

  try {
    while (true) {
      printMenu();
      const action = (await ask(rl, mutedOutput, "Choose an option: ")).trim() as MenuAction;

      if (action === "1") {
        await handleRegister(rl, mutedOutput);
      } else if (action === "2") {
        await handleLogin(rl, mutedOutput);
      } else if (action === "3") {
        await handleListUsers();
      } else if (action === "4") {
        console.log("Exiting Auth CLI.");
        break;
      } else {
        console.log("Invalid option. Please choose 1, 2, 3, or 4.");
      }
    }
  } finally {
    rl.close();
    await closePool();
  }
}

main().catch(async (error: unknown) => {
  const message = error instanceof Error ? error.message : "Unknown error";
  console.error(`Failed to run Auth CLI: ${message}`);
  await closePool();
  process.exitCode = 1;
});
