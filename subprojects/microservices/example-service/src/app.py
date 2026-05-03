"""Example microservice for the solo-leveling monorepo."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
