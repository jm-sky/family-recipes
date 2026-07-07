# Plan: Natywny look & feel na mobile (ścieżka Android)

**Status:** `in progress`  
**Data:** 2026-07-07  
**Zaktualizowano:** 2026-07-07  
**Kontekst:** Aplikacja ma wyjść na Androida (PWA → Capacitor). Obecny UI to desktop-first shell (sidebar + header + karty w kartach) — na telefonie czuć „stronę adminową w przeglądarce”, nie aplikację sklepową.

## Cel

Użytkownik na telefonie ma czuć, że korzysta z **aplikacji do list zakupów i przepisów**, a nie z responsywnej wersji panelu webowego. Zmiany w webie mają być kompatybilne z późniejszym opakowaniem w Capacitor — **jedna baza kodu**, bez forkowania layoutów per platforma.

## Stan obecny — co psuje „native feel”

| Obszar | Stan | Wpływ na UX mobile |
|--------|------|-------------------|
| Nawigacja | Hamburger → `Sheet` z bocznym menu (`AppSidebar`) | Ukryte sekcje, 2 tapnięcia do przełączenia modułu |
| Chrome | Stały `AppHeader` (logo, locale, dark mode, avatar) + `AppFooter` z linkami prawnymi | Zajmuje ~25–30% ekranu; footer nie ma sensu w apce |
| Layout treści | `AuthenticatedLayout`: gradient tło + `border rounded-xl shadow-lg` karta w `max-w-7xl` | Wizualnie „dashboard SaaS”, nie full-screen lista |
| Listy zakupów | Wiersze w `border rounded-md` + mały checkbox + ikona kosza | Małe targety dotykowe; brak swipe; brak „list item” feel |
| Akcje destrukcyjne | `window.confirm()` (`ShoppingListsPage`) | Natychmiastowy sygnał „to nie apka” |
| Dodawanie produktu | Panel inline w `Card` (chipy + search) | OK kierunek, ale brak bottom sheet / FAB jak w Listonic/Domownik |
| Safe area | Brak `viewport-fit=cover`, brak `env(safe-area-inset-*)` | Na Androidzie z gesture bar / notch treść przyklejona do krawędzi |
| Gestury | Brak pull-to-refresh, brak swipe-back | Brak oczekiwanego zachowania systemowego |
| Typografia / motion | shadcn/reka defaults, hover stany | Hover na touch; animacje „web dialog”, nie „screen transition” |
| Breakpoint | `768px` = mobile (`SidebarProvider`) | Tablet też dostaje hamburger zamiast sensownego split view |

**Pliki referencyjne:** `AuthenticatedLayout.vue`, `AppHeader.vue`, `AppSidebar.vue`, `ShoppingListPage.vue`, `ShoppingListsPage.vue`, `ProductAddPanel.vue`.

## Kierunek wizualny — Material 3 (Android) jako north star

Nie kopiujemy pixel-perfect Material You, ale **mapujemy wzorce**:

## Desktop bez zmian

Obecny layout **nie jest wyrzucany**. `AuthenticatedLayout` rozgałęzia shell według breakpointu; treść modułów (`<slot />`) i logika biznesowa zostają wspólne.

| Viewport | Shell |
|----------|--------|
| `md+` (desktop / tablet szeroki) | Sidebar + header + footer + karta treści — jak dziś |
| `< md` (mobile) | Top app bar + bottom nav, bez footera i outer card |

Admin, billing, ustawienia, tabele — nadal w desktopowym chrome. Mobile shell dotyczy głównie codziennego użycia (zakupy, rodzina, przepisy).

---

- **Navigation bar** (dolny) — 3–4 główne destynacje zawsze widoczne
- **Top app bar** — tytuł ekranu, opcjonalnie back, akcje kontekstowe (max 2 ikony)
- **Full-bleed surfaces** — treść od krawędzi do krawędzi, bez zagnieżdżonych kart
- **List items** — min. 48×48 dp touch target, divider zamiast obramowania każdego wiersza
- **Bottom sheets** — dodawanie/edycja, potwierdzenia, filtry
- **FAB** (opcjonalnie) — główna akcja ekranu (np. nowa lista)
- **Snackbar** zamiast toastów dla akcji z undo

