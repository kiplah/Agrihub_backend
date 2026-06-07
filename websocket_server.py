import asyncio
import json
import os
import datetime
from urllib.parse import urlparse, parse_qs
import websockets

PORT = int(os.environ.get("PORT", 8081))
HOST = os.environ.get("HOST", "0.0.0.0")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")

# Map user_id (str) to a set of active WebSocket connections
active_connections = {}

# Check database configuration
DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = False

if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
    IS_POSTGRES = True
    print("WebSocket Server configured for PostgreSQL.")
else:
    print(f"WebSocket Server configured for SQLite: {DB_PATH}")

def get_db_connection():
    if IS_POSTGRES:
        import psycopg2
        return psycopg2.connect(DATABASE_URL)
    else:
        import sqlite3
        return sqlite3.connect(DB_PATH)

def get_username(user_id):
    """Fetch username for a given user ID from database."""
    if not user_id:
        return "Unknown"
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        query = "SELECT username FROM users_user WHERE id = ?"
        params = (user_id,)
        if IS_POSTGRES:
            query = query.replace('?', '%s')
        cur.execute(query, params)
        row = cur.fetchone()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"Error fetching username for ID {user_id}: {e}")
    return "Unknown"

def save_message_to_db(sender_id, receiver_id, content):
    """Save message to Django database and return message details."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    is_read = False
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        query = "INSERT INTO chat_message (content, timestamp, is_read, receiver_id, sender_id) VALUES (?, ?, ?, ?, ?)"
        params = (content, timestamp, is_read, int(receiver_id), int(sender_id))
        
        if IS_POSTGRES:
            query = query.replace('?', '%s') + " RETURNING id"
            cur.execute(query, params)
            msg_id = cur.fetchone()[0]
        else:
            cur.execute(query, params)
            msg_id = cur.lastrowid
            
        conn.commit()
        conn.close()
        
        sender_username = get_username(sender_id)
        receiver_username = get_username(receiver_id)
        
        return {
            "id": msg_id,
            "sender": int(sender_id),
            "senderId": int(sender_id),
            "sender_username": sender_username,
            "receiver": int(receiver_id),
            "receiverId": int(receiver_id),
            "receiver_username": receiver_username,
            "content": content,
            "timestamp": timestamp,
            "is_read": is_read
        }
    except Exception as e:
        print(f"Error saving message to database: {e}")
        return None

async def handler(websocket):
    # Parse sender ID and receiver ID from connection URL query params
    query_params = parse_qs(urlparse(websocket.path).query)
    sender_id = query_params.get("senderID", [None])[0]
    
    if not sender_id:
        print("Connection rejected: missing senderID query parameter.")
        await websocket.close(code=4000, reason="senderID query param required")
        return
        
    sender_id = str(sender_id)
    active_connections.setdefault(sender_id, set()).add(websocket)
    print(f"User {sender_id} connected. Active connections for {sender_id}: {len(active_connections[sender_id])}")

    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                # Parse fields with fallback capitalization checks
                msg_sender_id = str(data.get("senderId") or data.get("senderID") or data.get("sender_id") or sender_id)
                msg_receiver_id = str(data.get("receiverId") or data.get("receiverID") or data.get("receiver_id"))
                content = data.get("content")
                
                if not msg_receiver_id or not content:
                    print("Received invalid message payload: missing receiverId or content.")
                    continue
                
                print(f"Received message from {msg_sender_id} to {msg_receiver_id}: {content}")
                
                # Save message to database
                message_payload = save_message_to_db(msg_sender_id, msg_receiver_id, content)
                if not message_payload:
                    print("Failed to save message to database. Skipping broadcast.")
                    continue
                
                # Convert payload back to JSON
                broadcast_data = json.dumps(message_payload)
                
                # Send back to sender's active connections so they get the database message state
                for conn in active_connections.get(msg_sender_id, []):
                    try:
                        await conn.send(broadcast_data)
                    except Exception as e:
                        print(f"Error sending message back to sender {msg_sender_id}: {e}")
                        
                # Send to receiver's active connections if they are online
                if msg_receiver_id in active_connections:
                    print(f"Broadcasting to receiver {msg_receiver_id} (online)")
                    for conn in active_connections[msg_receiver_id]:
                        try:
                            await conn.send(broadcast_data)
                        except Exception as e:
                            print(f"Error forwarding message to receiver {msg_receiver_id}: {e}")
                else:
                    print(f"Receiver {msg_receiver_id} is offline. Message saved to DB.")

            except json.JSONDecodeError:
                print("Received non-JSON message from client.")
            except Exception as e:
                print(f"Error processing message: {e}")

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed for user {sender_id}: {e}")
    finally:
        # Clean up connection registry
        if sender_id in active_connections:
            active_connections[sender_id].discard(websocket)
            if not active_connections[sender_id]:
                active_connections.pop(sender_id)
            print(f"User {sender_id} disconnected. Active connections for {sender_id}: {len(active_connections.get(sender_id, []))}")

async def main():
    print(f"Starting WebSocket server on ws://{HOST}:{PORT}")
    async with websockets.serve(handler, HOST, PORT):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWebSocket server stopped.")
