# To extract strings that need translation
pybabel extract -F ./config/i18n/arches.cfg -o ./config/i18n/arches.pot .

# Initialize a new language
pybabel init -i ./config/i18n/arches.pot -d ./config/i18n -l <LOCALE> -D arches

# Update existing
pybabel update -i ./config/i18n/arches.pot -d ./config/i18n -D arches

# to compile
pybabel compile -f -d ./config/i18n -D arches