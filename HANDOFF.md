# Sail in Spain — Booking module handoff

## Bestand
`booking.html` — standalone HTML/CSS/JS bestand, geen build-stap nodig. Gewoon openen in de browser om te testen.

## Wat het is
Een 3-staps boekingswizard (Trip → Details → Confirm) die de live widget op
`https://rentacatamaran.net/catamaran-booking-costa-del-sol.html` 1:1 namaakt qua
lay-out, kleuren en prijslogica, met twee bewuste verschillen:

1. **Lettertype**: eigen sans-serif stack (`-apple-system, BlinkMacSystemFont,
   'Segoe UI', Roboto, sans-serif`) in plaats van hun Cormorant Garamond/Inter.
2. **Backend**: stuurt naar ons eigen Google Apps Script endpoint (zie
   `SCRIPT_URL` in het `<script>`-blok onderaan `booking.html`), niet naar hun
   Zapier-webhooks.

Recentste wijziging: de "Book your Trip"-knop in de header is verwijderd en de
hele widget is compacter gemaakt (kleinere hero, paddings, fonts) zodat stap 1 +
prijssamenvatting op één scherm passen zonder te scrollen.

## Prijslogica (CHARTER_RULES in het script)
Volledige tabel voor 1–7 dagen + halve dag/sunset, met seizoenen (low/mid/
start-end/high), automatische capaciteitslimieten per chartertype (10 / 6 / 4
personen), en een "manual review"-vlag voor charters van 4+ dagen (verwijst
naar `alegria@sailinspain.be`). Deze tabel is exact overgenomen van de live
widget — niet zelf verzinnen, wijzig hier alleen in overleg.

## Backend / spreadsheet
- Endpoint: Google Apps Script Web App URL (staat in `SCRIPT_URL`), schrijft
  naar een Google Sheet "Boekingen" en stuurt een mailtje naar
  `backoffice@investinspain.be`.
- Script-broncode staat in `google-apps-script.js` in deze repo.
- Payload-velden: `name, email, phone, port, tripType, guests, dateFrom,
  dateTo, base, crew, fuel, total, notes, additional`.

## Repo's / deployment
Er zijn **twee losstaande GitHub-repo's** in scope, wees hier expliciet over
naar de gebruiker als dit ooit verwarrend is:

1. `InvestinspainBackoffice/sailinspain-boeking-intake` — deze werkrepo
   (intake/dev), bestand: `booking.html`.
2. `InvestinspainBackoffice/sailinspain-booking` — de repo die **Vercel
   production** deployt (`sailinspain-booking-livid.vercel.app`), bestand:
   `index.html`. Bij een release moet dezelfde inhoud naar **beide** repo's
   gepusht worden (in repo 2 als `index.html`, niet `booking.html`).

Beide repo's staan gesynchroniseerd op de compacte versie zonder "Book your
Trip"-knop (laatste commits: intake-repo `05d6f6f`, productie-repo `f9a4591`).

## Openstaande/mogelijke vervolgstappen
- Eventueel de site-header (logo/nav) helemaal weglaten als dit puur als
  embedded widget gebruikt gaat worden i.p.v. standalone pagina.
