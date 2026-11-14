# Frontend reference and confirmed decisions

Source material: user-uploaded `12.docx`, `app.docx`, the three-screen visual and piggy-bank logo supplied in this conversation. The documents contain historical conversations as well as requirements; old instructions to stop implementation do not override the current authorization to fix the backend. Historical CI/deployment statements are not current verification. Historical Kotlin/Spring references do not authorize rewriting the deployed FastAPI backend.

Latest explicit user decisions take precedence over conflicting text or picture details:

- Green header and orange selections, matching the image. This supersedes the paragraph in `12.docx` asking to invert the palette.
- Four category tabs, with a separate searchable location dropdown. The reference's three-tab arrangement is not the final navigation.
- Use the supplied piggy bank as the sample logo. The supplied artwork reads **Спестовник**; preserve that artwork rather than substituting the current pig emoji. Repository/service/package identifiers remain unchanged during backend work.
- Finish backend checks before starting frontend implementation. Existing Android UI remains unchanged in the backend PR.

Visual assets are preserved unmodified in `docs/references/app-visual-reference.png` and `docs/references/piggy-bank-logo.png`.

## Visual direction from the reference

Dark green header, white title, orange selected controls, white/light cards, compact product photos, retailer marks, prominent prices and smaller unit-price text. The grocery example has a product search dropdown with multiple product selections, clear/apply controls and a selected-count button. The fuel example has fuel-type filters, station names/addresses and update times. Treat all depicted prices and distances as illustrative, not live data or an authorization to add GPS.

## Functional requirements to carry forward

Four categories: Храни, Горива, Дом, Техника. Bulgarian default; English supported later. Android 10+ remains the stated target. No Plus tab is specified.

One shared location selection persists across categories. Searchable dropdown with mutually exclusive **Населено място** and **Пощ. код** modes, suggestions while typing, and municipality/region/postal details to distinguish same-name settlements. No OSM, current-location/GPS, radius, extra location instructions or the old “Сравнявай цени в EUR”/“Категории” subtitles. The kilometer badges in the illustration are not a GPS requirement. EUR is the recorded currency requirement; the illustration's лв. prices are not a currency specification.

Known barcode lookup; unknown-barcode identification requests; private receipt upload, OCR progress and review. Stores are real registered active branches linked to canonical localities, independent of whether they have prices. Display missing price coverage explicitly.

Product catalog and real thumbnails come from the backend. A separately enabled demo catalog provides three reference-product photos with `is_demo=true`, `verified=false` and no asserted price. Demo fixtures never enter verified price tables.

Physical-branch prices, national online offers, promotions and historical prices remain separate concepts. Fuelo is a third-party source, not an official retailer. API observations with unknown reported/estimated certainty must not be presented as verified station prices. The owner currently has no Fuelo API access.

## Backend handoff

See `BACKEND_READINESS.md` for implemented routes, validation and remaining rollout/configuration steps. Preserve the distinction between implemented, locally tested, CI verified and deployed when planning frontend work. Basket comparison and final screen interactions should be checked against the final frontend flow rather than inferred from illustrative prices.
