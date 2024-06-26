# Social Media API
The API performs basic social media actions.

### Technologies
1. Python, Django, ORM, PostgreSQL and Git
2. Celery as task scheduler for creating new posts
3. All endpoints documented via Swagger

### How to run with Docker
- Docker should be installed
- Copy .env.sample to .env and configure all necessary data
- Run `docker-compose up --build`
- Create admin user

### Getting acces
- Create user via `/api/user/register/`
- Get auth token via `/api/user/login/`

### Documentation
- Documentation available via `/api/doc/swagger/`
