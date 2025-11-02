# bot.py
from dataclasses import dataclass
import json
import logging
import os
from typing import Any, Dict, List, Optional

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
    WebAppInfo,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ========== CONFIGURATION ==========


class ConfigError(RuntimeError):
    """Erreur levée lorsque la configuration est invalide."""


@dataclass(frozen=True)
class BotConfig:
    token: str
    admin_id: int
    web_app_url: str
    channel_url: str
    contact_username: str

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Construit la configuration du bot à partir des variables d'environnement."""

        def _require_env(name: str) -> str:
            value = os.getenv(name)
            if not value:
                raise ConfigError(
                    f"La variable d'environnement {name} est obligatoire pour démarrer le bot."
                )
            return value.strip()

        token = _require_env("TELEGRAM_BOT_TOKEN")

        raw_admin_id = _require_env("TELEGRAM_ADMIN_ID")
        try:
            admin_id = int(raw_admin_id)
        except ValueError as exc:
            raise ConfigError(
                "TELEGRAM_ADMIN_ID doit être un identifiant Telegram numérique valide."
            ) from exc
        if admin_id <= 0:
            raise ConfigError("TELEGRAM_ADMIN_ID doit être strictement positif.")

        web_app_raw = _require_env("TELEGRAM_WEB_APP_URL")
        if not web_app_raw.lower().startswith("https://"):
            raise ConfigError("TELEGRAM_WEB_APP_URL doit utiliser HTTPS.")
        web_app_url = _ensure_trailing_slash(web_app_raw)

        channel_url = _require_env("TELEGRAM_CHANNEL_URL")
        if not channel_url.startswith("http://") and not channel_url.startswith("https://"):
            raise ConfigError("TELEGRAM_CHANNEL_URL doit être une URL valide.")

        contact_username = _require_env("TELEGRAM_CONTACT_USERNAME").lstrip("@")
        if not contact_username:
            raise ConfigError("TELEGRAM_CONTACT_USERNAME ne peut pas être vide.")

        return cls(
            token=token,
            admin_id=admin_id,
            web_app_url=web_app_url,
            channel_url=channel_url,
            contact_username=contact_username,
        )


def _ensure_trailing_slash(url: str) -> str:
    return url if url.endswith("/") else f"{url}/"


def get_config(context: ContextTypes.DEFAULT_TYPE) -> BotConfig:
    config = context.bot_data.get("config")
    if not isinstance(config, BotConfig):
        raise ConfigError(
            "Configuration du bot introuvable dans le contexte. Assure-toi que main() l'a chargée."
        )
    return config

# ========== LOGGING ==========

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== TEXTES DES COMMANDES ==========

WELCOME_TEXT = (
    "🌿 *Bienvenue chez CBD Shop !*\n\n"
    "Découvrez notre sélection premium de :\n"
    "• 🌿 Cartouches CBD 1g\n"
    "• 💨 Disposables CBD 1g\n\n"
    "Produits de haute qualité, testés en laboratoire et conformes à la législation française.\n\n"
    "*Cliquez sur le bouton ci-dessous pour accéder à la boutique* 👇"
)

INFO_TEXT = (
    "ℹ️ *Informations CBD Shop*\n\n"
    "*Qui sommes-nous ?*\n"
    "Spécialistes du CBD depuis 2020, nous proposons des produits premium testés en laboratoire.\n\n"
    "*Nos produits :*\n"
    "🌿 Cartouches CBD 1g (35€)\n"
    "• Compatible batteries 510\n"
    "• CBD : 85-87%\n"
    "• THC < 0.2%\n\n"
    "💨 Disposables CBD 1g (30€)\n"
    "• Prêts à l’emploi\n"
    "• ~400 bouffées\n"
    "• Batterie intégrée\n\n"
    "*Qualité garantie :*\n"
    "✅ Lab testé\n"
    "✅ Sans THC (< 0.2%)\n"
    "✅ Arômes naturels\n"
    "✅ Fabriqué en France/Europe\n\n"
    "*Certification :*\n"
    "Tous nos produits sont conformes à la législation française et européenne."
)

