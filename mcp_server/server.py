import sys
import json
import argparse
import asyncio
from quarry.net.client import ClientFactory, ClientProtocol
from skills.join_game import JoinGameSkill
from skills.mine_resource import MineResourceSkill

class MinecraftBot(ClientProtocol):
    async def packet_chat_message(self, buff, message):
        pass

    async def packet_disconnect(self, buff, reason):
        self.close()

class MinecraftClientFactory(ClientFactory):
    protocol = MinecraftBot

class MCPServer:
    def __init__(self, host="localhost", port=25565):
        self.host = host
        self.port = port
        self.bots = {}
        self.skills = {
            "joinGame": JoinGameSkill(),
            "mineResource": MineResourceSkill()
        }

    async def start(self):
        while True:
            try:
                line = sys.stdin.readline().strip()
                if not line:
                    continue
                request = json.loads(line)
                response = await self.handle_request(request)
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
            except json.JSONDecodeError:
                sys.stdout.write(json.dumps({"error": "Invalid JSON input"}) + "\n")
                sys.stdout.flush()
            except Exception as e:
                sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
                sys.stdout.flush()

    async def handle_request(self, request):
        skill_name = request.get("tool")
        params = request.get("params", {})
        if skill_name not in self.skills:
            return {"error": f"Skill '{skill_name}' not found"}
        try:
            result = await self.skills[skill_name].execute(self, params)
            return {"result": result}
        except Exception as e:
            return {"error": f"Skill execution failed: {str(e)}"}

    async def connect_bot(self, username, host=None, port=None):
        host = host or self.host
        port = port or self.port
        factory = MinecraftClientFactory()
        factory.protocol_version = 340
        protocol = await factory.connect(host, port, username)
        self.bots[username] = protocol
        return {"status": "connected", "username": username}

    async def disconnect_bot(self, username):
        if username in self.bots:
            self.bots[username].close()
            del self.bots[username]
            return {"status": "disconnected", "username": username}
        return {"error": f"Bot '{username}' not found"}

def parse_args():
    parser = argparse.ArgumentParser(description="Minecraft MCP Server")
    parser.add_argument("-p", "--port", type=int, default=25565, help="Minecraft server port")
    parser.add_argument("-h", "--host", default="localhost", help="Minecraft server host")
    return parser.parse_args()

async def main():
    args = parse_args()
    server = MCPServer(host=args.host, port=args.port)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
