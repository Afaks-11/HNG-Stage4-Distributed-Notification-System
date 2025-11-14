@echo off
echo 🔧 Setting up databases...

echo ⏳ Waiting for PostgreSQL to be ready...
:wait_loop
docker exec shared-postgres pg_isready -U postgres >nul 2>&1
if %errorlevel% neq 0 (
    echo PostgreSQL is unavailable - sleeping
    timeout /t 2 /nobreak >nul
    goto wait_loop
)

echo ✅ PostgreSQL is ready

echo 🔧 Creating database: user_service_db
docker exec shared-postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='user_service_db'" | findstr "1" >nul
if %errorlevel% neq 0 (
    docker exec shared-postgres psql -U postgres -c "CREATE DATABASE user_service_db;"
    echo ✅ Created database 'user_service_db'
) else (
    echo ✅ Database 'user_service_db' already exists
)

echo 🔧 Creating database: template_service_db
docker exec shared-postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='template_service_db'" | findstr "1" >nul
if %errorlevel% neq 0 (
    docker exec shared-postgres psql -U postgres -c "CREATE DATABASE template_service_db;"
    echo ✅ Created database 'template_service_db'
) else (
    echo ✅ Database 'template_service_db' already exists
)

echo 🔧 Creating database: push_service_db
docker exec shared-postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='push_service_db'" | findstr "1" >nul
if %errorlevel% neq 0 (
    docker exec shared-postgres psql -U postgres -c "CREATE DATABASE push_service_db;"
    echo ✅ Created database 'push_service_db'
) else (
    echo ✅ Database 'push_service_db' already exists
)

echo 🔧 Creating database: email_service_db
docker exec shared-postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='email_service_db'" | findstr "1" >nul
if %errorlevel% neq 0 (
    docker exec shared-postgres psql -U postgres -c "CREATE DATABASE email_service_db;"
    echo ✅ Created database 'email_service_db'
) else (
    echo ✅ Database 'email_service_db' already exists
)

echo 🔧 Creating database: api_gateway_db
docker exec shared-postgres psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='api_gateway_db'" | findstr "1" >nul
if %errorlevel% neq 0 (
    docker exec shared-postgres psql -U postgres -c "CREATE DATABASE api_gateway_db;"
    echo ✅ Created database 'api_gateway_db'
) else (
    echo ✅ Database 'api_gateway_db' already exists
)

echo ✅ Database setup complete