LIVRAISON_TEXT = (
    "📦 *Informations Livraison*\n\n"
    "*Modes de livraison :*\n\n"
    "🚗 *Livraison Express (Paris & région)*\n"
    "• Délai : 2-4h\n"
    "• Prix : 10€\n"
    "• Disponible 7j/7\n\n"
    "📮 *Colissimo Suivi*\n"
    "• Délai : 24-48h\n"
    "• Prix : Gratuit dès 50€ (sinon 5€)\n"
    "• Toute la France\n\n"
    "📍 *Retrait en point relais*\n"
    "• Délai : 24-48h\n"
    "• Prix : 3€\n"
    "• Plus de 10 000 points relais\n\n"
    "*Colis discret :*\n"
    "Emballage neutre, sans mention du contenu.\n\n"
    "*Suivi de commande :*\n"
    "Vous recevez un numéro de suivi dès l’expédition.\n\n"
    "*Retours :*\n"
    "14 jours pour changer d’avis (produits non ouverts)."
)

CONTACT_TEXT_TEMPLATE = (
    "📞 *Nous Contacter*\n\n"
    "*Service Client :*\n"
    "Telegram : @{contact_username}\n"
    "Réponse sous 2h en moyenne\n\n"
    "*Horaires :*\n"
    "Lundi - Vendredi : 9h - 20h\n"
    "Samedi - Dimanche : 10h - 18h\n\n"
    "*Suivez-nous :*\n"
    "📢 Notre canal : {channel_url}\n"
    "Offres exclusives, nouveautés et promotions !\n\n"
    "*Questions fréquentes :*\n"
    "• Livraison : /livraison\n"
    "• Nos produits : /info\n"
    "• Boutique : /shop\n\n"
    "*Une question ? Une suggestion ?*\n"
    "N’hésitez pas à nous écrire directement !"
)


def render_contact_text(config: BotConfig) -> str:
    return CONTACT_TEXT_TEMPLATE.format(
        contact_username=config.contact_username,
        channel_url=config.channel_url,
    )


def main_menu_keyboard(config: BotConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🛍️ Accéder à la boutique",
                    web_app=WebAppInfo(url=config.web_app_url),
                )
            ],
            [
                InlineKeyboardButton("ℹ️ Informations", callback_data="info"),
                InlineKeyboardButton("📦 Livraison", callback_data="livraison"),
            ],
            [
                InlineKeyboardButton("📞 Contact", callback_data="contact"),
                InlineKeyboardButton("📢 Notre Canal", url=config.channel_url),
            ],
        ]
    )


def info_keyboard(config: BotConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🛍️ Voir la boutique",
                    web_app=WebAppInfo(url=config.web_app_url),
                )
            ],
            [InlineKeyboardButton("« Retour au menu", callback_data="menu")],
        ]
    )


def livraison_keyboard(config: BotConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🛍️ Commander maintenant",
                    web_app=WebAppInfo(url=config.web_app_url),
                )
            ],
            [InlineKeyboardButton("« Retour au menu", callback_data="menu")],
        ]
    )


def contact_keyboard(config: BotConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "💬 Envoyer un message",
                    url=f"https://t.me/{config.contact_username}",
                )
            ],
            [InlineKeyboardButton("📢 Rejoindre le canal", url=config.channel_url)],
            [InlineKeyboardButton("« Retour au menu", callback_data="menu")],
        ]
    )


def shop_keyboard(config: BotConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🛍️ Ouvrir la boutique",
                    web_app=WebAppInfo(url=config.web_app_url),
                )
            ]
        ]
    )


def support_keyboard(config: BotConfig) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📞 Contacter le support",
                    url=f"https://t.me/{config.contact_username}",
                )
            ]
        ]
    )


