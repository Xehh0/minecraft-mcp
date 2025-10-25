class MineResourceSkill:
    async def execute(self, server, params):
        username = params.get("username")
        resource = params.get("name")
        count = params.get("count", 1)
        if not username or username not in server.bots:
            return {"error": f"Bot '{username}' not found"}
        if not resource:
            return {"error": "Resource name is required"}
        bot = server.bots[username]
        try:
            await bot.send_packet("player_digging", 0, {"x": 0, "y": 0, "z": 0}, 0)
            await asyncio.sleep(1)
            return {"status": "success", "resource": resource, "count": count}
        except Exception as e:
            return {"error": f"Mining failed: {str(e)}"}
