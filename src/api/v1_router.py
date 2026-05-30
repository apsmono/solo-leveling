"""Versioned API router aggregator."""

from __future__ import annotations

from fastapi import APIRouter

from src.api import dashboard, commands, reminders, library, graph, timeline, analysis, planning, autopilot, guide, n8n_callback

router = APIRouter(prefix="/api/v1")
router.include_router(dashboard.router)
router.include_router(commands.router)
router.include_router(reminders.router)
router.include_router(library.router)
router.include_router(graph.router)
router.include_router(timeline.router)
router.include_router(analysis.router)
router.include_router(planning.router)
router.include_router(autopilot.router)
router.include_router(guide.router)
router.include_router(n8n_callback.router)
