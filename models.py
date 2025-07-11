# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import func
# from datetime import date

# db = SQLAlchemy()

# class User(db.Model):
#     """
#     User model for authentication.
#     """
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)

#     def __repr__(self):
#         return f"<User {self.email}>"


# class Data(db.Model):
#     """
#     Data model for ship particle count records.
#     """
#     # __tablename__ = 'ship_data'
#     __tablename__ = 'data'

#     id = db.Column(db.Integer, primary_key=True)
#     Ship = db.Column(db.String(255), nullable=False)
#     Samp_Type = db.Column(db.String(50), nullable=False)
#     testdate = db.Column(db.Date, nullable=False)
#     vlims_lo_samp_point_Desc = db.Column(db.String(50), nullable=True)
#     VLIMS_PARTICLE_COUNT_4_MICRON_SCALE = db.Column(db.Float, nullable=True)
#     VLIMS_PARTICLE_COUNT_6_MICRON_SCALE = db.Column(db.Float, nullable=True)
#     VLIMS_PARTICLE_COUNT_14_MICRON_SCALE = db.Column(db.Float, nullable=True)

#     def __repr__(self):
#         return f"<Data {self.Ship} - {self.testdate}>"

#     def to_dict(self) -> dict:
#         """
#         Convert instance to dictionary for JSON response.
#         """
#         return {
#             'id': self.id,
#             'Ship': self.Ship,
#             'Samp_Type': self.Samp_Type,
#             'Test_Date': self.testdate.strftime('%Y-%m-%d') if self.testdate else None,
#             'Sample_Point': self.vlims_lo_samp_point_Desc,
#             'Particle_Count_4_Micron': self.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE or 0.0,
#             'Particle_Count_6_Micron': self.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE or 0.0,
#             'Particle_Count_14_Micron': self.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE or 0.0
#         }

#     @staticmethod
#     def get_filtered_data(start_date: date, end_date: date):
#         """
#         Returns aggregated particle count averages for 'BEFORE FILTER' and 'AFTER FILTER' points.
#         """
#         return db.session.query(
#             Data.Ship,
#             Data.vlims_lo_samp_point_Desc,
#             func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
#         ).filter(
#             Data.testdate >= start_date,
#             Data.testdate <= end_date,
#             Data.vlims_lo_samp_point_Desc.in_(['BEFORE FILTER', 'AFTER FILTER'])
#         ).group_by(Data.Ship, Data.vlims_lo_samp_point_Desc).all()


# new code



# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import func
# from datetime import date

# db = SQLAlchemy()

# class User(db.Model):
#     """
#     User model for authentication.
#     """
#     __tablename__ = 'users'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False)

#     def __repr__(self):
#         return f"<User {self.email}>"

# class Data(db.Model):
#     __tablename__ = 'data'

#     Ship = db.Column(db.String(255), primary_key=True)
#     Samp_Type = db.Column(db.String(50), primary_key=True)
#     testdate = db.Column(db.Date, primary_key=True)
#     vlims_lo_samp_point_Desc = db.Column(db.String(50), primary_key=True)

#     VLIMS_PARTICLE_COUNT_4_MICRON_SCALE = db.Column(db.Float, nullable=True)
#     VLIMS_PARTICLE_COUNT_6_MICRON_SCALE = db.Column(db.Float, nullable=True)
#     VLIMS_PARTICLE_COUNT_14_MICRON_SCALE = db.Column(db.Float, nullable=True)
# # class Data(db.Model):
# #     """
# #     Data model for ship particle count records.
# #     """
# #     __tablename__ = 'data'

# #     # id = db.Column(db.Integer, primary_key=True)
# #     Ship = db.Column(db.String(255), nullable=False)
# #     Samp_Type = db.Column(db.String(50), nullable=False)
# #     testdate = db.Column(db.Date, nullable=False)
# #     vlims_lo_samp_point_Desc = db.Column(db.String(50), nullable=True)
# #     VLIMS_PARTICLE_COUNT_4_MICRON_SCALE = db.Column(db.Float, nullable=True)
# #     VLIMS_PARTICLE_COUNT_6_MICRON_SCALE = db.Column(db.Float, nullable=True)
# #     VLIMS_PARTICLE_COUNT_14_MICRON_SCALE = db.Column(db.Float, nullable=True)

