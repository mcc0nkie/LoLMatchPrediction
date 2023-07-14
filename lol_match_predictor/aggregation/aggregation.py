import pandas as pd
import sqlalchemy as sa

def save_to_postgres(df, table_name, database_name, user, password, host, port):
    engine = sa.create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
    df.to_sql(table_name, engine, if_exists='replace', index=False)