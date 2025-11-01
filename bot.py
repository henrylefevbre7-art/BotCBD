# bot.py
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes
)
import json
import logging

# ========== CONFIGURATION ==========

TOKEN = "8329422168:AAHxxYoB2GeDk_UVKoQoBJo6TiPdBnsQfiE"  # <- ton token (pense à le régénérer + mettre en variable d'env ensuite)
ADMIN_ID = 123456789  # TODO: mets TON user id (trouve-le via @userinfobot)
WEB_APP_URL = "https://bottlg-khkg.onrender.com/"  # ton URL de mini-app (HTTPS + slash final)
CHANNEL_URL = "https://t.me/+TUar__WdjbE4ZmY0"     # ton canal
CONTACT_USERNAME = "PuffLabz"                      # sans @

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

CONTACT_TEXT = (
    "📞 *Nous Contacter*\n\n"
    "*Service Client :*\n"
    f"Telegram : @{CONTACT_USERNAME}\n"
    "Réponse sous 2h en moyenne\n\n"
    "*Horaires :*\n"
    "Lundi - Vendredi : 9h - 20h\n"
    "Samedi - Dimanche : 10h - 18h\n\n"
    "*Suivez-nous :*\n"
    f"📢 Notre canal : {CHANNEL_URL}\n"
    "Offres exclusives, nouveautés et promotions !\n\n"
    "*Questions fréquentes :*\n"
    "• Livraison : /livraison\n"
    "• Nos produits : /info\n"
    "• Boutique : /shop\n\n"
    "*Une question ? Une suggestion ?*\n"
    "N’hésitez pas à nous écrire directement !"
)

# ========== COMMANDES ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /start - Message de bienvenue"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Accéder à la boutique",
                              web_app=WebAppInfo(url=WEB_APP_URL))],
        [
            InlineKeyboardButton("ℹ️ Informations", callback_data="info"),
            InlineKeyboardButton("📦 Livraison", callback_data="livraison")
        ],
        [
            InlineKeyboardButton("📞 Contact", callback_data="contact"),
            InlineKeyboardButton("📢 Notre Canal", url=CHANNEL_URL)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /info"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Voir la boutique",
                              web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("« Retour au menu", callback_data="menu")]
    ]
    await update.message.reply_text(
        INFO_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def livraison_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /livraison"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Commander maintenant",
                              web_app=WebAppInfo(url=WEB_APP_URL))],
        [InlineKeyboardButton("« Retour au menu", callback_data="menu")]
    ]
    await update.message.reply_text(
        LIVRAISON_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /contact"""
    keyboard = [
        [InlineKeyboardButton("💬 Envoyer un message",
                              url=f"https://t.me/{CONTACT_USERNAME}")],
        [InlineKeyboardButton("📢 Rejoindre le canal", url=CHANNEL_URL)],
        [InlineKeyboardButton("« Retour au menu", callback_data="menu")]
    ]
    await update.message.reply_text(
        CONTACT_TEXT,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Commande /shop - Ouvrir la boutique"""
    keyboard = [[InlineKeyboardButton("🛍️ Ouvrir la boutique",
                                      web_app=WebAppInfo(url=WEB_APP_URL))]]
    await update.message.reply_text(
        "🌿 Cliquez sur le bouton ci-dessous pour accéder à notre boutique :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gestion des boutons inline"""
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        keyboard = [
            [InlineKeyboardButton("🛍️ Accéder à la boutique",
                                  web_app=WebAppInfo(url=WEB_APP_URL))],
            [
                InlineKeyboardButton("ℹ️ Informations", callback_data="info"),
                InlineKeyboardButton("📦 Livraison", callback_data="livraison")
            ],
            [
                InlineKeyboardButton("📞 Contact", callback_data="contact"),
                InlineKeyboardButton("📢 Notre Canal", url=CHANNEL_URL)
            ]
        ]
        await query.edit_message_text(
            WELCOME_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "info":
        keyboard = [
            [InlineKeyboardButton("🛍️ Voir la boutique",
                                  web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton("« Retour au menu", callback_data="menu")]
        ]
        await query.edit_message_text(
            INFO_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "livraison":
        keyboard = [
            [InlineKeyboardButton("🛍️ Commander maintenant",
                                  web_app=WebAppInfo(url=WEB_APP_URL))],
            [InlineKeyboardButton("« Retour au menu", callback_data="menu")]
        ]
        await query.edit_message_text(
            LIVRAISON_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "contact":
        keyboard = [
            [InlineKeyboardButton("💬 Envoyer un message",
                                  url=f"https://t.me/{CONTACT_USERNAME}")],
            [InlineKeyboardButton("📢 Rejoindre le canal", url=CHANNEL_URL)],
            [InlineKeyboardButton("« Retour au menu", callback_data="menu")]
        ]
        await query.edit_message_text(
            CONTACT_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Réception des commandes depuis la Web App"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        message = data["message"]
        cart = data["cart"]
        total = data["total"]

        # Envoyer la commande à l'admin
        admin_message = message.replace("\\n", "\n").replace("\\-", "-")
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_message,
            parse_mode="MarkdownV2"
        )

        # Confirmation au client
        keyboard = [[InlineKeyboardButton(
            "📞 Contacter le support",
            url=f"https://t.me/{CONTACT_USERNAME}"
        )]]
        await update.message.reply_text(
            f"✅ *Commande reçue !*\n\n"
            f"Montant total : *{total}€*\n"
            f"Nombre d'articles : *{len(cart)}*\n\n"
            f"📱 Vous serez contacté rapidement pour finaliser votre commande.\n\n"
            f"Merci de votre confiance ! 🌿",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

        logger.info(f"Commande reçue de {update.effective_user.id} - Total: {total}€")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de la commande : {e}")
        await update.message.reply_text(
            "❌ Une erreur est survenue lors de l'envoi de votre commande.\n"
            "Veuillez réessayer ou nous contacter directement."
        )

async def set_menu_button(application: Application):
    """Configure le bouton menu avec la Web App"""
    try:
        await application.bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🛍️ Boutique",
                web_app=WebAppInfo(url=WEB_APP_URL)
            )
        )
        logger.info("Menu button configuré avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la configuration du menu button : {e}")

def main():
    """Démarrage du bot"""
    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("livraison", livraison_command))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("shop", shop_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    # Configurer le menu button
    application.post_init = set_menu_button

    logger.info("🤖 Bot CBD Shop démarré…")
    print("🤖 Bot CBD Shop en ligne !")
    print(f"📱 Web App URL: {WEB_APP_URL}")
    print(f"👤 Admin ID: {ADMIN_ID}")

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
