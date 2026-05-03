"""Versioned API router aggregator."""

from __future__ import annotations

from fastapi import APIRouter

from src.api import dashboard, commands, reminders

router = APIRouter(prefix="/api/v1")
router.include_router(dashboard.router)
router.include_router(commands.router)
router.include_router(reminders.router)
