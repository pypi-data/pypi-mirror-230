# To extract strings that need translation
pybabel extract -F ./config/i18n/application.cfg -o ./config/i18n/application.pot .

# Initialize a new language
pybabel init -i ./config/i18n/application.pot -d ./config/i18n -l <LOCALE> -D application

# Update existing
pybabel update -i ./config/i18n/application.pot -d ./config/i18n -D application

# to compile
pybabel compile -f -d ./config/i18n -D application