def _format_amount(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, (int, float)):
        formatted = f"{value:.2f}"
        if formatted.endswith(".00"):
            formatted = formatted[:-3]
        return f"{formatted}€"

    text = str(value).strip()
    return text if text.endswith("€") else f"{text}€"


def _extract_cart_lines(cart: Any) -> List[str]:
    if not isinstance(cart, list) or not cart:
        return ["- Aucun article fourni"]

    lines: List[str] = []
    for entry in cart:
        if isinstance(entry, dict):
            name = str(entry.get("title") or entry.get("name") or "Article")
            quantity = entry.get("quantity") or entry.get("qty")
            price = entry.get("price") or entry.get("amount")

            details: List[str] = []
            if quantity:
                details.append(f"x{quantity}")
            if price is not None:
                details.append(str(price))

            suffix = f" ({', '.join(details)})" if details else ""
            lines.append(f"- {name}{suffix}")
        else:
            lines.append(f"- {entry}")

    return lines


def build_admin_order_message(
    update: Update,
    order_data: Dict[str, Any],
    cart_lines: List[str],
    cart_count: int,
    config: BotConfig,
) -> str:
    user = update.effective_user
    total = order_data.get("total")
    total_label = _format_amount(total)
    cart_summary = "\n".join(cart_lines)

    username = f"@{user.username}" if user and user.username else "—"
    full_name = user.full_name if user else "Utilisateur inconnu"
    user_id = user.id if user else "?"

    raw_payload = json.dumps(order_data, indent=2, ensure_ascii=False)

    parts = [
        "🛒 Nouvelle commande reçue",
        f"Client : {full_name} (ID: {user_id})",
        f"Username : {username}",
        f"Total : {total_label}",
        f"Articles : {cart_count}",
        cart_summary,
    ]

    comment = order_data.get("message") or order_data.get("notes")
    if comment:
        parts.extend(["", "Commentaire :", str(comment)])

    parts.extend(["", "Données brutes :", raw_payload])

    return "\n".join(parts)


def build_user_confirmation_message(total: Any, cart_count: int) -> str:
    total_label = _format_amount(total)
    return (
        "✅ *Commande reçue !*\n\n"
        f"Montant total : *{total_label}*\n"
        f"Nombre d'articles : *{cart_count}*\n\n"
        "📱 Vous serez contacté rapidement pour finaliser votre commande.\n\n"
        "Merci de votre confiance ! 🌿"
    )


