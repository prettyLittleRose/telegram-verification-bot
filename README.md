## 👮‍♂️ telegram-verification-bot

a telegram verification bot for group access using the telegram user api with filtering and screening.

## features
### verification
- auto-verify via direct messages to the configured telegram account
- custom rules (premium only, custom country, blacklist terms)

### filtering
- **term blacklisting** - ban specific words in user's bio or personal channel's bio
- **country blacklisting** - block by phone country code
- **font detection** - flag custom/non-ascii fonts
- **premium-only mode** - restrict to premium users

### configuration
- in-bot settings
- separate term/country blocklist
- custmoizable verification thresholds

## setup
### 1. configue settings
Edit `settings.json`:
```json
{
    "user": {
        "app_id": "YOUR_API_ID",
        "app_hash": "YOUR_API_HASH"
    },
    "bot": {
        "token": "YOUR_BOT_TOKEN",
        "chat_id": -1000000000000
    },
    "authorized_users": [123456789]
}
```
### 2. install dependencies
`pip install -r requirements.txt`
### 3. run the bot
`python main.py`

## commands

| command | description |
|---------|-------------|
| `/start` | Show information |
| `/settings` | Configure verification rules |
| `/terms` | Manage blocked terms |
| `/countries` | Manage blocked countries |
