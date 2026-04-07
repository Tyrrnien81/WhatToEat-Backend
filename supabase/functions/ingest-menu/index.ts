/**
 * Supabase Edge Function: `ingest-menu`
 *
 * Deploy: `supabase functions deploy ingest-menu`
 *
 * Secrets: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, TARGET_MENU_API_BASE
 * Optional: INGEST_WEEK_LOOKAHEAD (default 2)
 * Optional: INGEST_SKIP_WEEK_COVERAGE — `weekdays` (default): skip only when Mon–Fri all have
 *   snapshots; `full`: skip only when all 7 days Mon–Sun have snapshots; `none`: never skip
 *   (always fetch). Avoids skipping a week when Mon–Thu exist but Fri is still missing.
 *
 * Use `npm:` (pinned) — Supabase Edge resolves it reliably; combine with `awaitSb` so we never
 * read `.error` off an undefined response.
 */

import { createClient } from "npm:@supabase/supabase-js@2.49.4";

type Json = Record<string, unknown>;
type SupabaseLike = any;

const RESTAURANTS: Record<string, { id: number; name: string }> = {
  "carsons-market": { id: 45370, name: "Carson's Market" },
  "four-lakes-market": { id: 45371, name: "Four Lakes Market" },
  "gordon-avenue-market": { id: 45372, name: "Gordon Avenue Market" },
  "lizs-market": { id: 45373, name: "Liz's Market" },
  "lowell-market": { id: 45374, name: "Lowell Market" },
  "rhetas-market": { id: 45375, name: "Rheta's Market" },
};

const MEALS: Record<string, { id: number; name: string }> = {
  breakfast: { id: 14942, name: "Breakfast" },
  lunch: { id: 14943, name: "Lunch" },
  dinner: { id: 14944, name: "Dinner" },
};

const SKIP: Record<string, Set<string>> = {
  "carsons-market": new Set(["breakfast"]),
};

const CHUNK_SIZE = 500;
const DEFAULT_WEEK_LOOKAHEAD = 2;

const CORS_HEADERS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "authorization, x-client-info, apikey, content-type",
};

const JSON_HEADERS = {
  ...CORS_HEADERS,
  "content-type": "application/json",
};

type IngestRequestBody = {
  requestedDate?: string;
  triggerSource?: string;
};

function env(name: string): string {
  const v = Deno.env.get(name);
  if (!v) throw new Error(`Missing env: ${name}`);
  return v;
}

function envPositiveInt(name: string, fallback: number): number {
  const raw = Deno.env.get(name);
  if (!raw) return fallback;
  const n = Number(raw);
  return Number.isFinite(n) && n > 0 ? Math.floor(n) : fallback;
}

function isValidYmd(ymd: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(ymd)) return false;
  const dt = new Date(`${ymd}T00:00:00.000Z`);
  return !Number.isNaN(dt.getTime()) && dt.toISOString().slice(0, 10) === ymd;
}

type SbResult<T = unknown> = { data: T | null; error: { message: string } | null };

/**
 * Await a Supabase call and read `{ data, error }` without destructuring off `undefined`.
 * Also surfaces rejections as a clear Error (some failures happen before a result object exists).
 */
async function awaitSb<T = unknown>(
  label: string,
  pending: PromiseLike<unknown> | unknown,
): Promise<SbResult<T>> {
  let raw: unknown;
  try {
    raw = await Promise.resolve(pending);
  } catch (e) {
    throw new Error(`${label}: rejected — ${e instanceof Error ? e.message : String(e)}`);
  }
  if (raw == null || typeof raw !== "object") {
    throw new Error(
      `${label}: resolved to invalid value (${raw === null ? "null" : typeof raw}). Check @supabase/supabase-js import.`,
    );
  }
  const o = raw as Record<string, unknown>;
  const errVal = o["error"];
  let error: { message: string } | null = null;
  if (errVal != null && typeof errVal === "object" && "message" in errVal) {
    error = { message: String((errVal as { message: unknown }).message) };
  } else if (errVal != null) {
    error = { message: String(errVal) };
  }
  return { data: (o["data"] as T | null) ?? null, error };
}

