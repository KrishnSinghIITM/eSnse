from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json
from app.schemas import QueryPayload, QueryResponse, ErrorResponse, MessageResponse
from app.database import run_query, rows_to_dicts
from app.services.llm_service import generate_sql_from_question
from app.services.validator_service import validate_sql
from app.services.insight_service import generate_insight
from app.services import cache_service

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/cache/stats")
def cache_stats():
    """Return cache statistics."""
    return cache_service.stats()


@router.post("/query", response_model=QueryResponse)
def query(payload: QueryPayload):
    """Accepts `user_id` and `question`, returns cached answer if exists, else:
    generates SQL, validates it, executes, generates friendly answer, and caches.

    Step 0: Check cache for this user+question.
    Step 1: Generate SQL from the question using Gemini or fallback heuristics.
    Step 2: Validate the SQL (must be SELECT, no DELETE/DROP/UPDATE/INSERT).
    Step 3: Execute the query and get results.
    Step 4: Generate a human-friendly insight from the result using Gemini.
    Step 5: Cache the answer for next time.
    """

    # Step 0: Check cache first
    cached_answer = cache_service.get_answer(payload.user_id, payload.question)
    if cached_answer:
        return QueryResponse(result=cached_answer + "\n\n(Cached result - retrieved instantly)")

    try:
        # Step 1: Generate SQL from question
        sql_query = generate_sql_from_question(payload.question, payload.user_id)
        
        # Check if SQL generation failed
        if not sql_query or sql_query.strip() == "":
            return JSONResponse(status_code=503, content={"error": "LLM unavailable"})
        
        # Step 2: Validate SQL
        is_valid, validation_msg = validate_sql(sql_query)
        if not is_valid:
            return JSONResponse(status_code=400, content={"error": "Unable to generate valid query"})
        
        # Step 3: Execute query and normalize rows to dicts
        rows = run_query(sql_query)
        rows_dicts = rows_to_dicts(rows)

        if not rows_dicts or all(all(v is None for v in r.values()) for r in rows_dicts):
            return JSONResponse(status_code=404, content={"message": "No transactions found"})

        # Step 4: Generate insight using normalized rows
        insight = generate_insight(payload.question, rows_dicts, rows_dicts)
        
        # Step 5: Cache the result
        cache_service.set_answer(payload.user_id, payload.question, insight)
        
        return QueryResponse(result=insight)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
