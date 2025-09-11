#create requirement file
pip freeze > requirements.txt
install requirement
pip install requirements.txt
python manage.py runserver


brew install python@3.11
python3.11 -m venv venv

For generating the Scret key

python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
