from sqlalchemy import Integer, Column, String, Float, DateTime


class ShuttlePoint:
    __tablename__ = 'shuttle_data'
    """Name of the table of data points"""

    id = Column('ID', Integer, primary_key=True)
    """Primary key of shuttle data points"""

    license_plate = Column('LICENSE_PLATE_NUM', String)
    """License plate of shuttle"""

    shuttle_company = Column('SHUTTLE_COMPANY', String)
    """Name of the shuttle company"""

    longitude = Column('LOCATION_LONGITUDE', Float)
    """Longitude of shuttle position"""

    latitude = Column('LOCATION_LATITUDE', Float)
    """Latitude of shuttle position"""

    timestamp = Column('TIMESTAMPLOCAL', DateTime)
    """Time that this point was recorded"""
