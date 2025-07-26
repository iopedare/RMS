from app.extensions import db
import datetime

class MasterElectionLog(db.Model):
    """
    ORM model for tracking master election history and reasons.
    """
    __tablename__ = 'master_election_log'

    id = db.Column(db.Integer, primary_key=True)
    previous_master_id = db.Column(db.String(255), nullable=True)
    new_master_id = db.Column(db.String(255), nullable=False)
    election_reason = db.Column(db.String(50), nullable=False)  # 'shutdown', 'failure', 'manual', etc.
    election_timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    devices_participating = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<MasterElectionLog(id={self.id}, prev={self.previous_master_id}, new={self.new_master_id}, reason={self.election_reason})>"

    def to_dict(self):
        return {
            'id': self.id,
            'previous_master_id': self.previous_master_id,
            'new_master_id': self.new_master_id,
            'election_reason': self.election_reason,
            'election_timestamp': self.election_timestamp.isoformat() if self.election_timestamp else None,
            'devices_participating': self.devices_participating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 