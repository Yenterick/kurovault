from fastapi import APIRouter

router = APIRouter()


@router.get("/", description="Endpoint to check the server status.")
async def health_check():
    return {"status": "ok", "message": "KuroVault API is up and running!"}