function toNum(v: unknown): number | null {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

function ymdToApiPath(dateStr: string): string {
  return dateStr.replaceAll("-", "/");
}

/** Monday YYYY-MM-DD (UTC calendar math). */
function mondayOfWeekContaining(ymd: string): string {
  const [y, m, d] = ymd.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  const diff = (dt.getUTCDay() + 6) % 7;
  dt.setUTCDate(dt.getUTCDate() - diff);
  return dt.toISOString().slice(0, 10);
}

function addDaysYmd(ymd: string, days: number): string {
  const [y, m, d] = ymd.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() + days);
  return dt.toISOString().slice(0, 10);
}

/** Days to require before skipping the API fetch for this (restaurant, meal, week). */
function requiredDatesForSkip(
  weekMonday: string,
  mode: "weekdays" | "full",
): string[] {
  const n = mode === "full" ? 7 : 5;
  return Array.from({ length: n }, (_, i) => addDaysYmd(weekMonday, i));
}

function hasCoverageForSkip(
  dates: Set<string>,
  weekMonday: string,
  mode: "weekdays" | "full",
): boolean {
  for (const d of requiredDatesForSkip(weekMonday, mode)) {
    if (!dates.has(d)) return false;
  }
  return true;
}

async function loadSnapshotDatesInRange(
  supabase: SupabaseLike,
  rangeStart: string,
  rangeEnd: string,
): Promise<Map<string, Set<string>>> {
  const map = new Map<string, Set<string>>();
  const { data, error } = await awaitSb(
    "menu_snapshots coverage",
    supabase
      .from("menu_snapshots")
      .select("restaurant_id, meal_type_id, service_date")
      .gte("service_date", rangeStart)
      .lte("service_date", rangeEnd),
  ) as SbResult<Array<{ restaurant_id: number; meal_type_id: number; service_date: string }>>;
  if (error) throw new Error(`coverage query: ${error.message}`);
  for (const row of data ?? []) {
    const r = row.restaurant_id as number;
    const m = row.meal_type_id as number;
    const sd = String(row.service_date).slice(0, 10);
    const key = `${r}:${m}`;
    if (!map.has(key)) map.set(key, new Set());
    map.get(key)!.add(sd);
  }
  return map;
}

async function chunkedUpsert(
  supabase: SupabaseLike,
  table: string,
  rows: Json[],
  onConflict?: string,
) {
  if (!rows.length) return;
  for (let i = 0; i < rows.length; i += CHUNK_SIZE) {
    const chunk = rows.slice(i, i + CHUNK_SIZE);
    const { error } = await awaitSb(
      `upsert ${table}`,
      supabase.from(table).upsert(chunk, onConflict ? { onConflict } : undefined),
    );
    if (error) throw new Error(`upsert ${table}: ${error.message}`);
  }
}

