# Migration checklist

- [ ] Enumerate legacy backend endpoints and DTOs.
- [ ] Inspect every Flyway migration and map the live schema.
- [ ] Inspect Neon project `bg-prices-preview` read-only.
- [ ] Identify Render services in the confirmed workspace.
- [ ] Export and validate products, retailers, branches and price records.
- [ ] Separate demo data from verified price observations.
- [x] Create dedicated GitHub repository `Per5on/spestoslav`.
- [ ] Add mobile/backend CI and tests.
- [ ] Implement four category screens and shared settlement selection.
- [ ] Add authentication, submissions, moderation and price collection.
- [ ] Create an isolated Neon development branch before schema work.
- [ ] Configure Render Blueprint after service topology review.
