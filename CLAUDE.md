# CLAUDE.md — Jørgen Østergaards jobsøgningsside

Læses automatisk af Claude Code i dette repo. Alt her gælder uanset hvilken Claude-konto der arbejdes fra.

## Hvad det er

Personlig one-page jobsøgningsside, live på **https://ostergaardjorgen.github.io/**.
Repo: `ostergaardjorgen/ostergaardjorgen.github.io` — GitHub Pages bygger direkte fra `main`.

Positionering: **specialist i identitet & adgangsstyring (IAM) og sikkerhed**, understøttet af AI og IT-ledelse. Søger Product Manager / IAM-lead — interim eller fast.

## Filer

| Fil | Rolle |
|---|---|
| `index.html` | Hele sitet i én fil — CSS og JS indlejret, ingen build, ingen eksterne afhængigheder |
| `build_cv.py` | Genererer CV-PDF'erne **direkte fra `index.html`** |
| `Jorgen-Ostergaard-cv-dk.pdf` / `-en.pdf` | Genereret — rediger aldrig i hånden |
| `manifest.webmanifest`, `icon-*.png`, `apple-touch-icon.png` | PWA / installér-på-hjemmeskærm |
| `qr-linkedin.svg` | QR til LinkedIn-profilen i kontaktsektionen |
| `foto.jpg` | Portræt (bruges af både site og CV) |

## Faste regler

1. **Dansk ⇒ engelsk, altid.** Dansk er kildetekst i markup'en (`data-i18n="nøgle"`), engelsk ligger i `var EN = {…}` i scriptet nederst. Enhver dansk rettelse skal have sin engelske i *samme* commit. Spørg ikke — gør det.
2. **Tjek nøgledækning før commit:** alle `data-i18n`-nøgler i HTML skal findes i `EN`, og omvendt. Både *missing* og *unused* skal være tomme.
3. **Bump versionen ved hver release.** Fodnoten viser `Version 0.xx` — hæv med 0.01 pr. push der ændrer sitet. Commit-subject starter med samme version: `v0.19: <tekst>`.
4. **Genbyg CV'et efter tekstændringer:** `py -3 build_cv.py`. Så kan site og CV aldrig drive fra hinanden.
5. **Led aldrig med CEO-titlen.** Intet "Former CEO" eller "efter otte år som CEO" som åbning — det læses som snobbet og som en udfordrer til den ansættende leder. Led med faget og årene; produktejerskabet er pointen, ikke rangen. Titlen må stå i selve ID Connect-posten.
6. **Rigtige æ ø å** i al synlig tekst. Filnavne må være ASCII (`Jorgen-Ostergaard-…`).
7. **Fire fagområder à præcis 6 punkter.** Ulige antal efterlader et hul i to-kolonne-gitteret.
8. **Mailadressen står aldrig synligt** på siden — kun kontaktformularen (FormSubmit, captcha slået til). QR og LinkedIn-knap er de øvrige kontaktveje.

## Verifikation før "færdig"

```bash
node --check <udtrukket script>          # JS-syntaks
gh api repos/ostergaardjorgen/ostergaardjorgen.github.io/pages/builds --jq '.[0] | "\(.status) \(.commit[0:7])"'
```

**Meld først live når Pages-buildet står `built` på det rigtige commit.** At spørge selve sitet giver falske positiver fra CDN-cache — det er sket.

## Kendte faldgruber

- Scriptet skal ligge **efter** bundnavigationen i DOM'en, ellers finder faneskiftet ingen faner.
- Preview-ruden i Claude-desktop kører ikke scripts på lokale filer — test sprogskift og faner på det live site.
- `.gitattributes` markerer PDF og billeder som binære. Fjern det ikke; linjeskift-konvertering ødelægger PDF'er.
- Pages-builds tager normalt under et minut, men har taget over ti.

## Privatliv

Ingen cookies, ingen analytics, ingen tredjeparts-ressourcer ved læsning. `localStorage` rummer kun `lang`. Formulardata går via FormSubmit (tredjepart) — det er oplyst i sektionen "Privatliv og cookies" og i noten under Send-knappen. **Intet cookiebanner** — der er intet samtykkekrævende at spørge om.

## Kom i gang på en ny maskine eller konto

```bash
gh auth login
git clone https://github.com/ostergaardjorgen/ostergaardjorgen.github.io.git "C:\ClaudeCode\Online CV"
py -3 -m pip install reportlab pillow pypdf
```

Node.js bruges kun til `node --check`.

## Ikke i dette repo

Repoet er **offentligt**. Ansøgninger, målrettede CV'er og cover letters til konkrete stillinger hører ikke hjemme her — de indeholder hvem der er søgt hos og navne på tredjepersoner.
