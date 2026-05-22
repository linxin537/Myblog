from datetime import datetime
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Table, Index, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

article_likes = Table(
    "article_likes",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

article_favorites = Table(
    "article_favorites",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("article_id", ForeignKey("articles.id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow, nullable=False),
)

class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False) # Markdown
    html_content: Mapped[str | None] = mapped_column(Text, nullable=True) # HTML Cache
    summary: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cover_image: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_draft: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    author = relationship("User", backref="articles")
    category = relationship("Category", back_populates="articles")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")

    # FULLTEXT index for MySQL
    __table_args__ = (
        Index('idx_title_content_fulltext', 'title', 'content', mysql_prefix='FULLTEXT', mysql_with_parser='ngram'),
    )
