# Yatube
### Description:
Social network of free writers. The following features are implemented in the project:
* Registration
* Create a post
* Recover password
* Comment on posts
* Subscribe to the author
* Pagination of pages
* Access control
---
### Technologies:
* Python 3.9.10
* Django 2.2.19
* Pillow==8.3.0
* Pytest==5.3.5
* Sorl-thumbnail==12.6.3
---
### Installation and launch:
1. Clone the repository. On the command line:
```
git clone https://github.com/MrKalister/yatube_final.git
```
or use SSH-key:
```
git clone git@github.com:MrKalister/yatube_final.git
```
2. Install and activate the virtual environment
```
python -m venv venv
```
```
source venv/Scripts/activate
```
3. Install dependencies from the file requirements.txt
```
pip install -r requirements.txt
``` 
4. Make migrate:
```
python3 manage.py migrate
```
5. Run a project in dev-mode:
```
cd yatube/
```
```
python3 manage.py runserver
```
6. Open in your browser localhost or 127.0.0.1
---

### Author
 **Maxim Novikov** 
## Date of creation
2022/3/1
