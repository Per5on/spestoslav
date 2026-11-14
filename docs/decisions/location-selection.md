# Location selection decision

**Decision: GPS is excluded from Спестослав.** There will be no device-location permission, GPS lookup, manual coordinate entry or radius-based search.

The app has one shared selected locality used by Храни, Горива, Дом and Техника. The selector is a searchable drop-down:
- Tap the location field to search.
- Type at least two characters of a Bulgarian or English settlement name, or a postal code where verified postal-code data is available.
- Select a result from the drop-down.
- Show municipality, region and postal code (when known) to distinguish settlements with similar names.
- The selected locality remains the same when switching category tabs.

## Reference interaction

The user specified https://avtogararuse.org/index.cgi. The page presents a route-search form with select controls labelled “Тръгва от” and “Пристига в”, followed by date and time controls. For Спестослав, use the clear, form-based selection pattern as a visual/interaction reference, adapted to one searchable settlement selector. Do not copy its route semantics or add a second destination field.

## Data requirements

- Search canonical Bulgarian settlement records, not only localities inferred from retailer branches.
- Postal codes are optional until imported from a reliable, validated source.
- OSM may supplement locality names and branch locations but is not a complete postal-code authority.
- Never auto-select a locality from the device's position.
