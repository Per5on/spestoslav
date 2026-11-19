import { api } from "../api";

export type MerchantDirectoryEntry = {
  id: string;
  category_code: string;
  retailer_code: string;
  retailer_name: string;
  locality_id: string;
  locality_name: string;
  municipality: string | null;
  region: string | null;
  branch_name: string | null;
  address: string;
};

/** Load bounded pages from verified branch records, never synthetic merchants. */
export async function loadMerchantDirectory(signal?: AbortSignal): Promise<MerchantDirectoryEntry[]> {
  const pageSize = 100;
  const maximumPages = 100;
  const result: MerchantDirectoryEntry[] = [];
  const seen = new Set<string>();
  for (let page = 0; page < maximumPages; page += 1) {
    const rows = await api<MerchantDirectoryEntry[]>(
      `/api/v1/merchant-directory?limit=${pageSize}&offset=${page * pageSize}`,
      { signal },
    );
    for (const row of rows) {
      if (seen.has(row.id)) continue;
      seen.add(row.id);
      result.push(row);
    }
    if (rows.length < pageSize) return result;
  }
  throw new Error("Merchant directory exceeded the supported page limit");
}

export type MerchantLocalityGroup = {
  locality_id: string;
  locality_name: string;
  municipality: string | null;
  region: string | null;
  branches: MerchantDirectoryEntry[];
};
export type MerchantCategoryGroup = {
  category_code: string;
  localities: MerchantLocalityGroup[];
};

/** Group by canonical IDs rather than ambiguous locality display names. */
export function groupMerchantDirectory(rows: MerchantDirectoryEntry[]): MerchantCategoryGroup[] {
  const categories = new Map<string, Map<string, MerchantLocalityGroup>>();
  for (const row of rows) {
    let localities = categories.get(row.category_code);
    if (!localities) {
      localities = new Map();
      categories.set(row.category_code, localities);
    }
    let locality = localities.get(row.locality_id);
    if (!locality) {
      locality = {
        locality_id: row.locality_id,
        locality_name: row.locality_name,
        municipality: row.municipality,
        region: row.region,
        branches: [],
      };
      localities.set(row.locality_id, locality);
    }
    locality.branches.push(row);
  }
  const compare = (a: string, b: string) => a.localeCompare(b, "bg");
  return [...categories].sort(([a], [b]) => compare(a, b)).map(([category_code, localities]) => ({
    category_code,
    localities: [...localities.values()]
      .sort((a, b) => compare(a.locality_name, b.locality_name) || compare(a.locality_id, b.locality_id))
      .map((locality) => ({
        ...locality,
        branches: locality.branches.sort(
          (a, b) => compare(a.retailer_name, b.retailer_name) ||
            compare(a.address, b.address) ||
            compare(a.id, b.id),
        ),
      })),
  }));
}