Paleta i tokeny: zachować obecny design system (Tailwind + shadcn), ale dodać warstwę **mobile tokens** (`--mobile-touch-min`, `--app-bar-height`, safe-area).

## Propozycja architektury UI

### 1. Mobile shell (`MobileAppShell`)

Nowy layout aktywowany przy `max-width: 768px` (lub `md:` breakpoint — do ustalenia):

```
┌─────────────────────────────┐
│  ←  Lista zakupów      ⋮    │  ← TopAppBar (sticky, safe-area-top)
├─────────────────────────────┤
│                             │
│   Treść full-bleed          │  ← bez outer Card, bez gradientu
│   (scroll)                  │
│                             │
│                      [+]    │  ← FAB (opcjonalnie, kontekstowo)
├─────────────────────────────┤
│  🏠   👨‍👩‍👧   📖   🛒         │  ← BottomNav (safe-area-bottom)
└─────────────────────────────┘
```

**Bottom nav — proponowane zakładki (4):**

| Tab | Route | Uwagi |
|-----|-------|-------|
| Start | `/dashboard` | Skróty: aktywna lista, ostatnie przepisy |
| Rodzina | `/family` | |
| Przepisy | `/recipes` | Placeholder OK w MVP |
| Zakupy | `/shopping` | Główny use case w sklepie |

Profil, ustawienia, billing, admin → **ekran konta** (avatar w TopAppBar lub 5. tab „Więcej» tylko jeśli konieczne — preferujemy 4 + menu overflow).

**Desktop:** bez zmian — sidebar + header (obecny `AuthenticatedLayout`).

Implementacja: `AuthenticatedLayout` deleguje do `DesktopShell` / `MobileShell` na podstawie `useMediaQuery`, wspólny `<slot />` treści.

### 2. Ekrany modułowe — wzorce per flow

#### Zakupy — lista list (`ShoppingListsPage`)

| Teraz | Propozycja mobile |
|-------|-------------------|
| Grid kart 2-kolumnowy | Pionowa lista `ListItem` (nazwa, progress, chevron) |
| Formularz inline „nowa lista” | FAB → bottom sheet z jednym polem + CTA |
| `window.confirm` przy usuwaniu | Bottom sheet „Usunąć listę?” + destructive button |
| Przycisk „Kategorie” w headerze strony | Akcja w TopAppBar (ikona tune) lub w overflow menu |

#### Zakupy — pojedyncza lista (`ShoppingListPage`)

| Teraz | Propozycja mobile |
|-------|-------------------|
| Link „wstecz” tekstowy | Systemowy back w TopAppBar (`router.back()`) |
| `ProductAddPanel` w Card na górze | **Sticky search bar** pod app barem LUB FAB „Dodaj” → full-height bottom sheet (jak Listonic) |
| Chipy sugestii | W bottom sheet: sekcja „Ostatnie” + „Popularne” + klawiatura od razu |
| Wiersz: checkbox + border box | `ListItem` pełnej szerokości, tap = toggle checked, **swipe left** = usuń (z undo snackbar) |
| **Long press** | Menu: edytuj ilość/jednostkę, przenieś kategorię |
| Progress | Pod tytułem — `LinearProgress` (cienki, bez ramki) |

To jest **najważniejszy ekran** — tu ROI z natywnego UX jest największy (użycie jedną ręką w sklepie).

#### Rodzina (`FamilyPage`)

- Lista członków jako `ListItem` z avatarami
- Zaproszenie → bottom sheet z linkiem + share sheet (Web Share API / Capacitor Share później)

#### Auth / onboarding

- Na mobile: bez dwukolumnowego `GuestLayoutTwoColumns` — już częściowo OK; upewnić się, że formularze mają `inputmode`, `autocomplete`, duże przyciski primary na dole ekranu (thumb zone)

### 3. Komponenty do dodania (shared)

