import datetime as dt

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Appointment, get_db, init_db
from schemas import (
    AppointmentRequest,
    AppointmentResponse,
    CancelAppointmentRequest,
    CancelAppointmentResponse,
    ListAppointmentRequest,
)

app = FastAPI()

init_db()


@app.post("/schedule_appointment/")
def schedule_appointment(request: AppointmentRequest, db: Session = Depends(get_db)):
    new_appointment = Appointment(
        patient_name=request.patient_name,
        reason=request.reason,
        start_time=request.start_time,
    )
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)

    return AppointmentResponse(
        id=new_appointment.id,
        patient_name=new_appointment.patient_name,
        reason=new_appointment.reason,
        start_time=new_appointment.start_time,
        canceled=new_appointment.canceled,
        created_at=new_appointment.created_at,
    )


@app.post("/cancel_appointment/")
def cancel_appointment(request: CancelAppointmentRequest, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(request.date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.patient_name == request.patient_name)
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .where(Appointment.canceled == False)  # noqa: E712
    )

    appointments = result.scalars().all()
    if not appointments:
        raise HTTPException(
            status_code=404,
            detail="No matching appointment for the details found in our system",
        )

    for appointment in appointments:
        appointment.canceled = True

    db.commit()

    return CancelAppointmentResponse(canceled_count=len(appointments))


@app.get("/list_appointments/")
def list_appointments(date: dt.date, db: Session = Depends(get_db)):
    start_dt = dt.datetime.combine(date, dt.time.min)
    end_dt = start_dt + dt.timedelta(days=1)

    result = db.execute(
        select(Appointment)
        .where(Appointment.canceled == False)  # noqa: E712
        .where(Appointment.start_time >= start_dt)
        .where(Appointment.start_time < end_dt)
        .order_by(Appointment.start_time.asc())
    )

    booked_appointments = []
    for appointment in result.scalars().all():
        booked_appointments.append(
            AppointmentResponse(
                id=appointment.id,
                patient_name=appointment.patient_name,
                reason=appointment.reason,
                start_time=appointment.start_time,
                canceled=appointment.canceled,
                created_at=appointment.created_at,
            )
        )

    return booked_appointments

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend:app", host="127.0.0.1", port=4444, reload=True)