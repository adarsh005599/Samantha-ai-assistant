from __future__ import annotations

import datetime as dt

from pydantic import BaseModel


class AppointmentRequest(BaseModel):
    patient_name: str
    reason: str | None = None
    start_time: dt.datetime


class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    reason: str | None
    start_time: dt.datetime
    canceled: bool
    created_at: dt.datetime


class CancelAppointmentRequest(BaseModel):
    patient_name: str
    date: dt.date


class CancelAppointmentResponse(BaseModel):
    canceled_count: int


class ListAppointmentRequest(BaseModel):
    date: dt.date