| Komponent | Opis | Priorytet |
|-----------|------|-----------|
| `MobileShell` | TopBar + slot + BottomNav + safe areas | P0 |
| `TopAppBar` | Tytuł, back, actions slot | P0 |
| `BottomNav` | 4 taby, active state, haptic on tap (Capacitor) | P0 |
| `BottomSheet` | Wrapper na `Sheet` z `side="bottom"`, drag handle, snap points | P0 |
| `ListItem` / `ListGroup` | Divider, min-height 56px, ripple (CSS) | P0 |
| `SwipeableListItem` | vueuse gesture lub lekka lib; fallback: przycisk usuń widoczny | P1 |
| `ConfirmSheet` | Zamiennik `window.confirm` | P0 |
| `SnackbarAction` | Sonner z action „Cofnij” | P1 |
| `PullToRefresh` | Opcjonalnie na listach (TanStack Query `refetch`) | P2 |

Większość bazuje na istniejącym `Sheet` (reka-ui) — **nie nowa biblioteka UI**, tylko mobile-oriented composition.

### 4. Detale „native feel” (quick wins)

1. **Safe area:** `viewport-fit=cover` w `index.html` + paddingi `pb-[env(safe-area-inset-bottom)]` na BottomNav
2. **Touch targets:** min `size-11` (44px) na interaktywnych elementach; spacing między wierszami listy
3. **Wyłączyć hover-primary na mobile:** `@media (hover: none)` — brak hover scale na logo/linkach
4. **Ukryć footer** w `MobileShell` — linki prawne w Ustawienia → Informacje prawne
5. **Ukryć LocaleToggle / DarkModeToggle z headera** na mobile → Ustawienia (zostawić w systemie jeśli użytkownik woli)
6. **Page transitions:** `router-view` z lekkim slide (Vue transition + `prefers-reduced-motion`)
7. **Tap highlight:** `-webkit-tap-highlight-color: transparent` + własny ripple na ListItem
8. **Sticky elements:** search / progress przy scrollu listy zakupów
9. **Keyboard:** bottom sheet z `visualViewport` resize — pole input nad klawiaturą (ważne na Androidzie)

### 5. Ścieżka Android (PWA → Capacitor)

Zgodnie z [README.md](../../README.md):

| Faza | Co robimy | Native bonus |
|------|-----------|--------------|
| **A — Mobile web** | Mobile shell + bottom sheets + list patterns w Vue | Instalowalna PWA, offline (już jest SW) |
| **B — PWA polish** | manifest `display: standalone`, splash, theme-color per route, ikony adaptive | „Add to Home Screen” ≈ apka |
| **C — Capacitor** | `@capacitor/android`, StatusBar, NavigationBar, Haptics, Share, Back button | Systemowy back = `router.back()`, hardware back zamyka sheet |

**Zasada:** żadnej logiki biznesowej w warstwie native — tylko adaptery (`usePlatform()`, `useHaptics()`, `useAndroidBackButton()`).

## Fazy implementacji (szacunek)

### Faza 0 — Fundament shell (2–3 dni)

- [ ] `MobileShell`, `TopAppBar`, `BottomNav`
- [ ] `AuthenticatedLayout` — rozgałęzienie mobile/desktop
- [ ] Safe area + ukrycie footera na mobile
- [ ] `ConfirmSheet` + podmiana `window.confirm` w module shopping

**Kryterium akceptacji:** nawigacja między 4 modułami jednym kciukiem, bez otwierania sidebara.

### Faza 1 — Zakupy mobile-first (3–4 dni)

- [ ] `ShoppingListsPage` — lista native + FAB
- [ ] `ShoppingListPage` — ListItem, swipe delete, snackbar undo
- [ ] `ProductAddPanel` → bottom sheet (Faza D z [shopping-product-suggestions](2026-07-07-shopping-product-suggestions.md))
- [ ] Sticky progress + search

**Kryterium:** dodanie 5 produktów w sklepie ≤ 30 s, jedną ręką, bez scrollowania do góry.

### Faza 2 — Reszta modułów + polish (2–3 dni)

