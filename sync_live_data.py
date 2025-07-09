from flask import Flask, jsonify
import urllib.parse
import pandas as pd
import pyodbc
from sqlalchemy import create_engine

app = Flask(__name__)

# 1️⃣ Source DB connection (VLIMS_HOUSTON)
source_conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=4.233.139.169,1433;"
    "DATABASE=VLIMS_HOUSTON;"
    "UID=VLIMS_Admin;"
    "PWD=Admin@TheViswaGroup@2022"
)
source_params = urllib.parse.quote_plus(source_conn_str)
source_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={source_params}")

# 2️⃣ Destination DB connection (data_msc)
dest_conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=52.140.61.220;"
    "DATABASE=data_msc;"
    "UID=sa;"
    "PWD=Viswa.AJ#2025"
)
dest_params = urllib.parse.quote_plus(dest_conn_str)
dest_engine = create_engine(f"mssql+pyodbc:///?odbc_connect={dest_params}")

# 3️⃣ Query to pull data from source
QUERY = """
select 
    LO.[VLIMS_LO_BATCH_NO] BatchNo,
    LO.[VLIMS_LO_SERIAL] LO_Serial,
    LO.[VLIMS_LO_SAMP_TYPE] SampleType,
    c.vlims_customer_id,
    C.[VLIMS_CUSTOMER_NAME] CustomerName,
    s.vlims_ship_id,
    S.[VLIMS_SHIP_NAME] Ship,
    vlims_ship_imo_number,
    LOE.[VLIMS_LO_EQUIPMENT_DESCRIPTION] Equipment,
    VLIMS_LO_SAMP_POINT_DESC,
    [VLIMS_PARTICLE_COUNT_4_MICRON_RANGE],
    [VLIMS_PARTICLE_COUNT_4_MICRON_SCALE],
    [VLIMS_PARTICLE_COUNT_6_MICRON_RANGE],
    [VLIMS_PARTICLE_COUNT_6_MICRON_SCALE],
    [VLIMS_PARTICLE_COUNT_14_MICRON_RANGE],
    [VLIMS_PARTICLE_COUNT_14_MICRON_SCALE],
    [VLIMS_PARTICLE_COUNT_21_MICRON_RANGE],
    [VLIMS_PARTICLE_COUNT_21_MICRON_SCALE],
    [VLIMS_PARTICLE_COUNT_38_MICRON_RANGE],
    [VLIMS_PARTICLE_COUNT_38_MICRON_SCALE],
    [VLIMS_PARTICLE_COUNT_4406_ISO_CODE],
    [VLIMS_PARTICLE_COUNT_4406_ME_MAKE],
    [VLIMS_PARTICLE_COUNT_4406_ALLOWABLE_LIMIT],
    [VLIMS_LO_IMAGE_ID],
    [VLIMS_PARTICLE_COUNT_4406_INTERPRETATION],
    [VLIMS_ISO_PARTICLE_COUNT_4_MICRON_MAN_LIMIT],
    [VLIMS_ISO_PARTICLE_COUNT_6_MICRON_MAN_LIMIT],
    [VLIMS_ISO_PARTICLE_COUNT_14_MICRON_MAN_LIMIT],
    [VLIMS_ISO_PARTICLE_TYPE1],
    [VLIMS_ISO_PARTICLE_TYPE2],
    [VLIMS_ISO_MAGNIFICATION],
    [VLIMS_ISO_SAMPLE_VOLUME],
    [VLIMS_ISO_DIAMETER_OF_ANALYSIS_MEMBRANE],
    [VLIMS_ISO_TYPE_METHOD],
    convert(Date,LO.[VLIMS_TEST_DATE]) TestDate,
    L.VLIMS_TEST_LOCATION_NAME TestLocation,
    datepart(week,LO.[VLIMS_TEST_DATE]) weeknum,
    datepart(week,LO.[VLIMS_TEST_DATE]-6) Week_ACC
from [dbo].[VLIMS_LUBE_OIL_SAMPLE] LO
inner join VLIMS_HOUSTON.dbo.VLIMS_CUSTOMER C on LO.VLIMS_CUSTOMER_ID = C.VLIMS_CUSTOMER_ID
inner join VLIMS_SHIP S on LO.[VLIMS_SHIP_ID] = S.VLIMS_SHIP_ID
inner join [VLIMS_HOUSTON].dbo.[VLIMS_LO_EQUIPMENT] LOE on LO.[VLIMS_LO_EQUIPMENT_ID] = LOE.[VLIMS_LO_EQUIPMENT_ID]
inner JOIN VLIMS_Houston.dbo.vlims_test_location L on L.VLIMS_TEST_LOCATION_ID = LO.VLIMS_TEST_LOCATION_ID
join VLIMS_LO_PALL_CONTAMINATION PC on pc.VLIMS_LO_SERIAL = Lo.VLIMS_LO_SERIAL
where LO.VLIMS_TEST_DATE between '01-01-2010' and '12-31-2040'
and c.vlims_customer_id = 488
order by LO.VLIMS_TEST_DATE, LO.[VLIMS_LO_SERIAL]
"""

@app.route("/sync-live-data", methods=["GET"])
def sync_live_data():
    try:
        # Step 1: Read data from source
        df = pd.read_sql_query(QUERY, source_engine)

        # Step 2: Write to destination - new table named BI_Live_Data (replace if exists)
        df.to_sql("BI_Live_Data", dest_engine, if_exists="replace", index=False)

        return jsonify({
            "status": "success",
            "rows_written": len(df),
            "message": "Live data synced to BI_Live_Data table successfully."
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
