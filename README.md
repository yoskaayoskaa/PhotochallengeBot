# PhotochallengeBot 

### Game Telegram chatbot developed on Aiohttp + asyncio.

The main project goal is to become more familiar with Python asynchronous programming.

*Stack:*
* Poller / Workers / Sender: asyncio + Queues
* Admin API:  
Aiohttp + apispec + marshmallow + Swagger + Postman
* DB: PostgreSQL + SQLAlchemy + Alembic
* Tests: pytest
* VPS: beget (Ubuntu 22.04)

*Game mechanics and main features:*  

* Chat participants are divided into pairs, vote for each other's avatars, the whole game winner with the most votes for all rounds is determined.  
* All updates and chat messages are put in the queues to increase the bot consistency and not to lose the update/message on reload.
* Bot supports simultaneous play in multiple chats while monitoring the game status in each of them.
* Players registration is implemented, as well as recording the game session and the players results in different chats.
* There is also a general game statistics for all players in all chats.
* [Admin API](https://github.com/yoskaayoskaa/PhotochallengeBot_Admin_API) as a separate Aiohttp app.
* Game mechanics is covered by asynchronous tests.

**Feel free to contact me for bot testing :)**
