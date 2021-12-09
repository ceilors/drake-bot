# Drake Meme Bot
[Бот](https://t.me/drake_meme_bot) для генерации мемов с дрейком в телеграмме.

<img src="./resources/drake-yes-small.png" alt="drawing" width="200"/>

Если будете запускать своего на heroku, то:
- установить параметр `USE_HEROKU` в `config.py`
- пропишите в переменные окружения
    - `TOKEN`
    - `HEROKU_BUILDPACK_GIT_LFS_REPO`
    - `APP_NAME` такое же имя как и у сервиса в heroku
- установить `https://github.com/raxod502/heroku-buildpack-git-lfs`
