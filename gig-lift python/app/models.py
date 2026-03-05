from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, UniqueConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    rides_offered: Mapped[list["Ride"]] = relationship(
        back_populates="driver",
        cascade="all, delete-orphan",
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="rider",
        cascade="all, delete-orphan",
    )
    sent_messages: Mapped[list["RideMessage"]] = relationship(
        "RideMessage",
        back_populates="sender",
        cascade="all, delete-orphan",
    )

class Ride(Base):
    __tablename__ = "rides"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    driver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    origin: Mapped[str] = mapped_column(String(200), nullable=False)
    origin_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    origin_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    destination: Mapped[str] = mapped_column(String(200), nullable=False)
    depart_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    seats_total: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    artist: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    tags_csv: Mapped[str] = mapped_column(Text, nullable=False, default="")
    @property
    def tags(self) -> list[str]:
        return [t.strip() for t in self.tags_csv.split(",") if t.strip()]
    @tags.setter
    def tags(self, items: list[str]) -> None:
        self.tags_csv = ",".join(sorted({t.strip() for t in items if t.strip()}))
    driver: Mapped["User"] = relationship(back_populates="rides_offered")
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="ride",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["RideMessage"]] = relationship(
        "RideMessage",
        back_populates="ride",
        cascade="all, delete-orphan",
        order_by="RideMessage.created_at.asc()",
    )

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), nullable=False)
    rider_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ride: Mapped["Ride"] = relationship(back_populates="bookings")
    rider: Mapped["User"] = relationship(back_populates="bookings")

class CompletedRide(Base):
    __tablename__ = "completed_rides"
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), primary_key=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("ride_id", "rater_id", "ratee_id", name="uq_rating_once_per_ride_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), nullable=False)
    rater_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    ratee_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    stars: Mapped[int] = mapped_column(Integer, nullable=False)  # 1..5
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (
        UniqueConstraint("ride_id", "reporter_id", "reported_user_id", name="uq_report_once_per_ride_pair"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), nullable=False)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reported_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AdminUser(Base):
    __tablename__ = "admin_users"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class RideMessage(Base):
    __tablename__ = "ride_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id"), nullable=False, index=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    ride: Mapped["Ride"] = relationship("Ride", back_populates="messages")
    sender: Mapped["User"] = relationship("User", back_populates="sent_messages")


class UserBlock(Base):
    __tablename__ = "user_blocks"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_block_once"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    blocker_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    blocked_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    blocker: Mapped["User"] = relationship("User", foreign_keys=[blocker_id])
    blocked: Mapped["User"] = relationship("User", foreign_keys=[blocked_id])
