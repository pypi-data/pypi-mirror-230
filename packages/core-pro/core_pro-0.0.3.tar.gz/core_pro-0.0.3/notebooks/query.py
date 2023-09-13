from src.core_pro.oop_sql import DataPipeLine


query = """
    select grass_date
    , count(distinct user_id) total_a1
    from mp_user.dws_user_login_1d__vn_s0_live
    where grass_date >= date'2022-01-01'
    group by 1
"""
df = DataPipeLine(query).run_presto_to_df()
