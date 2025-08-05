#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for postgres..."
while ! nc -z postgres 5432; do
  sleep 0.5
done
echo "PostgreSQL started"

# Run migrations only if RUN_MIGRATIONS is set to true
if [ "$RUN_MIGRATIONS" = "true" ]; then
  echo "Making migrations..."
  python manage.py makemigrations --noinput

  echo "Applying migrations..."
  python manage.py migrate --noinput
else
  echo "Skipping migrations."
fi

# Execute the command passed from CMD
exec "$@"




# #!/bin/bash
# # Wait for PostgreSQL to be ready
# echo "Waiting for postgres..."
# while ! nc -z postgres 5432; do
#   sleep 0.5
# done
# echo "PostgreSQL started"

# # echo "Making migrations..."
# # python manage.py makemigrations --noinput

# # Run migrations
# python manage.py migrate --noinput

# # Run passed CMD
# exec "$@"
