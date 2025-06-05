<h1 align="center"> Archio project</h1>

## Description
This website platform allows volunteers to transcribe and label ancient documents using crowdsourcing. It aims to improve the transcription of any type of document, regardless of subject, language or layout.
This project has been developed as part of a master thesis at UCLouvain in computer science (EPL faculty).

- Can help AI learning
- Automated and less time-consuming management
- Faster and more user-friendly transcription
- Flexible workflow

## Project demo 
### Transcription
To transcribe a document, a volunteer has to label each line and transcribe each line into the corresponding text box.

[Tutorial video](https://youtu.be/aq-J-yl0LEo)
<p>
  <img src = "https://i.imgur.com/ZWHZYJE.png" width=800>
</p>


### Verification
The transcription must be checked by another volunteer. If the volunteer suggests another transcription for a line, this line must go through a new verification step.

<p>
  <img src = "https://i.imgur.com/psuMMh0.png" width=800>
</p>

### Consultation
Once the process has been completed, you can view the transcription of a document (with a list of proposals) and export the data.

<p>
  <img src = "https://i.imgur.com/WGh7GuZ.png" width=800>
</p>

### Forum
A forum is included to allow volunteers to help each other about a particular document or line.
<p>
  <img src = "https://i.imgur.com/rvo2MVb.png" width=800>
</p>

## Extra features
- Built-in forum for volunteers collaboration
- Export data and metadata
- Closed group project and candidate system
- User management with roles
## Installation
### Requirements
    Python 3.10 
    Django 5.1.3
    Pillow 11.1.0

### Deployment
This project can be deployed in a python development environment with the following command

    python3 ./manage.py runserver 0.0.0.0:8000

For a production deployment, you need to refer to the [Django specifications](https://docs.djangoproject.com/fr/5.2/howto/deployment/)

 ## Contact 
 Author: Jeremy Sidgwick ([Linkedin](https://www.linkedin.com/in/jeremy-sidgwick/))
 

## License
This projet is under MIT license
