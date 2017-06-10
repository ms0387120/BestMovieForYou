# Best Movie for You!

## Usage
- First, go to the `mysite` folder, and create a `config.yaml` file. For linux system:
```linux
cd mysite
cp config_template.yaml config.yaml
```
Inside the `config.yaml` file, fill in your OMDB api key.

- Second, type the following command to launch the server:
```python
python manage.py runserver <port>
```
This will launch a local host on `<port>`.

- Third, browse the website:
```
http://localhost:<port>
```
And, enjoy!

## Required packages:
```
beautifulsoup4==4.6.0
Django==1.11.2
httplib2==0.10.3
nltk==3.2.4
numpy==1.12.1
PyYAML==3.12
requests==2.11.1
scikit-learn==0.18.1
scipy==0.19.0
sklearn==0.0
```