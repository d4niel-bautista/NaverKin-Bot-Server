from services.queues import ws_conn_outbound

async def process_incoming_message(client_id, message):
    print(client_id, message)