- [ ] Family, Dashboard — list patterns
- [ ] Page transitions, pull-to-refresh na listach
- [ ] Audit touch targets w auth/settings
- [ ] Testy e2e Playwright viewport mobile

### Faza 3 — Capacitor (osobny plan, ~2 dni)

- Spike: back button, status bar, build APK
- Nie blokuje Faz 0–2

## Makiety (ASCII)

### Bottom sheet — dodaj produkt

```
┌─────────────────────────────┐
│         ───                 │  drag handle
│  Dodaj produkt                │
├─────────────────────────────┤
│ 🔍 Szukaj…                   │
│ [Mleko] [Chleb] [Jajka]      │
│ ── Ostatnie ──               │
│ 🥛 Mleko 2%                  │
│ 🥖 Chleb                     │
│ ── Popularne ──              │
│ …                            │
├─────────────────────────────┤
│  [ Dodaj „własny produkt” ]  │
└─────────────────────────────┘
```

### Wiersz listy zakupów (swipe)

```
│ ☐  Mleko 2%           1 l   │  ← tap = check
│ ← swipe ──────────────────── │
│              [ Usuń ]        │
```

## Metryki sukcesu

- Czas dodania pozycji do listy (median) — baseline vs po Fazie 1
- Liczba tapnięć: otwarcie listy z dashboardu → pierwszy produkt dodany (cel: ≤ 4)
- Subiektywna ocena „czy to apka?” — mini test z 3–5 użytkownikami rodziny
- Brak regresji desktop (sidebar, tabele admina)

## Ryzyka i mitigacje

| Ryzyko | Mitygacja |
|--------|-----------|
| Dwa layouty do utrzymania | Jeden slot treści; różny tylko chrome; wspólne komponenty list |
| Swipe vs scroll konflikt | Swipe tylko na osi X z progiem; lub P1 bez swipe, sama ListItem |
| Bottom sheet + klawiatura | `visualViewport` API, test na prawdziwym Androidzie |
| Scope creep (Material pełna implementacja) | Tylko wzorce UX, nie migracja na Vuetify/MDI |

## Podjęte decyzje (2026-07-07)

| # | Pytanie | Decyzja |
|---|---------|---------|
| 1 | 4 taby vs 5 | **4 taby** — Start, Rodzina, Przepisy, Zakupy; profil/ustawienia/admin przez avatar lub overflow w `TopAppBar` |
| 2 | Tablet (768–1024px) | **Sidebar collapsible** — bez bottom nav; mobile shell tylko `< md` |
| 3 | `ProductAddPanel` | **FAB + bottom sheet** na mobile (Listonic-style); desktop bez zmian |
| 4 | Swipe delete | **P1** — po walidacji shella (Faza 0); nie blokuje pierwszego PR |
| 5 | Dark mode | **Wybór użytkownika** — toggle w ustawieniach, bez wymuszania `prefers-color-scheme` |
| 6 | Capacitor | **Po Fazie 1** — najpierw mobile web + walidacja z rodziną, potem spike APK |
| 7 | Benchmark | **Mix: Listonic (zakupy) + obecny design system** — wzorce UX dodawania produktów i list ze sklepu; shell Material-inspired, nie pixel-perfect Material You |

## Powiązane dokumenty

- [README.md](../../README.md) — strategia PWA / Capacitor
- [2026-07-07-shopping-product-suggestions.md](2026-07-07-shopping-product-suggestions.md) — bottom sheet w Fazie D
- [../research/2026-07-07-shopping-add-item-ux.md](../research/2026-07-07-shopping-add-item-ux.md) — benchmark Listonic
- [../reviews/2026-07-06-ux.md](../reviews/2026-07-06-ux.md) — checklist UX (responsive)

## Rekomendacja

Zacząć od **Fazy 0 + Faza 1** wyłącznie na module **Zakupy** — to główny scenariusz mobile i najszybsza ścieżka do „to już nie wygląda jak strona”. Reszta modułów dostaje ten sam shell, ale bez przebudowy treści do czasu walidacji z rodziną.
