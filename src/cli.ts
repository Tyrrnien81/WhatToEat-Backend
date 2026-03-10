import readline from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { closePool, pool } from "./db";
import { listUsers } from "./auth/userRepository";
import { loginWithPassword, registerWithPassword } from "./auth/authService";

type MenuAction = "1" | "2" | "3" | "4";

function createInterface() {
  return readline.createInterface({ input, output });
}

async function askHidden(question: string): Promise<string> {
  return new Promise((resolve) => {
    const mutableOutput = {
      write(chunk: string) {
        if (chunk.includes("\n") || chunk.includes("\r")) {
          output.write(chunk);
        } else {
          output.write("*");
        }
      }
    };

    const rl = readline.createInterface({ input, output: mutableOutput as typeof output, terminal: true });
    rl.question(question).then((answer) => {
      rl.close();
      output.write("\n");
      resolve(answer);
    });
  });
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

async function handleRegister(): Promise<void> {
  const rl = createInterface();
  try {
    const name = await rl.question("Name: ");
    const email = await rl.question("Email: ");
    rl.close();

    const password = await askHidden("Password: ");
    const user = await registerWithPassword(name, email, password);
    console.log("\nUser registered successfully.");
    console.log(JSON.stringify(user, null, 2));
  } finally {
    rl.close();
  }
}

async function handleLogin(): Promise<void> {
  const rl = createInterface();
  try {
    const email = await rl.question("Email: ");
    rl.close();

    const password = await askHidden("Password: ");
    const result = await loginWithPassword(email, password);
    console.log("\nLogin succeeded.");
    console.log(JSON.stringify(result, null, 2));
  } finally {
    rl.close();
  }
}

async function handleListUsers(): Promise<void> {
  const users = await listUsers();
  console.log("\nRegistered users:");
  console.log(JSON.stringify(users, null, 2));
}

async function main(): Promise<void> {
  await ensureDbConnection();
  const rl = createInterface();

  try {
    while (true) {
      printMenu();
      const action = (await rl.question("Choose an option: ")).trim() as MenuAction;

      if (action === "1") {
        await handleRegister();
      } else if (action === "2") {
        await handleLogin();
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
