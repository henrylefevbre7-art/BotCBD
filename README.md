# BotCBD

Bot Telegram pour diriger les utilisateurs vers une boutique WebApp et g?rer la r?ception des commandes. Le bot repose sur `python-telegram-bot` v20 et n?cessite plusieurs variables d'environnement pour fonctionner correctement.

## Configuration

Avant de lancer le bot, d?finissez les variables d'environnement suivantes?:

- `TELEGRAM_BOT_TOKEN` ? Token du bot (obtenu aupr?s de BotFather).
- `TELEGRAM_ADMIN_ID` ? Identifiant num?rique Telegram de l'administrateur qui re?oit les commandes.
- `TELEGRAM_WEB_APP_URL` ? URL HTTPS de la mini-app. Un slash final est automatiquement ajout? si n?cessaire.
- `TELEGRAM_CHANNEL_URL` ? Lien vers le canal Telegram associ?.
- `TELEGRAM_CONTACT_USERNAME` ? Nom d'utilisateur du support (sans `@`).

Vous pouvez les d?finir en ligne de commande?:

```bash
export TELEGRAM_BOT_TOKEN="8329422168:AAHxxYoB2GeDk_UVKoQoBJo6TiPdBnsQfiE"
export TELEGRAM_ADMIN_ID="7534164397"
export TELEGRAM_WEB_APP_URL="https://votre-mini-app.example/"   # ? renseigner d?s que disponible
export TELEGRAM_CHANNEL_URL="https://t.me/+TUar__WdjbE4ZmY0"
export TELEGRAM_CONTACT_USERNAME="PuffLabz"
```

## Installation

```bash
pip install -r requirements.txt
```

## Ex?cution

```bash
python3 bot.py
```

Le bot d?marre en mode polling et configure automatiquement le bouton de menu WebApp. Surveillez les logs pour v?rifier la bonne prise en compte des commandes envoy?es par la mini-app.