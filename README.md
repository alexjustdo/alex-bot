# Alex — Telegram AI Asistentka

## Čo potrebujete
- Telegram účet
- Anthropic API kľúč (https://console.anthropic.com)
- GitHub účet (zadarmo)
- Railway účet (zadarmo) — https://railway.app

---

## Krok 1 — Vytvorte Telegram bota

1. Otvorte Telegram a nájdite **@BotFather**
2. Napíšte `/newbot`
3. Zadajte meno bota, napr. `Alex Asistentka`
4. Zadajte username, napr. `alex_moja_bot`
5. BotFather vám pošle **TOKEN** — uložte si ho!

---

## Krok 2 — Nahrajte kód na GitHub

1. Vytvorte nový repozitár na https://github.com/new
2. Nahrajte všetky tri súbory: `bot.py`, `requirements.txt`, `railway.toml`

---

## Krok 3 — Spustite na Railway

1. Choďte na https://railway.app a prihláste sa cez GitHub
2. Kliknite **New Project → Deploy from GitHub repo**
3. Vyberte váš repozitár
4. Choďte do **Variables** a pridajte:

```
TELEGRAM_TOKEN = váš_token_od_botfathera
ANTHROPIC_API_KEY = váš_anthropic_kľúč
```

5. Railway automaticky spustí bota

---

## Hotovo!

Otvorte Telegram, nájdite svojho bota a napíšte `/start`.

## Príkazy bota
- `/start` — Privítanie a reštart
- `/reset` — Vymazanie histórie konverzácie
- `/help` — Zoznam funkcií
