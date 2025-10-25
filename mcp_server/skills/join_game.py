class JoinGameSkill:
    async def execute(self, server, params):
        username = params.get("username")
        host = params.get("host")
        port = params.get("port")
        if not username:
            return {"error": "Username is required"}
        return await server.connect_bot(username, host, port)
