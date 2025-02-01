from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import httpx
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyResponse(BaseModel):
    symbol: str
    name: str
    id: int
    url: str

@app.get("/api/search")
async def search_stocks(q: str):
    if not q or len(q) < 2:
        return []
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://www.screener.in/api/company/search/",
                params={"q": q, "v": 3, "fts": 1}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Failed to fetch results from upstream")
            
            data = response.json()
            
            if not isinstance(data, list):
                return []
            
            # Filter and format results
            filtered_results = [
                {
                    "symbol": company["url"].replace("/company/", "").replace("/", ""),
                    "name": company["name"],
                    "id": company["id"],
                    "url": company["url"]
                }
                for company in data
                if company.get("id") is not None
            ]
            
            return filtered_results
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)