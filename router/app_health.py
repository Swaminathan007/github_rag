from fastapi import APIRouter
from .llm_init import get_llm
router = APIRouter(prefix="/app")


@router.get("/health")
async def health_check():
    try:
        llm_model = get_llm()
        llm_health = llm_model.check_health()
        vector_db_health = llm_model.vector_db.check_health()
        return {
            "llm_health": llm_health,
            "vector_db_health": vector_db_health,
            "app":True
        }
    except Exception as e:
        return {
            "llm_health": "Down",
            "vector_db_health": "Down",
            "error": str(e)
        }