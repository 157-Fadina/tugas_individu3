from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import zope.sqlalchemy

# 1. Setup Base (Dasar untuk Model)
Base = declarative_base()

# 2. Fungsi untuk membuat koneksi (Engine)
def get_engine(settings, prefix='sqlalchemy.'):
    return create_engine(settings['sqlalchemy.url'])

# 3. Fungsi untuk membuat pabrik session
def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory

# 4. Fungsi untuk mendapatkan session (Transaction Manager)
def get_tm_session(session_factory, transaction_manager):
    dbsession = session_factory()
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession

# 5. Fungsi untuk bikin tabel otomatis
def init_db(engine):
    Base.metadata.create_all(engine)