from fastapi import APIRouter
from app.services.google_sheet import get_google_sheet

router = APIRouter(prefix="/google", tags=["Google Sheet"])


@router.get("/test")
def test_google_sheet():

    worksheet = get_google_sheet()

    data = worksheet.get_all_values()

    return {
        "rows": len(data),
        "data": data
    }