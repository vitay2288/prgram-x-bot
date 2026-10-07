import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
DAILY_BONUS = 500
REFERRAL_PERCENT = 9

LEVELS = {
    "Bronze": {"threshold": 0, "bonus": 0},
    "Silver": {"threshold": 5000, "bonus": 100},
    "Gold": {"threshold": 25000, "bonus": 250},
    "Master": {"threshold": 100000, "bonus": 500},
}
