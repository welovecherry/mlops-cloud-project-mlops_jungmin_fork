# #!/bin/bash
# airflow db init
# airflow users create \
#     --username admin \
#     --firstname admin \
#     --lastname lee \
#     --role Admin \
#     --email admin@airflow.com \
#     --password admin123
# airflow webserver -p 8181 & airflow scheduler

#!/bin/bash

# airflow db init

# airflow users create \
#   --username admin \
#   --firstname admin \
#   --lastname lee \
#   --role Admin \
#   --email admin@airflow.com \
#   --password admin123

# # webserver와 scheduler를 모두 백그라운드 실행하지 말고, webserver만 foreground로
# airflow scheduler &

# exec airflow webserver -p 8181

#!/bin/bash
# airflow db init
# airflow users create \
#     --username admin \
#     --firstname admin \
#     --lastname lee \
#     --role Admin \
#     --email admin@airflow.com \
#     --password admin123
# exec airflow webserver --host 0.0.0.0 --port 8181 & airflow scheduler

#!/bin/bash
airflow db init
airflow users create \
    --username admin \
    --firstname admin \
    --lastname lee \
    --role Admin \
    --email admin@airflow.com \
    --password admin123

# 스케줄러는 백그라운드, 웹서버는 포그라운드로
airflow scheduler &
exec airflow webserver --host 0.0.0.0 --port 8181