async function chunkedInsert(
  supabase: SupabaseLike,
  table: string,
  rows: Json[],
) {
  if (!rows.length) return;
  for (let i = 0; i < rows.length; i += CHUNK_SIZE) {
    const chunk = rows.slice(i, i + CHUNK_SIZE);
    const { error } = await awaitSb(
      `insert ${table}`,
      supabase.from(table).insert(chunk),
    );
    if (error) throw new Error(`insert ${table}: ${error.message}`);
  }
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS_HEADERS });
  }

  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST only" }), {
      status: 405,
      headers: JSON_HEADERS,
    });
  }

  const parsed = await req.json().catch(() => ({}));
  if (parsed == null || typeof parsed !== "object" || Array.isArray(parsed)) {
    return new Response(
      JSON.stringify({
        ok: false,
        error: "Invalid JSON body. Expected an object like { requestedDate, triggerSource }.",
      }),
      { status: 400, headers: JSON_HEADERS },
    );
  }

  const body = parsed as Record<string, unknown>;
  const allowedKeys = new Set(["requestedDate", "triggerSource"]);
  const unknownKeys = Object.keys(body).filter((k) => !allowedKeys.has(k));
  if (unknownKeys.length > 0) {
    return new Response(
      JSON.stringify({
        ok: false,
        error:
          `Unsupported body key(s): ${unknownKeys.join(", ")}. ` +
          "Use only requestedDate and triggerSource.",
      }),
      { status: 400, headers: JSON_HEADERS },
    );
  }

  if (
    body.requestedDate !== undefined &&
    typeof body.requestedDate !== "string"
  ) {
    return new Response(
      JSON.stringify({
        ok: false,
        error: "requestedDate must be a string in YYYY-MM-DD format.",
      }),
      { status: 400, headers: JSON_HEADERS },
    );
  }

  if (
    body.triggerSource !== undefined &&
    typeof body.triggerSource !== "string"
  ) {
    return new Response(
      JSON.stringify({
        ok: false,
        error: "triggerSource must be a string.",
      }),
      { status: 400, headers: JSON_HEADERS },
    );
  }

  if (typeof createClient !== "function") {
    throw new Error("createClient is missing — @supabase/supabase-js did not load");
  }
  const supabase = createClient(env("SUPABASE_URL"), env("SUPABASE_SERVICE_ROLE_KEY"), {
    auth: { persistSession: false },
    global: { fetch },
  });
  if (typeof supabase?.from !== "function" || typeof supabase?.rpc !== "function") {
    throw new Error("createClient returned an invalid client (missing .from / .rpc)");
  }
  const baseUrl = env("TARGET_MENU_API_BASE").replace(/\/+$/, "");

  let runId: number | null = null;
  let triggerSource = "manual";
  let requestedDate = new Date().toISOString().slice(0, 10);

  let requestsTotal = 0;
  let daysWithMenuTotal = 0;
  let rowsTouched = 0;
  let errorCount = 0;
  let skippedFetches = 0;
  const pairErrors: Array<{ pair: string; error: string }> = [];

  try {
    const body = parsed as IngestRequestBody;

    if (body.triggerSource) triggerSource = body.triggerSource;
    if (body.requestedDate) {
      if (!isValidYmd(body.requestedDate)) {
        return new Response(
          JSON.stringify({
            ok: false,
            error: `Invalid requestedDate '${body.requestedDate}'. Use YYYY-MM-DD.`,
          }),
          { status: 400, headers: JSON_HEADERS },
        );
      }
      requestedDate = body.requestedDate;
    }

    const weekLookahead = envPositiveInt("INGEST_WEEK_LOOKAHEAD", DEFAULT_WEEK_LOOKAHEAD);
    const skipCoverageRaw = (Deno.env.get("INGEST_SKIP_WEEK_COVERAGE") ?? "weekdays")
      .toLowerCase();
    const skipWeekCoverage: "none" | "weekdays" | "full" =
      skipCoverageRaw === "full"
        ? "full"
        : skipCoverageRaw === "none"
        ? "none"
        : "weekdays";

    const baseMonday = mondayOfWeekContaining(requestedDate);
    const weekAnchors: string[] = [];
    for (let w = 0; w < weekLookahead; w++) {
      weekAnchors.push(addDaysYmd(baseMonday, w * 7));
    }

    const marketsTotal = Object.keys(RESTAURANTS).length;
    const mealPairsTotal = Object.keys(RESTAURANTS).flatMap((slug) =>
      Object.keys(MEALS)
        .filter((m) => !SKIP[slug]?.has(m))
        .map((m) => `${slug}/${m}`)
    ).length;
    const plannedUnits = weekAnchors.length * mealPairsTotal;

    const { data: beginData, error: beginErr } = await awaitSb(
      "begin_ingest_run",
      supabase.rpc("begin_ingest_run", {
        p_trigger_source: triggerSource,
        p_requested_date: requestedDate,
        p_markets_total: marketsTotal,
        p_meals_total: plannedUnits,
        p_details: {
          requestedDate,
          weekAnchors,
          skipWeekCoverage,
          startedBy: "edge-function",
        },
      }),
    );
    if (beginErr) throw new Error(`begin_ingest_run failed: ${beginErr.message}`);
    if (beginData == null || beginData === "") {
      throw new Error("begin_ingest_run returned no run id (data empty)");
    }
    runId = Number(beginData);
    if (!Number.isFinite(runId)) {
      throw new Error(`begin_ingest_run returned non-numeric id: ${String(beginData)}`);
    }

    await chunkedUpsert(
      supabase,
      "restaurants",
      Object.values(RESTAURANTS).map((r) => ({
        external_restaurant_id: r.id,
        name: r.name,
      })),
      "external_restaurant_id",
    );
    rowsTouched += Object.keys(RESTAURANTS).length;

    await chunkedUpsert(
      supabase,
      "meal_types",
      Object.values(MEALS).map((m) => ({
        external_meal_type_id: m.id,
        name: m.name,
      })),
      "external_meal_type_id",
    );
    rowsTouched += Object.keys(MEALS).length;

    const { data: dbRestaurants, error: reErr } = await awaitSb<
      Array<{ id: number; external_restaurant_id: number }>
    >(
      "restaurants select",
      supabase.from("restaurants").select("id, external_restaurant_id"),
    );
    if (reErr) throw new Error(reErr.message);

    const { data: dbMeals, error: meErr } = await awaitSb<
      Array<{ id: number; external_meal_type_id: number }>
    >(
      "meal_types select",
      supabase.from("meal_types").select("id, external_meal_type_id"),
    );
    if (meErr) throw new Error(meErr.message);

    const restaurantIdByExternal = new Map<number, number>(
      (dbRestaurants ?? []).map((r: { external_restaurant_id: number; id: number }) => [
        r.external_restaurant_id,
        r.id,
      ]),
    );
    const mealTypeIdByExternal = new Map<number, number>(
      (dbMeals ?? []).map((m: { external_meal_type_id: number; id: number }) => [
        m.external_meal_type_id,
        m.id,
      ]),
    );

    const globalStart = weekAnchors[0];
    const globalEnd = addDaysYmd(weekAnchors[weekAnchors.length - 1], 6);
    const coverage = await loadSnapshotDatesInRange(supabase, globalStart, globalEnd);

    for (const anchorYmd of weekAnchors) {
      for (const [slug, rMeta] of Object.entries(RESTAURANTS)) {
        for (const [meal, mMeta] of Object.entries(MEALS)) {
          if (SKIP[slug]?.has(meal)) continue;

          const pair = `${slug}/${meal}@${anchorYmd}`;

          const restaurantId = restaurantIdByExternal.get(rMeta.id);
          const mealTypeId = mealTypeIdByExternal.get(mMeta.id);
          if (!restaurantId || !mealTypeId) {
            errorCount += 1;
            pairErrors.push({
              pair,
              error: "Missing internal restaurant/meal_type id mapping",
            });
            continue;
          }

          const covKey = `${restaurantId}:${mealTypeId}`;
          let dates = coverage.get(covKey) ?? new Set<string>();
          if (
            skipWeekCoverage !== "none" &&
            hasCoverageForSkip(dates, anchorYmd, skipWeekCoverage)
          ) {
            skippedFetches += 1;
            continue;
          }

          requestsTotal += 1;

          try {
            const apiUrl =
              `${baseUrl}/${slug}/menu-type/${meal}/${ymdToApiPath(anchorYmd)}/`;
            const resp = await fetch(apiUrl, { method: "GET" });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

            const raw = await resp.json();
            const days = Array.isArray(raw?.days) ? raw.days : [];
            const exportedAt = raw?.last_updated ?? null;

            for (const day of days) {
              const serviceDate = day?.date as string | undefined;
              const menuItems = Array.isArray(day?.menu_items) ? day.menu_items : [];
              if (!serviceDate || menuItems.length === 0) continue;

              daysWithMenuTotal += 1;

              await chunkedUpsert(
                supabase,
                "menu_snapshots",
                [{
                  restaurant_id: restaurantId,
                  meal_type_id: mealTypeId,
                  service_date: serviceDate,
                  exported_at: exportedAt,
                }],
                "restaurant_id,meal_type_id,service_date",
              );
              rowsTouched += 1;

              const { data: snapRows, error: snapErr } = await awaitSb(
                "menu_snapshots snapshot lookup",
                supabase
                  .from("menu_snapshots")
                  .select("id")
                  .eq("restaurant_id", restaurantId)
                  .eq("meal_type_id", mealTypeId)
                  .eq("service_date", serviceDate)
                  .limit(1),
              ) as SbResult<Array<{ id: number }>>;
              if (snapErr || !snapRows?.length) {
                throw new Error(`snapshot lookup failed: ${snapErr?.message ?? "not found"}`);
              }
              const snapshotId = snapRows[0].id as number;

              const sdKey = serviceDate.slice(0, 10);
              if (!coverage.has(covKey)) coverage.set(covKey, new Set());
              coverage.get(covKey)!.add(sdKey);

              const menuInfo = (day?.menu_info ?? {}) as Record<string, unknown>;
              const sectionRows: Json[] = [];
              for (const [extMenuIdStr, info] of Object.entries(menuInfo)) {
                const extMenuId = Number(extMenuIdStr);
                if (!Number.isFinite(extMenuId)) continue;

                const inf = info as {
                  section_options?: { display_name?: string };
                  position?: unknown;
                };
                sectionRows.push({
                  snapshot_id: snapshotId,
                  external_menu_id: extMenuId,
                  display_name: inf?.section_options?.display_name ?? "Section",
                  position: toNum(inf?.position) ?? 0,
                });
              }

              await chunkedUpsert(
                supabase,
                "menu_sections",
                sectionRows,
                "snapshot_id,external_menu_id",
              );
              rowsTouched += sectionRows.length;

              const { data: sectionMapRows, error: secErr } = await awaitSb(
                "menu_sections select",
                supabase
                  .from("menu_sections")
                  .select("id, external_menu_id")
                  .eq("snapshot_id", snapshotId),
              ) as SbResult<Array<{ id: number; external_menu_id: number }>>;
              if (secErr) throw new Error(`menu_sections select failed: ${secErr.message}`);

              const sectionIdByExternalMenu = new Map<number, number>(
                (sectionMapRows ?? []).map((s: { external_menu_id: number; id: number }) => [
                  s.external_menu_id,
                  s.id,
                ]),
              );
              const sectionIds = (sectionMapRows ?? []).map((s: { id: number }) => s.id as number);

              const foodRowsByExtId = new Map<number, Json>();
              const nutritionByExtId = new Map<number, Json>();
              const iconRowsByExtId = new Map<number, Json>();
              const iconAssigns = new Set<string>();
              const itemTemp: Array<{
                sectionId: number;
                extFoodId: number | null;
                external_menu_item_id: number | null;
                food_variation_id: number | null;
                position: number;
                station_name: string | null;
                category: string | null;
                price: number | null;
                serving_size_amount: string | null;
                serving_size_unit: string | null;
              }> = [];

              let currentStation: string | null = null;

              for (const item of menuItems) {
                if (item?.is_station_header) {
                  currentStation = item?.text ?? null;
                  continue;
                }

                const food = item?.food;
                if (!food?.id) continue;
                const extFoodId = Number(food.id);
                if (!Number.isFinite(extFoodId)) continue;

                const srv = food?.serving_size_info ?? {};
                if (!foodRowsByExtId.has(extFoodId)) {
                  foodRowsByExtId.set(extFoodId, {
                    external_food_id: extFoodId,
                    name: food?.name ?? "Unknown",
                    description: food?.description ?? null,
                    food_category: food?.food_category ?? null,
                    price: toNum(food?.price),
                    ingredients: food?.ingredients ?? null,
                    serving_size_amount:
                      srv?.serving_size_amount != null ? String(srv.serving_size_amount) : null,
                    serving_size_unit:
                      srv?.serving_size_unit != null ? String(srv.serving_size_unit) : null,
                  });
                }

                const nutr = food?.rounded_nutrition_info;
                if (nutr) nutritionByExtId.set(extFoodId, nutr);

                const icons = food?.icons?.food_icons ?? [];
                for (const ic of icons) {
                  const extIconId = Number(ic?.id);
                  if (!Number.isFinite(extIconId)) continue;

                  if (!iconRowsByExtId.has(extIconId)) {
                    iconRowsByExtId.set(extIconId, {
                      external_icon_id: extIconId,
                      name: ic?.name ?? "icon",
                      slug: ic?.slug ?? `icon-${extIconId}`,
                      icon_type: toNum(ic?.type) ?? 1,
                      behavior: toNum(ic?.behavior) ?? 1,
                      is_filter: Boolean(ic?.is_filter),
                      is_highlight: Boolean(ic?.is_highlight),
                      sort_order: toNum(ic?.sort_order) ?? 0,
                    });
                  }
                  iconAssigns.add(`${extFoodId}:${extIconId}`);
                }

                const extMenuId = toNum(item?.menu_id);
                if (extMenuId == null) continue;
                const sectionId = sectionIdByExternalMenu.get(extMenuId);
                if (!sectionId) continue;

                itemTemp.push({
                  sectionId,
                  extFoodId,
                  external_menu_item_id: toNum(item?.id),
                  food_variation_id: toNum(item?.food_variation_id),
                  position: toNum(item?.position) ?? 0,
                  station_name: currentStation,
                  category: item?.category ?? null,
                  price: toNum(item?.price),
                  serving_size_amount:
                    item?.serving_size_amount != null ? String(item.serving_size_amount) : null,
                  serving_size_unit:
                    item?.serving_size_unit != null ? String(item.serving_size_unit) : null,
                });
              }

              const foodRows = [...foodRowsByExtId.values()];
              await chunkedUpsert(supabase, "foods", foodRows, "external_food_id");
              rowsTouched += foodRows.length;

              const extFoodIds = [...foodRowsByExtId.keys()];
              let foodIdByExt = new Map<number, number>();
              if (extFoodIds.length) {
                const { data: fRows, error: fErr } = await awaitSb(
                  "foods select",
                  supabase
                    .from("foods")
                    .select("id, external_food_id")
                    .in("external_food_id", extFoodIds),
                ) as SbResult<Array<{ id: number; external_food_id: number }>>;
                if (fErr) throw new Error(`foods select failed: ${fErr.message}`);
                foodIdByExt = new Map(
                  (fRows ?? []).map((f: { external_food_id: number; id: number }) => [
                    f.external_food_id,
                    f.id,
                  ]),
                );
              }

              const nutrRows: Json[] = [];
              for (const [extFoodId, nutr] of nutritionByExtId.entries()) {
                const foodId = foodIdByExt.get(extFoodId);
                if (!foodId) continue;
                const n = nutr as Record<string, unknown>;
                nutrRows.push({
                  food_id: foodId,
                  calories: toNum(n?.calories),
                  g_fat: toNum(n?.g_fat),
                  g_saturated_fat: toNum(n?.g_saturated_fat),
                  g_trans_fat: toNum(n?.g_trans_fat),
                  mg_cholesterol: toNum(n?.mg_cholesterol),
                  g_carbs: toNum(n?.g_carbs),
                  g_added_sugar: toNum(n?.g_added_sugar),
                  g_sugar: toNum(n?.g_sugar),
                  mg_potassium: toNum(n?.mg_potassium),
                  mg_sodium: toNum(n?.mg_sodium),
                  g_fiber: toNum(n?.g_fiber),
                  g_protein: toNum(n?.g_protein),
                  mg_iron: toNum(n?.mg_iron),
                  mg_calcium: toNum(n?.mg_calcium),
                  mg_vitamin_c: toNum(n?.mg_vitamin_c),
                  iu_vitamin_a: toNum(n?.iu_vitamin_a),
                  re_vitamin_a: toNum(n?.re_vitamin_a),
                  mcg_vitamin_a: toNum(n?.mcg_vitamin_a),
                  mg_vitamin_d: toNum(n?.mg_vitamin_d),
                  mcg_vitamin_d: toNum(n?.mcg_vitamin_d),
                });
              }
              await chunkedUpsert(supabase, "food_nutrition", nutrRows, "food_id");
              rowsTouched += nutrRows.length;

              const iconRows = [...iconRowsByExtId.values()];
              await chunkedUpsert(supabase, "food_icons", iconRows, "external_icon_id");
              rowsTouched += iconRows.length;

              const extIconIds = [...iconRowsByExtId.keys()];
              let iconIdByExt = new Map<number, number>();
              if (extIconIds.length) {
                const { data: iRows, error: iErr } = await awaitSb(
                  "food_icons select",
                  supabase
                    .from("food_icons")
                    .select("id, external_icon_id")
                    .in("external_icon_id", extIconIds),
                ) as SbResult<Array<{ id: number; external_icon_id: number }>>;
                if (iErr) throw new Error(`food_icons select failed: ${iErr.message}`);
                iconIdByExt = new Map(
                  (iRows ?? []).map((i: { external_icon_id: number; id: number }) => [
                    i.external_icon_id,
                    i.id,
                  ]),
                );
              }

              const assignRows: Json[] = [];
              for (const pairKey of iconAssigns) {
                const [ef, ei] = pairKey.split(":").map(Number);
                const foodId = foodIdByExt.get(ef);
                const iconId = iconIdByExt.get(ei);
                if (!foodId || !iconId) continue;
                assignRows.push({ food_id: foodId, icon_id: iconId });
              }
              await chunkedUpsert(supabase, "food_icon_assignments", assignRows, "food_id,icon_id");
              rowsTouched += assignRows.length;

              if (sectionIds.length) {
                const { error: delErr } = await awaitSb(
                  "menu_section_items delete",
                  supabase.from("menu_section_items").delete().in("section_id", sectionIds),
                );
                if (delErr) throw new Error(`delete menu_section_items failed: ${delErr.message}`);
              }

              const msiRows: Json[] = [];
              for (const it of itemTemp) {
                const foodId = it.extFoodId ? foodIdByExt.get(it.extFoodId) ?? null : null;
                msiRows.push({
                  section_id: it.sectionId,
                  food_id: foodId,
                  external_menu_item_id: it.external_menu_item_id,
                  food_variation_id: it.food_variation_id,
                  position: it.position,
                  station_name: it.station_name,
                  category: it.category,
                  price: it.price,
                  serving_size_amount: it.serving_size_amount,
                  serving_size_unit: it.serving_size_unit,
                });
              }
              await chunkedInsert(supabase, "menu_section_items", msiRows);
              rowsTouched += msiRows.length;
            }
          } catch (e) {
            errorCount += 1;
            pairErrors.push({ pair, error: e instanceof Error ? e.message : String(e) });
          }
        }
      }
    }

    const status = errorCount === 0 ? "success" : "partial";

    const { error: finishErr } = await awaitSb(
      "finish_ingest_run",
      supabase.rpc("finish_ingest_run", {
        p_run_id: runId,
        p_status: status,
        p_requests_total: requestsTotal,
        p_files_or_days_total: daysWithMenuTotal,
        p_rows_upserted_total: rowsTouched,
        p_error_count: errorCount,
        p_error_message: errorCount ? `${errorCount} pair(s) failed` : null,
        p_details: {
          requestedDate,
          weekAnchors,
          skipWeekCoverage,
          skippedFetches,
          pairErrors,
        },
      }),
    );
    if (finishErr) throw new Error(`finish_ingest_run failed: ${finishErr.message}`);

    return new Response(
      JSON.stringify({
        ok: true,
        runId,
        status,
        requestedDate,
        weekAnchors,
        skipWeekCoverage,
        skippedFetches,
        requestsTotal,
        daysWithMenuTotal,
        rowsTouched,
        errorCount,
        pairErrors,
      }),
      { status: 200, headers: JSON_HEADERS },
    );
  } catch (e) {
    const message = e instanceof Error ? e.message : String(e);

    if (runId != null) {
      try {
        const { error: finErr } = await awaitSb(
          "finish_ingest_run (failure path)",
          supabase.rpc("finish_ingest_run", {
            p_run_id: runId,
            p_status: "failed",
            p_requests_total: requestsTotal,
            p_files_or_days_total: daysWithMenuTotal,
            p_rows_upserted_total: rowsTouched,
            p_error_count: errorCount + 1,
            p_error_message: message,
            p_details: { requestedDate, pairErrors, fatal: message },
          }),
        );
        if (finErr) {
          console.error("finish_ingest_run (failure path) RPC error:", finErr.message);
        }
      } catch (e) {
        console.error("finish_ingest_run (failure path) threw:", e);
      }
    }

    return new Response(JSON.stringify({ ok: false, error: message, runId }), {
      status: 500,
      headers: JSON_HEADERS,
    });
  }
});
