from datetime import datetime
from kafka import KafkaConsumer
from sqlalchemy import create_engine, Column, Integer, Text, TIMESTAMP
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import json

Base = declarative_base()

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    text = Column(Text)
    created_at = Column(TIMESTAMP)

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
Session = sessionmaker(bind=engine)

consumer = KafkaConsumer(
    'post_events',
    bootstrap_servers=os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    session = Session()
    try:
        event = message.value
        if event['type'] == 'post_created':
            new_post = Post(
                user_id=event['user_id'],
                text=event['text'],
                created_at=datetime.fromisoformat(event['created_at'])
            )
            session.add(new_post)
            session.commit()
            print(f"Post {new_post.id} saved to PostgreSQL")
    except Exception as e:
        session.rollback()
        print(f"Error processing event: {str(e)}")
    finally:
        session.close()