#     def __repr__(self):
#         return f"<Data {self.Ship} - {self.testdate}>"

#     def to_dict(self) -> dict:
#         """
#         Convert instance to dictionary for JSON response.
#         """
#         return {
#             'id': self.id,
#             'Ship': self.Ship,
#             'Samp_Type': self.Samp_Type,
#             'Test_Date': self.testdate.strftime('%Y-%m-%d') if self.testdate else None,
#             'Sample_Point': self.vlims_lo_samp_point_Desc,
#             'Particle_Count_4_Micron': self.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE or 0.0,
#             'Particle_Count_6_Micron': self.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE or 0.0,
#             'Particle_Count_14_Micron': self.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE or 0.0
#         }

#     @staticmethod
#     def get_filtered_summary(start_date: date, end_date: date, ship_name: str):
#         """
#         Returns average particle counts for BEFORE and AFTER FILTER for a specific ship.
#         """
#         return db.session.query(
#             Data.vlims_lo_samp_point_Desc.label('Sample_Point'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
#         ).filter(
#             Data.testdate >= start_date,
#             Data.testdate <= end_date,
#             Data.vlims_lo_samp_point_Desc.in_(['BEFORE FILTER', 'AFTER FILTER']),
#             Data.Ship == ship_name
#         ).group_by(Data.vlims_lo_samp_point_Desc).all()


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date

db = SQLAlchemy()

class User(db.Model):
    """
    User model for authentication.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

class Data(db.Model):
    """
    Data model for ship particle count records.
    This assumes your 'data' table in SQL Server DOES NOT have an 'id' column.
    Composite primary key is set using 4 fields.
    """
    __tablename__ = 'live_data'

    Ship = db.Column(db.String(255), primary_key=True)
    Samp_Type = db.Column(db.String(50), primary_key=True)
    testdate = db.Column(db.Date, primary_key=True)
    vlims_lo_samp_point_Desc = db.Column(db.String(50), primary_key=True)

    VLIMS_PARTICLE_COUNT_4_MICRON_SCALE = db.Column(db.Float, nullable=True)
    VLIMS_PARTICLE_COUNT_6_MICRON_SCALE = db.Column(db.Float, nullable=True)
    VLIMS_PARTICLE_COUNT_14_MICRON_SCALE = db.Column(db.Float, nullable=True)

    # ✅ Add this field for ship summary endpoint
    LO_Serial = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Data {self.Ship} - {self.testdate}>"

    def to_dict(self) -> dict:
        """
        Convert instance to dictionary for JSON response.
        """
        return {
            'Ship': self.Ship,
            'Samp_Type': self.Samp_Type,
            'Test_Date': self.testdate.strftime('%Y-%m-%d') if self.testdate else None,
            'Sample_Point': self.vlims_lo_samp_point_Desc,
            'Particle_Count_4_Micron': self.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE or 0.0,
            'Particle_Count_6_Micron': self.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE or 0.0,
            'Particle_Count_14_Micron': self.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE or 0.0
        }

    @staticmethod
    def get_filtered_summary(start_date: date, end_date: date, ship_name: str):
        """
        Returns average particle counts for BEFORE and AFTER FILTER for a specific ship.
        """
        return db.session.query(
            Data.vlims_lo_samp_point_Desc.label('Sample_Point'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
        ).filter(
            Data.testdate >= start_date,
            Data.testdate <= end_date,
            Data.vlims_lo_samp_point_Desc.in_(['BEFORE FILTER', 'AFTER FILTER']),
            Data.Ship == ship_name
        ).group_by(Data.vlims_lo_samp_point_Desc).all()