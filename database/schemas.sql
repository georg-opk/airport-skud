-- Создание таблиц базы данных СКУД (§2.6)
CREATE TABLE employees (
    id          SERIAL PRIMARY KEY,
    full_name   VARCHAR(255) NOT NULL,
    position    VARCHAR(100),
    department  VARCHAR(100),
    hire_date   DATE,
    status      VARCHAR(20) DEFAULT 'активен',
    photo_path  TEXT
);

CREATE TABLE zones (
    id             SERIAL PRIMARY KEY,
    zone_name      VARCHAR(100) NOT NULL,
    zone_type      VARCHAR(50),
    security_level INT
);

CREATE TABLE passes (
    id           SERIAL PRIMARY KEY,
    employee_id  INT REFERENCES employees(id),
    pass_number  VARCHAR(50),
    issue_date   DATE,
    expiry_date  DATE,
    status       VARCHAR(20) DEFAULT 'активен',
    access_level INT
);

CREATE TABLE access_rights (
    id          SERIAL PRIMARY KEY,
    pass_id     INT REFERENCES passes(id),
    zone_id     INT REFERENCES zones(id),
    valid_from  TIMESTAMP,
    valid_to    TIMESTAMP,
    time_window VARCHAR(50)
);

CREATE TABLE checkpoints (
    id              SERIAL PRIMARY KEY,
    checkpoint_name VARCHAR(100),
    zone_id         INT REFERENCES zones(id),
    camera_id       VARCHAR(50)
);

CREATE TABLE access_events (
    id               SERIAL PRIMARY KEY,
    event_time       TIMESTAMP NOT NULL DEFAULT now(),
    checkpoint_id    INT REFERENCES checkpoints(id),
    employee_id      INT REFERENCES employees(id),
    pass_id          INT REFERENCES passes(id),
    result           VARCHAR(20),
    similarity_score FLOAT CHECK (similarity_score BETWEEN 0 AND 1),
    liveness_score   FLOAT CHECK (liveness_score BETWEEN 0 AND 1),
    reason           TEXT
);

CREATE TABLE blacklist (
    id         SERIAL PRIMARY KEY,
    person_id  VARCHAR(50),
    full_name  VARCHAR(255),
    photo_path TEXT,
    add_date   TIMESTAMP DEFAULT now(),
    reason     TEXT
);

CREATE TABLE system_users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    role          VARCHAR(20),
    password_hash TEXT
);

-- Индексы для ускорения поиска
CREATE INDEX idx_events_employee ON access_events(employee_id);
CREATE INDEX idx_events_time     ON access_events(event_time);
CREATE INDEX idx_rights_pass     ON access_rights(pass_id);
CREATE INDEX idx_cp_zone         ON checkpoints(zone_id);


-- Триггер автоматического аннулирования пропуска по сроку действия
CREATE OR REPLACE FUNCTION set_pass_expired()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expiry_date < CURRENT_DATE THEN
        NEW.status := 'аннулирован';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_pass_status
    BEFORE UPDATE ON passes
    FOR EACH ROW
    EXECUTE FUNCTION set_pass_expired();


-- Скользящее среднее нагрузки по часам (оконная функция)
WITH hourly AS (
    SELECT date_trunc('hour', event_time) AS h, COUNT(*) AS cnt
    FROM access_events GROUP BY h
)
SELECT h, cnt,
       AVG(cnt) OVER (ORDER BY h
                      ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) AS avg_cnt
FROM hourly ORDER BY h;

-- Ранжирование событий сотрудника (последние сверху)
SELECT employee_id, event_time, result,
       ROW_NUMBER() OVER (PARTITION BY employee_id
                          ORDER BY event_time DESC) AS rn
FROM access_events;

-- Выявление аномалий: многократные отказы за период
SELECT employee_id, COUNT(*) AS refusal_count
FROM access_events
WHERE result = 'отказ'
GROUP BY employee_id
HAVING COUNT(*) > 5;


