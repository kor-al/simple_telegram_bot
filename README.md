# simple_telegram_bot

This bot is implemented using the [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and [dateparser](https://pypi.org/project/dateparser/) libraries.

The file [preprocess_code](https://github.com/kor-al/simple_telegram_bot/blob/master/preprocess_code.py) produces the table of cities that is required for the bot to work properly.

### Example:

**bot**: Здравствуйте, я помогу вам с оформлением авиабилетов. Как я могу к вам обращаться? <br />
Сурок <br />
**bot**: Сурок, откуда вы полетите?<br />
Самара<br />
**bot**: Сурок, куда вы полетите?<br />
Рио-де-Жанейро<br />
**bot**: Сурок, в какие даты?<br />
с 8 марта по 18 июня<br />
**bot**: Спасибо! Всё ли верно: вы собираетесь отправиться из Самары в Рио-де-Жанейро 8 марта и вернуться 18 июня?<br />
Да <br />
**bot**: Отлично. Предлагаю вам следующие варианты перелета: https://www.aviasales.ru/search/KUF0803RIO18061<br />
**bot**: Хотите обсудить другую поездку?<br />
Нет <br />
**bot**: Окей, до свидания, Сурок.<br />
**bot**: Отправьте /start, чтобы снова начать разговор.<br />

