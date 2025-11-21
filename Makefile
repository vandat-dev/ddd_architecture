.PHONY: proto

# Run app
run:
	uvicorn app.main:app --port 8007 --reload

create-admin:
	@read -p "👤 Username: " username; \
	read -p "📧 Email: " email; \
	read -p "🔑 Password: " password; \
	python -m app.scripts.create_admin \
		--username $$username \
		--email $$email \
		--password $$password
