# Plan: Monetyzacja family-recipes (Stripe)

**Status:** `verification needed` — Faza B smoke 12/12 OK (2026-08-03); opcjonalnie ręczne Checkout kartą testową  
**Data:** 2026-08-03  
**Kontekst:** Kolejka monetyzacji (meta `.docs/stripe-status.md`) — family-recipes jako #1. Limity członków free/basic/pro już egzekwowane lokalnie; Stripe **test** włączony na VPS.

## Decyzje produktowe (zaakceptowane 2026-08-03)

1. **Płaci family owner** — rola `owner` w `family_memberships`, **nie** mylić z systemową rolą usera (`user` / `admin` / `owner`).
2. **Paywall:**
   - Limity członków (jak dziś): Free 2 / Basic 5 / Pro bez limitu.
   - **Płatny plan** → limitowany dostęp do AI na **systemowym** tokenie OpenRouter z `.env`.
   - **Free** → AI tylko BYOK (własny klucz OpenRouter).
   - **Keep export** → free na wszystkich planach (bez bramki planowej).
3. **Waluta / interwały:** PLN; od razu **miesiąc + rok** (~17% rabatu rocznego).

## Ceny (zaakceptowane)

| Plan | Miesiąc | Rok | Efektywnie / mies. |
|------|--------:|----:|-------------------:|
| Free | 0 | 0 | 0 |
| Basic | **9,99 zł** | **99 zł** | ~8,25 zł |
| Pro | **14,99 zł** | **149 zł** | ~12,40 zł |

### Limity AI (systemowy klucz, per rodzina / miesiąc)

| Plan | Budżet | Uwagi |
|------|--------|-------|
| Free | 0 USD | tylko BYOK |
| Basic | ~**0,50 USD** | „spróbuj AI” (import przepisów itd.) |
| Pro | ~**2 USD** | spokojne użycie rodzinne |

Egzekwowanie limitu AI: **per rodzina** (płaci owner; benefit dla całej rodziny).

## Model rozliczeniowy

```
Family owner (membership.role = owner)
  → Stripe Customer + Subscription (Checkout)
  → webhook aktualizuje Family.plan (free | basic | pro)
  → limity członków + AI entitlement z Family.plan
```

- Członkowie (`member`) **nie** otwierają Checkout / Customer Portal.
- Subskrypcja Stripe może nadal być powiązana z `user_id` ownera (wzorzec gear-stack), ale **źródło prawdy planu produktu** = `families.plan`.
- Po anulowaniu / past_due: downgrade `Family.plan` → `free` (polityka grace period — do doprecyzowania przy implementacji; default: jak gear-stack / koniec okresu).

## Mapowanie Stripe

Utworzyć w Stripe (najpierw **test**, potem **live**) Products + Prices:

| Stripe Price | `plan_tier` | Interval | Kwota |
|--------------|-------------|----------|------:|
| Basic monthly | `basic` | month | 9,99 PLN |
| Basic annual | `basic` | year | 99 PLN |
| Pro monthly | `pro` | month | 14,99 PLN |
| Pro annual | `pro` | year | 149 PLN |

Env (zamiast gear-stack `pro` / `pro_plus`):

```
STRIPE_BASIC_MONTHLY_PRICE_ID=
STRIPE_BASIC_ANNUAL_PRICE_ID=
STRIPE_PRO_MONTHLY_PRICE_ID=
STRIPE_PRO_ANNUAL_PRICE_ID=
```

Webhook: `price_id` → `basic` | `pro` → zapis do `families.plan` (oraz opcjonalnie mirror w `subscriptions.plan_tier` dla ownera).

## Luki vs obecny kod (do zrobienia)

| Obszar | Stan dziś | Cel |
|--------|-----------|-----|
| FE plany | `free/basic/pro`, ceny mock `$5/$10` | PLN 9,99 / 14,99 + rok |
| BE billing | `free/pro/pro_plus` (gear-stack) | `free/basic/pro` + price IDs Basic/Pro |
| Checkout | dowolny zalogowany user | tylko **family owner** |
| Plan produktu | `families.plan` (ręczne / seed) | sync z webhooków Stripe |
| AI access | rola `isPremium` / admin / system owner **lub** BYOK | `Family.plan ∈ {basic,pro}` → system key + limit USD; Free → BYOK |
| Keep | bez bramki planowej | bez zmian (zostaje free) |
| UI copy | Pro obiecuje AI; banner tylko o członkach | Basic/Pro: członkowie + AI; Keep nie jako premium |

## Fazy wdrożenia

### Faza A — produkt + kod (bez live keys) — `in progress`

- [x] Przepiąć billing BE/FE: tiers `basic`/`pro`, env price IDs, waluta display PLN.
- [x] Checkout + portal: guard `membership.role == owner`.
- [x] Webhooki: aktualizacja `families.plan` przy create/update/delete subskrypcji.
- [x] AI: entitlement z planu rodziny + limity ~0,50 / ~2 USD; Free = BYOK.
- [x] Zaktualizować UI planów, banner upgrade, i18n PL/EN.
- [x] Testy BE (checkout, limits) — `test_billing_service.py`.
- [x] Migracja `003` — tabele billing + plan_tier free/basic/pro.

### Faza B — Stripe test na VPS — `done` (2026-08-03)

- [x] Products/Prices w Stripe **test** (PLN).
- [x] Klucze test + webhook endpoint + price IDs w `.env`.
- [x] `STRIPE_ENABLED=true` (+ recreate kontenera; `VITE_STRIPE_ENABLED=true`).
- [x] Deploy FE na `/var/www/family-recipes` (2026-08-03).
- [x] Smoke API (12/12): owner checkout basic/pro × month/year → Stripe URL; member checkout/portal 403; free invite limit; AI free=403 / basic≠403; `families.plan` sync up/down.
- [x] Meta: `.docs/stripe-status.md` → 🧪 test.

**Poza smoke automatycznym:** pełna płatność kartą testową w Checkout UI + live webhook delivery z Dashboard (opcjonalna weryfikacja ręczna).

### Faza C — live — `todo`

- [ ] Te same Prices w Stripe **live**.
- [ ] Podmiana kluczy live + webhook live.
- [ ] Meta: `.docs/stripe-status.md` → ✅ live.

## Poza scope (na teraz)

- Stripe Tax / VAT display (osobna decyzja przed live B2C PL).
- Proration UX, trial, kody promo (Stripe pozwala `allow_promotion_codes` — opcjonalnie później).
- AI metering UI dla rodziny (wystarczy twardy limit + komunikat).
- Płatność przez membera / split billing.

## Referencje

- [README.md](../../README.md) §12 — limity członków
- [CLAUDE.md](../../CLAUDE.md) — `STRIPE_ENABLED=true` (test)
- Meta: [`.docs/stripe-status.md`](../../../.docs/stripe-status.md)
- Wzorzec: `gear-stack` billing (Checkout + webhooki + portal) — **adaptacja** pod family owner + `basic`/`pro` PLN
