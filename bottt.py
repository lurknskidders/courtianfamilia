import asyncio
from telethon import TelegramClient, errors, events
from telethon.tl.functions.channels import UpdateUsernameRequest
from telethon.tl.functions.account import CheckUsernameRequest
from telethon.tl.types import InputPeerChannel

# === CONFIG - fill these with your info ===
api_id = 26219194
api_hash = 'f4ec9092519091c8102b8b85b615dd07'
group_username = 'wouldsheleave'  # Your group/channel username WITHOUT '@'
target_username = 'groomie'  # The username you want to snipe

# === END CONFIG ===

# Async function to check if username is available
async def is_username_available(client, username):
    try:
        result = await client(CheckUsernameRequest(username))
        return result  # True if available, False if taken
    except errors.FloodWaitError as e:
        print(f"Flood wait: sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"Error checking username availability: {e}")
        return False

# Async function to claim username on user account
async def claim_username(client, username):
    try:
        await client(UpdateUsernameRequest(channel='me', username=username))
        print(f"Successfully claimed username @{username} on user account")
        return True
    except errors.UsernameOccupiedError:
        print(f"Username @{username} is already taken")
        return False
    except errors.FloodWaitError as e:
        print(f"Flood wait while claiming username: sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"Error claiming username: {e}")
        return False

# Async function to transfer username to group/channel
async def transfer_username_to_group(client, group, username):
    try:
        await client(UpdateUsernameRequest(channel=group, username=username))
        print(f"Successfully transferred @{username} to group @{group}")
        return True
    except errors.UsernameOccupiedError:
        print(f"Username @{username} already occupied when transferring")
        return False
    except errors.FloodWaitError as e:
        print(f"Flood wait while transferring username: sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        return False
    except Exception as e:
        print(f"Error transferring username to group: {e}")
        return False

# Async function to send confirmation message to group
async def send_confirmation(client, group, username):
    try:
        await client.send_message(group, f"✅ Username @{username} was successfully claimed and transferred to this group.")
    except Exception as e:
        print(f"Error sending confirmation message: {e}")

async def main():
    print("Starting Telegram sniper bot...")
    phone = input("Enter your phone number (with country code): ")

    client = TelegramClient('sniper_session', api_id, api_hash)

    await client.start(phone=phone)
    print("Logged in successfully.")

    # Resolve group entity
    try:
        group_entity = await client.get_entity(group_username)
    except Exception as e:
        print(f"Failed to get group entity @{group_username}: {e}")
        return

    print(f"Monitoring availability of @{target_username}...")

    while True:
        available = await is_username_available(client, target_username)
        if available:
            print(f"Username @{target_username} is available! Trying to claim...")
            claimed = await claim_username(client, target_username)
            if claimed:
                transferred = await transfer_username_to_group(client, group_entity, target_username)
                if transferred:
                    await send_confirmation(client, group_entity, target_username)
                    print("All done! Exiting.")
                    break
                else:
                    print("Failed to transfer username to group. Releasing username.")
                    # Optional: you can remove username from user account here
                    # await claim_username(client, '') # to release username
                    # Or try again or exit
                    break
            else:
                print("Failed to claim username. Retrying...")
        else:
            print(f"Username @{target_username} not available. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())

