from .db import SessionLocal, Run, Event, Artifact
from datetime import datetime

class MemoryService:
    # Instead of keeping one global session, open a new one per call

    def log_event(self, run_id, agent, payload):
        with SessionLocal() as db:
            db.add(Event(run_id=run_id, agent=agent, payload=payload))
            db.commit()

    def add_artifact(self, run_id, kind, uri, meta=None):
        with SessionLocal() as db:
            db.add(Artifact(run_id=run_id, kind=kind, uri=uri, meta=meta or {}))
            db.commit()

    def save_run(self, run_id, user_id, mode, ps, prefs, status):
        with SessionLocal() as db:
            run = db.query(Run).filter_by(run_id=run_id).first()
            if not run:
                db.add(
                    Run(
                        run_id=run_id,
                        user_id=user_id,
                        mode=mode,
                        problem_statement=ps,
                        preferences=prefs,
                        status=status,
                    )
                )
            else:
                run.status = status
                run.updated_at = datetime.utcnow()
            db.commit()


# ✅ Single service instance for app usage
memory = MemoryService()
