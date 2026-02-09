from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from models.track import Track
from models.artist import Artist
from typing import Optional, List


class TrackRepository:
    @staticmethod
    def create(db: Session, track: Track) -> Track:
        db.add(track)
        db.commit()
        db.refresh(track)
        return track

    @staticmethod
    def get_all(db: Session) -> List[Track]:
        tracks: List[Track] = db.query(Track).all()
        return tracks

    @staticmethod
    def get_by_id(db: Session, track_id: int) -> Optional[Track]:
        track: Optional[Track] = (
            db.query(Track).filter(Track.idTrack == track_id).first()
        )
        return track

    @staticmethod
    def get_by_youtube_link(db: Session, youtube_link: str) -> Optional[Track]:
        track: Optional[Track] = (
            db.query(Track).filter(Track.youtubeLink == youtube_link).first()
        )
        return track

    @staticmethod
    def search_tracks(db: Session, query: str, limit: int = 10):
        tracks = (
            db.query(Track)
            .join(Track.artists)
            .options(joinedload(Track.artists))
            .filter(
                or_(
                    Track.title.ilike(f"%{query}%"),
                    Artist.name.ilike(f"%{query}%"),
                )
            )
            .distinct()
            .limit(limit)
            .all()
        )

        return tracks
