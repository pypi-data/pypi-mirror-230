import asyncio
import asyncpg



####### can we get rid of this handling loop, do we need it in the first place, or asyncpg will keep riunning in the background? #####
####### if connection is droped it seems not connecting again, neweds more checking ######


router_instance = None

async def listen_to_db(router_instance):
    settings = router_instance.db_settings
    conn = None
    while True:
        try:
            if not conn or conn.is_closed():
                # Connect to the PostgreSQL database
                conn = await asyncpg.connect(
                    host=settings.host,
                    database=settings.database,
                    user=settings.user,
                    password=settings.password,
                    port=settings.port
                )

                # Add a listener to a PostgreSQL channel
                await conn.add_listener('routing_rules_updated_channel', notification_handler)

                print("Listening for notifications to update routing rules...")
                print("ReLoading rules from postgres....")
                router_instance.load_rules_from_postgres()
            
            # Keep the coroutine alive to continue listening for notifications
            await asyncio.sleep(5)  # Adjust the sleep time as needed
        except Exception as e:
            print(f"An unexpected error occurred when trying to listen to updates for routing rules: {e}")
            await asyncio.sleep(5)  # Sleep before attempting to reconnect in case of unexpected errors


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
    loop.run_until_complete(listen_to_db(router_instance))