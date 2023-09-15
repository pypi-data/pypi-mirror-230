import asyncio
import asyncpg

router_instance = None

async def listen_to_db(settings):
    # Connect to the PostgreSQL database
    try:
        conn = await asyncpg.connect(
            host=settings.host,
            database=settings.database,
            user=settings.user,
            password=settings.password,
            port=settings.port
        )
        
        # Add a listener to a PostgreSQL channel (replace 'your_channel' with the actual channel name)
        await conn.add_listener('routing_rules_updated_channel', notification_handler)
        
        print("Listening for notifications to update routing rules...")
        
        # Keep the coroutine alive to continue listening for notifications
        while True:
            # print("Listening for notifications...")
            await asyncio.sleep(10**8)  
    except Exception as e:
        print(f"cannot connect to database for notifications and rules update service: {e}")


async def notification_handler(connection, pid, channel, payload):
    print(f"Received notification about a routing rules update have been done. Reloading rules from database.......")
    if router_instance:
        router_instance.load_rules_from_postgres()
    # print(f"ruuuules {router_instance.rules}")

def activate_notification_rules_update(router):
    global router_instance
    router_instance = router
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_db(router_instance.db_settings))