# ========== COMMANDES ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start - Message de bienvenue"""
    message = update.effective_message
    if message is None:
        logger.warning("Commande /start reçue sans message associé.")
        return

    config = get_config(context)

    await message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_keyboard(config),
        parse_mode=ParseMode.MARKDOWN,
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /info"""
    message = update.effective_message
    if message is None:
        logger.warning("Commande /info reçue sans message associé.")
        return

    config = get_config(context)

    await message.reply_text(
        INFO_TEXT,
        reply_markup=info_keyboard(config),
        parse_mode=ParseMode.MARKDOWN,
    )

async def livraison_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /livraison"""
    message = update.effective_message
    if message is None:
        logger.warning("Commande /livraison reçue sans message associé.")
        return

    config = get_config(context)

    await message.reply_text(
        LIVRAISON_TEXT,
        reply_markup=livraison_keyboard(config),
        parse_mode=ParseMode.MARKDOWN,
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /contact"""
    message = update.effective_message
    if message is None:
        logger.warning("Commande /contact reçue sans message associé.")
        return

    config = get_config(context)

    await message.reply_text(
        render_contact_text(config),
        reply_markup=contact_keyboard(config),
        parse_mode=ParseMode.MARKDOWN,
    )

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /shop - Ouvrir la boutique"""
    message = update.effective_message
    if message is None:
        logger.warning("Commande /shop reçue sans message associé.")
        return

    config = get_config(context)

    await message.reply_text(
        "🌿 Cliquez sur le bouton ci-dessous pour accéder à notre boutique :",
        reply_markup=shop_keyboard(config),
        parse_mode=ParseMode.MARKDOWN,
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestion des boutons inline"""
    query = update.callback_query
    if query is None or query.data is None:
        logger.warning("Callback reçue sans données exploitables.")
        return

    await query.answer()

    config = get_config(context)

    if query.data == "menu":
        await query.edit_message_text(
            WELCOME_TEXT,
            reply_markup=main_menu_keyboard(config),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif query.data == "info":
        await query.edit_message_text(
            INFO_TEXT,
            reply_markup=info_keyboard(config),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif query.data == "livraison":
        await query.edit_message_text(
            LIVRAISON_TEXT,
            reply_markup=livraison_keyboard(config),
            parse_mode=ParseMode.MARKDOWN,
        )

    elif query.data == "contact":
        await query.edit_message_text(
            render_contact_text(config),
            reply_markup=contact_keyboard(config),
            parse_mode=ParseMode.MARKDOWN,
        )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Réception des commandes depuis la Web App"""
    message = update.effective_message
    if message is None or message.web_app_data is None:
        logger.warning("Update web-app reçu sans données exploitables.")
        return

    config = get_config(context)

    try:
        payload = json.loads(message.web_app_data.data)
    except json.JSONDecodeError:
        logger.exception("Impossible de décoder la commande envoyée par la Web App")
        await message.reply_text(
            "❌ Impossible de lire les informations de commande.",
            reply_markup=support_keyboard(config),
        )
        return

    if not isinstance(payload, dict):
        logger.error("Format inattendu pour la commande Web App: %s", payload)
        await message.reply_text(
            "❌ Format de commande inattendu. Contactez le support.",
            reply_markup=support_keyboard(config),
        )
        return

    cart = payload.get("cart", [])
    cart_lines = _extract_cart_lines(cart)
    cart_count = len(cart) if isinstance(cart, list) else 0
    total = payload.get("total")

    admin_message = build_admin_order_message(update, payload, cart_lines, cart_count, config)

    try:
        await context.bot.send_message(chat_id=config.admin_id, text=admin_message)
    except Exception:
        logger.exception("Erreur lors de l'envoi de la commande à l'admin")
        await message.reply_text(
            "❌ Nous n'avons pas pu transmettre votre commande.\n"
            "Merci de contacter le support directement.",
            reply_markup=support_keyboard(config),
        )
        return

    await message.reply_text(
        build_user_confirmation_message(total, cart_count),
        reply_markup=support_keyboard(config),
        parse_mode=ParseMode.MARKDOWN,
    )

    user_id = update.effective_user.id if update.effective_user else "inconnu"
    logger.info("Commande reçue de %s - Total: %s", user_id, total)

async def set_menu_button(application: Application):
    """Configure le bouton menu avec la Web App"""
    try:
        config = application.bot_data.get("config")
        if not isinstance(config, BotConfig):
            raise ConfigError("Configuration du bot absente pendant set_menu_button")

        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🛍️ Boutique",
                web_app=WebAppInfo(url=config.web_app_url),
            )
        )
        logger.info("Menu button configuré avec succès")
    except Exception:
        logger.exception("Erreur lors de la configuration du menu button")

def main():
    """Démarrage du bot"""
    try:
        config = BotConfig.from_env()
    except ConfigError as exc:
        logger.error("Configuration invalide : %s", exc)
        raise SystemExit(1) from exc

    application = (
        Application.builder()
        .token(config.token)
        .post_init(set_menu_button)
        .build()
    )

    application.bot_data["config"] = config

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("livraison", livraison_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("shop", shop_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(
        MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data)
    )

    logger.info("🤖 Bot CBD Shop démarré…")
    print("🤖 Bot CBD Shop en ligne !")
    print(f"📱 Web App URL: {config.web_app_url}")
    print(f"👤 Admin ID: {config.admin_id}")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
