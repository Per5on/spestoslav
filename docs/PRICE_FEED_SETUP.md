# Enable recurring production prices

Set up the restricted database login, add the two repository settings, and run the read-only check before activating the schedule. The current deployment uses Neon project `long-resonance-77491878`, branch `preview` (`br-snowy-morning-baym8iw6`), database `bgprices`. The live API is `https://spestoslav-api.onrender.com`. [Production PR](https://github.com/Per5on/spestoslav/pull/28)

## 1. Create the restricted Neon login

1. Open the [Neon console](https://console.neon.tech/), select the existing project and its `preview` branch, then open **SQL Editor**. Select database `bgprices` and a database administrator role.
2. Run `SELECT current_database();` and confirm the result is `bgprices`. Generate a unique, strong password in your password manager. If the role already exists, use the existing dedicated login and check its grants before continuing.
3. Replace the password placeholder locally in the SQL Editor. Use SQL to create the login and give it read access to the catalogue tables and insert access to the published-offer table.

```sql
CREATE ROLE spestovnik_price_publisher
  LOGIN PASSWORD 'REPLACE_WITH_YOUR_GENERATED_PASSWORD';

GRANT CONNECT ON DATABASE bgprices TO spestovnik_price_publisher;
GRANT USAGE ON SCHEMA public TO spestovnik_price_publisher;

GRANT SELECT ON TABLE
  public.grocery_catalog_identities,
  public.technology_catalog_identities,
  public.products,
  public.catalog_retailers,
  public.national_offers
TO spestovnik_price_publisher;

GRANT INSERT ON TABLE public.national_offers TO spestovnik_price_publisher;
```

4. In the Neon project dashboard, click **Connect**. Select branch `preview`, database `bgprices`, and role `spestovnik_price_publisher`. Copy the connection URL with its SSL parameters. If the role is missing from the menu, verify it in `pg_roles` on `preview`. The SQL-created role was present with `rolcanlogin = true` while the menu only showed the owner. Use the `preview` hostname, database and saved publisher password to assemble the URL locally.

   ```text
   postgresql://spestovnik_price_publisher:URL_ENCODED_PASSWORD@YOUR_NEON_HOST/bgprices?sslmode=require
   ```

   Percent-encode special characters in the password portion if you assemble the URL. Keep the full URL in your password manager and the GitHub secret. [Neon role and connection guide](https://neon.com/docs/manage/roles)

## 2. Add the GitHub Actions settings

Open **Settings → Secrets and variables → Actions** in `Per5on/spestoslav`. Create the entries at repository level. [Repository Actions settings](https://github.com/Per5on/spestoslav/settings/secrets/actions)

| Tab | Name | Value |
| --- | --- | --- |
| **Secrets → New repository secret** | `PRICE_PUBLISH_DATABASE_URL` | The URL for `spestovnik_price_publisher` from step 1 |
| **Variables → New repository variable** | `PRICE_REUSE_APPROVED_CATEGORIES` | `groceries technology` |

Enter the categories with one space and no quotes. This enables the verified product categories. Fuel has a separate source verification step. The public API URL already has the correct default. [GitHub secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets) · [GitHub variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables)

## 3. Run the read-only configuration check

1. Go to **Actions → Daily price source checks → Run workflow**.
2. Choose branch `fix/production-price-publication-20261127` and select **Check the production publisher configuration with a read-only query**. If the checkbox does not appear, run the same check with GitHub CLI.

   ```bash
   gh workflow run daily-price-checks.yml --repo Per5on/spestoslav --ref fix/production-price-publication-20261127 -f verify_publication=true
   ```

3. Open the **publication-config** job. Look for a configured publisher connection, an exact `groceries technology` category value, INSERT privilege, three existing pilot retailers and a registered BulMag. The job prints statuses and counts. [Successful preflight](https://github.com/Per5on/spestoslav/actions/runs/45963801361)

## 4. Activate the schedule and verify publication

1. Once the preflight and CI pass, mark [PR 28](https://github.com/Per5on/spestoslav/pull/28) **Ready for review** and merge it into `main`.
2. Go to **Actions → Refresh published prices → Run workflow** and select `main`. The recurring schedule runs every four hours after the merge.
3. Open the run and verify green **Refresh approved categories and report coverage** and **Verify production comparisons** steps. The `price-comparison-report` artifact should show `ok: true` and at least one comparable product for each product category. The exact offer counts can vary with retailer availability. Confirm that a later scheduled run republishes offers before they expire. [Actions runs](https://github.com/Per5on/spestoslav/actions) · [Live grocery offers](https://spestoslav-api.onrender.com/api/v1/national-offers?category_code=groceries) · [Live technology offers](https://spestoslav-api.onrender.com/api/v1/national-offers?category_code=technology)

A run link is enough to share for verification. APK packaging has separate approval.
