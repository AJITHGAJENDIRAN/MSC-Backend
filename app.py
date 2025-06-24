from flask import Flask, request, jsonify, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from models import db, User, Data
from sqlalchemy import func, extract, distinct
from datetime import datetime
import urllib
from flask import send_from_directory
from flask_cors import CORS
import os




app = Flask(__name__)
CORS(app)

# Set secret key for session
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Change this to a secure random key

params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=14.97.168.235;"
    "DATABASE=data_msc;"
    "UID=sa;"
    "PWD=Viswa.AJ@2025;"
)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
db.init_app(app)

# Create DB tables
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return "API is working"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    return jsonify({"id": new_user.id, "email": new_user.email}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"id": user.id, "email": user.email}), 200

@app.route("/api/sample-type-count", methods=["GET"])
def sample_type_count():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        filters = []
        if start_date:
            filters.append(Data.testdate >= datetime.strptime(start_date, "%Y-%m-%d").date())
        if end_date:
            filters.append(Data.testdate <= datetime.strptime(end_date, "%Y-%m-%d").date())

        query = db.session.query(Data.Samp_Type, func.count(Data.Samp_Type).label("count")).group_by(Data.Samp_Type)
        if filters:
            query = query.filter(*filters)

        return jsonify({row[0]: row[1] for row in query.all()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/ship-hcu-count", methods=["GET"])
def ship_hcu_count():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        filters = [Data.Samp_Type == "HCU"]
        if start_date:
            filters.append(Data.testdate >= datetime.strptime(start_date, "%Y-%m-%d").date())
        if end_date:
            filters.append(Data.testdate <= datetime.strptime(end_date, "%Y-%m-%d").date())

        query = db.session.query(Data.Ship, func.count(Data.Samp_Type)).filter(*filters).group_by(Data.Ship)
        return jsonify({row[0]: row[1] for row in query.all()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/purifier-count", methods=["GET"])
def purifier_count():
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        filters = [Data.Samp_Type == "Purifier"]
        if start_date:
            filters.append(Data.testdate >= datetime.strptime(start_date, "%Y-%m-%d").date())
        if end_date:
            filters.append(Data.testdate <= datetime.strptime(end_date, "%Y-%m-%d").date())

        query = db.session.query(Data.Ship, func.count(Data.Samp_Type)).filter(*filters).group_by(Data.Ship)
        return jsonify({row[0]: row[1] for row in query.all()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/ships', methods=['GET'])
def ship_list():
    try:
        ships = db.session.query(distinct(Data.Ship)).all()
        return jsonify([s[0] for s in ships if s[0]]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ship-hcu-details', methods=['GET'])
def ship_hcu_details():
    try:
        ship = request.args.get('ship')
        start_year = int(request.args.get('startYear'))
        end_year = int(request.args.get('endYear'))

        results = db.session.query(
            Data.Ship,
            Data.testdate,
            Data.vlims_lo_samp_point_Desc,
            Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE,
            Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE,
            Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE
        ).filter(
            Data.Ship == ship,
            extract('year', Data.testdate) >= start_year,
            extract('year', Data.testdate) <= end_year,
            Data.vlims_lo_samp_point_Desc.like('HCU%')
        ).order_by(Data.testdate).all()

        return jsonify([{
            'Ship': r.Ship,
            'Sample_Point': r.vlims_lo_samp_point_Desc,
            'Test_Date': r.testdate.strftime('%Y-%m-%d'),
            'Particle_Count_4_Micron': r.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE or 0.0,
            'Particle_Count_6_Micron': r.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE or 0.0,
            'Particle_Count_14_Micron': r.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE or 0.0
        } for r in results]), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# @app.route('/api/average-particle-count', methods=['GET'])
# def get_average_particle_count():
#     try:
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')
#         ship_name = request.args.get('ship_name', None)

#         if not start_date or not end_date:
#             return jsonify({'error': 'Missing required parameters'}), 400

#         # Convert dates
#         try:
#             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#         except ValueError:
#             return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

#         # Base query
#         query = db.session.query(
#             Data.vlims_lo_samp_point_Desc,
#             func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
#         ).filter(
#             Data.testdate >= start_date,
#             Data.testdate <= end_date,
#             Data.vlims_lo_samp_point_Desc.in_([f'HCU#{i}' for i in range(1, 10)])
#         )

#         # Apply ship filter if ship_name is provided
#         if ship_name and ship_name.lower() != 'all':
#             query = query.filter(Data.Ship == ship_name)
        
#         query = query.group_by(Data.vlims_lo_samp_point_Desc)
#         results = query.all()

#         if not results:
#             return jsonify({'message': 'No data found for the specified date range'}), 404

#         # Format data
#         data_list = [
#             {
#                 'Sample_Point': row.vlims_lo_samp_point_Desc,
#                 'Average_Particle_Count_4_Micron': round(row.avg_4_micron, 2) if row.avg_4_micron else 0.0,
#                 'Average_Particle_Count_6_Micron': round(row.avg_6_micron, 2) if row.avg_6_micron else 0.0,
#                 'Average_Particle_Count_14_Micron': round(row.avg_14_micron, 2) if row.avg_14_micron else 0.0
#             }
#             for row in results
#         ]

#         return jsonify(data_list), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

@app.route('/api/average-particle-count', methods=['GET'])
def get_average_particle_count():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        ship = request.args.get('ship_name', None)

        if not start_date or not end_date:
            return jsonify({'error': 'Missing date parameters'}), 400

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        query = db.session.query(
            Data.vlims_lo_samp_point_Desc,
            func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
        ).filter(
            Data.testdate >= start_date,
            Data.testdate <= end_date,
            Data.vlims_lo_samp_point_Desc.in_([f'HCU#{i}' for i in range(1, 10)])
        )

        if ship and ship.lower() != 'all':
            query = query.filter(Data.Ship == ship)

        results = query.group_by(Data.vlims_lo_samp_point_Desc).all()

        if not results:
            return jsonify({'message': 'No data found'}), 404

        return jsonify([
            {
                'Sample_Point': row.vlims_lo_samp_point_Desc,
                'Average_Particle_Count_4_Micron': round(row.avg_4_micron or 0.0, 2),
                'Average_Particle_Count_6_Micron': round(row.avg_6_micron or 0.0, 2),
                'Average_Particle_Count_14_Micron': round(row.avg_14_micron or 0.0, 2)
            } for row in results
        ]), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# @app.route('/api/average-particle-count', methods=['GET'])
# def get_average_particle_count():
#     try:
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')

#         if not start_date or not end_date:
#             return jsonify({'error': 'Missing required parameters'}), 400

#         # Convert dates
#         try:
#             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#         except ValueError:



#             return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

#         # Query the database for the averages without filtering by ship name
#         results = db.session.query(
#             Data.Ship,
#             Data.vlims_lo_samp_point_Desc,
#             func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
#         ).filter(
#             Data.testdate >= start_date,
#             Data.testdate <= end_date,
#             Data.vlims_lo_samp_point_Desc.in_([f'HCU#{i}' for i in range(1, 10)])
#         ).group_by(Data.Ship, Data.vlims_lo_samp_point_Desc).all()

#         if not results:
#             return jsonify({'message': 'No data found for the specified date range'}), 404

#         # Format data
#         data_list = [
#             {
#                 'Ship': row.Ship,
#                 'Sample_Point': row.vlims_lo_samp_point_Desc,
#                 'Average_Particle_Count_4_Micron': round(row.avg_4_micron, 2) if row.avg_4_micron else 0.0,
#                 'Average_Particle_Count_6_Micron': round(row.avg_6_micron, 2) if row.avg_6_micron else 0.0,
#                 'Average_Particle_Count_14_Micron': round(row.avg_14_micron, 2) if row.avg_14_micron else 0.0
#             }
#             for row in results
#         ]

#         return jsonify(data_list), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

@app.route('/api/filtered-average-particle-count', methods=['GET'])
def filtered_average_particle_count():
    # Your logic here
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({'error': 'Missing required parameters'}), 400

        # Convert dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Query for BEFORE FILTER data
        before_filter_results = db.session.query(
            Data.Ship,
            func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
        ).filter(
            Data.testdate >= start_date,
            Data.testdate <= end_date,
            Data.vlims_lo_samp_point_Desc == 'BEFORE FILTER'
        ).group_by(Data.Ship).all()

        # Query for AFTER FILTER data
        after_filter_results = db.session.query(
            Data.Ship,
            func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
            func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
        ).filter(
            Data.testdate >= start_date,
            Data.testdate <= end_date,
            Data.vlims_lo_samp_point_Desc == 'AFTER FILTER'
        ).group_by(Data.Ship).all()

        # Format the results
        data_list = []
        for row in before_filter_results:
            data_list.append({
                'Ship': row.Ship,
                'vlims_lo_samp_point_Desc': 'BEFORE FILTER',
                'Average_Particle_Count_4_Micron': round(row.avg_4_micron, 2) if row.avg_4_micron else 0.0,
                'Average_Particle_Count_6_Micron': round(row.avg_6_micron, 2) if row.avg_6_micron else 0.0,
                'Average_Particle_Count_14_Micron': round(row.avg_14_micron, 2) if row.avg_14_micron else 0.0
            })

        for row in after_filter_results:
            data_list.append({
                'Ship': row.Ship,
                'vlims_lo_samp_point_Desc': 'AFTER FILTER',
                'Average_Particle_Count_4_Micron': round(row.avg_4_micron, 2) if row.avg_4_micron else 0.0,
                'Average_Particle_Count_6_Micron': round(row.avg_6_micron, 2) if row.avg_6_micron else 0.0,
                'Average_Particle_Count_14_Micron': round(row.avg_14_micron, 2) if row.avg_14_micron else 0.0
            })

        return jsonify(data_list), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# @app.route('/api/filtered-average-particle-count', methods=['GET'])
# def filtered_average_particle_count():
#     # Your logic here
#     try:
#         start_date = request.args.get('start_date')
#         end_date = request.args.get('end_date')

#         if not start_date or not end_date:
#             return jsonify({'error': 'Missing required parameters'}), 400

#         # Convert dates
#         try:
#             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#         except ValueError:
#             return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

#         # Query for BEFORE FILTER data
#         before_filter_results = db.session.query(
#             Data.Ship,
#             func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
#         ).filter(
#             Data.testdate >= start_date,
#             Data.testdate <= end_date,
#             Data.vlims_lo_samp_point_Desc == 'BEFORE FILTER'
#         ).group_by(Data.Ship).all()

#         # Query for AFTER FILTER data
#         after_filter_results = db.session.query(
#             Data.Ship,
#             func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6_micron'),
#             func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14_micron')
#         ).filter(
#             Data.testdate >= start_date,
#             Data.testdate <= end_date,
#             Data.vlims_lo_samp_point_Desc == 'AFTER FILTER'
#         ).group_by(Data.Ship).all()

#         # Format the results
#         data_list = []
#         for row in before_filter_results:
#             data_list.append({
#                 'Ship': row.Ship,
#                 'vlims_lo_samp_point_Desc': 'BEFORE FILTER',
#                 'Average_Particle_Count_4_Micron': round(row.avg_4_micron, 2) if row.avg_4_micron else 0.0,
#                 'Average_Particle_Count_6_Micron': round(row.avg_6_micron, 2) if row.avg_6_micron else 0.0,
#                 'Average_Particle_Count_14_Micron': round(row.avg_14_micron, 2) if row.avg_14_micron else 0.0
#             })

#         for row in after_filter_results:
#             data_list.append({
#                 'Ship': row.Ship,
#                 'vlims_lo_samp_point_Desc': 'AFTER FILTER',
#                 'Average_Particle_Count_4_Micron': round(row.avg_4_micron, 2) if row.avg_4_micron else 0.0,
#                 'Average_Particle_Count_6_Micron': round(row.avg_6_micron, 2) if row.avg_6_micron else 0.0,
#                 'Average_Particle_Count_14_Micron': round(row.avg_14_micron, 2) if row.avg_14_micron else 0.0
#             })

#         return jsonify(data_list), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

# @app.route('/api/filtered-average-particle-count', methods=['GET'])
# def avg_particle_count():
#     try:
#         start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
#         end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()

#         data_list = []
#         for label in ['BEFORE FILTER', 'AFTER FILTER']:
#             results = db.session.query(
#                 Data.Ship,
#                 func.avg(Data.VLIMS_PARTICLE_COUNT_4_MICRON_SCALE).label('avg_4'),
#                 func.avg(Data.VLIMS_PARTICLE_COUNT_6_MICRON_SCALE).label('avg_6'),
#                 func.avg(Data.VLIMS_PARTICLE_COUNT_14_MICRON_SCALE).label('avg_14')
#             ).filter(
#                 Data.testdate >= start_date,
#                 Data.testdate <= end_date,
#                 Data.vlims_lo_samp_point_Desc == label
#             ).group_by(Data.Ship).all()

#             for row in results:
#                 data_list.append({
#                     'Ship': row.Ship,
#                     'vlims_lo_samp_point_Desc': label,
#                     'Average_Particle_Count_4_Micron': round(row.avg_4, 2) if row.avg_4 else 0.0,
#                     'Average_Particle_Count_6_Micron': round(row.avg_6, 2) if row.avg_6 else 0.0,
#                     'Average_Particle_Count_14_Micron': round(row.avg_14, 2) if row.avg_14 else 0.0
#                 })

#         return jsonify(data_list), 200

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
    # app.run(debug=True, host='0.0.0.0', port=5000)