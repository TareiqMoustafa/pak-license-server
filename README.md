# سيرفر التراخيص

## الملفات
`server.py` المسارات · `core.py` منطق التراخيص والإعدادات · `telegram_bot.py` بوت تيليجرام ·
`admin_page.py` لوحة التحكم · `store.py` التخزين (Upstash) · `security.py` المصادقة وتحديد المعدل.

## متغيرات Vercel
| المتغير | الغرض |
|---|---|
| `ADMIN_TOKEN` | توكن لوحة التحكم (24 حرفاً على الأقل، **غيّره الآن**) |
| `KEY_PEPPER` | سر لتشفير الأكواد. لا تغيّره بعد إنشاء أكواد وإلا لن تعمل القديمة |
| `KV_*` | تضيفها Upstash تلقائياً |
| `TELEGRAM_BOT_TOKEN` | توكن البوت (اختياري) |
| `TELEGRAM_ADMIN_IDS` | معرّفاتك الرقمية مفصولة بفاصلة (اختياري) |
| `PATCH_URL` `PATCH_FILE_NAME` `GAME_PACKAGE` | احتياطية فقط؛ الأفضل من اللوحة ← الإعدادات |

## المسارات
- `POST /api/verify` التحقق (يستقبل `app_version`، ويرجع رابط الباتش ورقمه والتحديث الإلزامي)
- `GET /api/app-config` إعلان/دعم/صيانة بدون رابط الباتش
- `GET/POST /api/admin/settings` · `POST /api/admin/add` · `GET /api/admin/list` · `POST /api/admin/control`
- `POST /api/admin/telegram/setup` ربط البوت · `POST /api/telegram/webhook`
- `GET /admin` اللوحة · `GET /api/health`

## أوامر بوت تيليجرام
`/add month 3 أحمد` · `/list` · `/info ID` · `/extend ID 30` · `/reset ID` · `/ban ID` · `/unban ID` ·
`/delete ID نعم` · `/stats` · `/settings` · `/link URL` · `/version 5` · `/force on|off` · `/notice نص` · `/maintenance on|off`
