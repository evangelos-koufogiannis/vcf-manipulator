# vcf-manipulator
A REST API (over HTTP) that will manipulate data based on the contents of a VCF File.

# Instructions to start the Django application.

    Clone the project to the desired directory: git clone https://github.com/evangelos-koufogiannis/vcf-manipulator.git
    Change directory to vcf-manipulator one: cd vcf-manipulator/
    Create a Python 3 virtual environmet: python -m venv venv or python3 -m venv venv according to your setup
    Activate the newly created venv: source venv/bin/activate
    Install application's requirements defined in requirements.txt file: pip install -r requirements.txt
    Change directory to Django's project directory: cd manipulator/
    Start the Django server (specify deferent IP and/or Port if that's desired but Postman's calls are for the default server settings): python manage.py runserver
    Default location and file-name for placing your VCF file is defined as "vcf-manipulator/manipulator/vcf/data/file.vcf" (Can be altered at Django project settings.py file)

Note: API call structure and examples can bee found in the Postman files.
