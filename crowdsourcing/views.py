from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import View

from forum.models import UserPost
from authentication.models import User
from .forms import ImageUploadForm, TextForm
from .models import Document, Rectangle, Task, Subtask, Project, UserProject

from datetime import timedelta
import csv
import json

from django.views.generic.edit import FormView
from .forms import FileFieldForm

class FileFieldFormView(FormView):

    form_class = FileFieldForm
    template_name = 'local/upload_image.html'  # Replace with your template.
    success_url = "/upload/"  # Replace with your URL or reverse().

    def form_valid(self, form):
        print("form",form)
        files = form.cleaned_data["Files"]
        master_name = form.cleaned_data["Archive_name"]
        project = form.cleaned_data["project"]
        for f in files:
            uploaded_file = Document(image=f, group_name=master_name,project=project)
            uploaded_file.save()
            #TODO save in (file and master name)
        return super().form_valid(form)

# def upload_image(request):
#     if request.method == 'POST':
#         form = ImageUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#     else:
#         form = ImageUploadForm()
#     return render(request, 'local/upload_image.html', {'form': form})

# todo remettre le login mais ça fonctionne pas comme ça pour les class
# @login_required()
class TranscriptionPage(View):

    template_name = "local/transcription.html"

    def get(self, request, doc_id):
        user = request.user
        document = Document.objects.get(pk=doc_id)

        if document.status == "to_transcribe": #debut dans le tache
            task = Task()
            task.document = document
            task.ended = now() + timedelta(hours=1)
            task.user = user
            document.status = 'in_transcription'

        elif document.status == "in_transcription":#reprendre une sauvegarde
            task = Task.objects.get(document=document, status='in_progress', type='transcription')
            if task.user != user:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()

        document.save()
        task.save()

        #generate data for template
        image = document.image
        rectangles = Rectangle.objects.filter(document=doc_id)

        forms = []
        rectangles_data=[]
        for rect in rectangles:
            text_value = ""
            try:
                subtask = Subtask.objects.get(task=task, rectangle=rect)
                print(subtask)
                text_value = subtask.text
            except:
                pass

            forms.append((rect, TextForm(instance=rect), text_value))

            rectangles_data.append({
                "x": rect.x,
                "y": rect.y,
                "width": rect.width,
                "height": rect.height,
                "angle": rect.angle,
                "id": rect.id
            })

        return render(request, self.template_name, {
            'document': document,
            'rectangles': rectangles_data,
            'forms': forms,
        })


    def post(self, request, doc_id):
        document =Document.objects.get(pk=doc_id)
        task = Task.objects.get(document=document, status='in_progress', type='transcription')
        k = request.POST
        print(k)
        submit = False
        if("submit" in k):
            submit = True
            print("submit")
            document.status = 'to_verify'
            document.save()
            task.status = 'completed'
            task.save()

        for key, text_value in request.POST.items():
            print(key, text_value)
            if key.startswith('rect_'):  # Identifier les champs par un préfixe unique
                rect_id = key.split('_')[1]  # Extraire l'ID du rectangle
                try:
                    rectangle = Rectangle.objects.get(id=rect_id)
                    existing_subtasks = Subtask.objects.filter(task=task, rectangle=rectangle)
                except Rectangle.DoesNotExist:
                    print("Rectangle with ID", rect_id, "does not exist")
                    continue
                if (len(existing_subtasks) > 0):
                    print("existing_subtasks", existing_subtasks)
                    sub = existing_subtasks[0]
                else:
                    print("creating subtask with rectangle", rectangle.id, "with value:", text_value)
                    sub = Subtask()
                    sub.task = task
                    sub.rectangle = rectangle
                if(submit):
                    sub.status = 'completed'
                sub.text = text_value
                sub.save()
        return redirect('/project/' + str(document.project.id))  # Rediriger après le succès


def save_rectangles(request):

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            doc_id = data.get('document')
            rectangles = data.get('rectangles', [])
            print("rectangles recu du front",rectangles)
            doc = Document.objects.get(id=doc_id)
            registered_rectangles = list(Rectangle.objects.filter(document=doc))

            existing_id_rectangles=[]
            # Process each rectangle data to update or create
            for rect_data in rectangles:
                rect_id = rect_data.get('rectid')

                if rect_id !=-1:
                    existing_id_rectangles.append(int(rect_id))
                    # Update existing rectangle
                    rect = Rectangle.objects.get(id=rect_id)
                    rect.x = rect_data['x']
                    rect.y = rect_data['y']
                    rect.width = rect_data['width']
                    rect.height = rect_data['height']
                    rect.angle = rect_data['angle']
                    rect.save()
                else:
                    # Create new rectangle
                    Rectangle.objects.create(
                        document=doc,
                        x=rect_data['x'],
                        y=rect_data['y'],
                        width=rect_data['width'],
                        height=rect_data['height'],
                        angle=rect_data['angle']
                    )

            for i in registered_rectangles:
                if(i.id not in existing_id_rectangles):
                    print("del",i,i.id)
                    i.delete()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error saving rectangles: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def main_page(request):
    visible_projects=[]
    hidden_projects=[]
    projects = Project.objects.all()
    for project in projects:
        if project.name.startswith("hidden|"):
            hidden_projects.append(project)
        else:
            visible_projects.append(project)

    return render(request, 'local/main.html', {"projects":visible_projects,"hidden_projects":hidden_projects})

@login_required #TODO pas forcement mais faudrait etre co pour postuler
def project_page(request,project_id):

    user = User.objects.get(id=request.user.id)
    project = Project.objects.get(id=project_id)

    # if already a task in progress direct link to it
    existing_tasks = Task.objects.filter(user=user,status='in_progress')

    to_continue=[]
    to_continue_type = ""
    for existing_task in existing_tasks:
        if existing_task.document.project == project:
            # print("tache existante")
            to_continue.append(existing_task.document)
            to_continue_type = existing_task.type

    try:
        UsrPrj = UserProject.objects.get(user=user, project=project)
        role = UsrPrj.role

    except UserProject.DoesNotExist:
        role = "visitor" #TODO ou creer en db à ce moment là mais ? jsp peut etre mieux pas pour ne pas avoir trop de reccord useless en db

    members_list=[]
    full_members_list = UserProject.objects.filter(project=project)
    for member in full_members_list:
        if member.role in ["manager", 'verifier', 'transcriber']:
            members_list.append(member)


    #TODO filter pour avoir que les projets ou le users peut avoir +/-
    # to_transcribe = Document.objects.filter(project=project_id,status="to_transcribe")
    # in_transcription = Document.objects.filter(project=project_id,status="in_transcription")
    # to_verify =  Document.objects.filter(project=project_id,status="to_verify")
    # in_verification = Document.objects.filter(project=project_id, status="in_verification")
    # done = Document.objects.filter(project=project_id,status="completed")
    statuses = ["to_transcribe", "in_transcription", "to_verify", "in_verification", "completed"]

    documents_by_status = {}
    size = {}

    # Filtrer les documents par statut et les organiser par group_name
    for status in statuses:
        # Filtrer les documents pour chaque statut
        documents = Document.objects.filter(project=project_id, status=status)
        size[status] = len(documents)

        # Utiliser defaultdict pour regrouper les documents par group_name
        dico_by_group = defaultdict(list)
        for document in documents:
            dico_by_group[document.group_name].append(document)

        # Stocker le dictionnaire regroupé dans le dictionnaire principal
        documents_by_status[status] = dict(dico_by_group)

    # Maintenant, tu peux accéder aux documents regroupés par group_name pour chaque statut, par exemple :
    to_transcribe = documents_by_status["to_transcribe"]
    in_transcription = documents_by_status["in_transcription"]
    to_verify = documents_by_status["to_verify"]
    in_verification = documents_by_status["in_verification"]
    completed = documents_by_status["completed"]

    # Si tu veux afficher les résultats par statut et group_name
    total = size["to_transcribe"] + size["in_transcription"] + size["to_verify"] + size["in_verification"] + size["completed"]

    return render(request, 'local/project.html', { "to_transcribe":documents_by_status["to_transcribe"],
                                                   "in_transcription":in_transcription,
                                                   "to_verify":to_verify,
                                                   "in_verification":in_verification,
                                                   "to_continue":to_continue,
                                                   "done":completed,
                                                   "role":role,
                                                   "to_continue_type" : to_continue_type,
                                                   "project":{"id":project_id,"name":project.name,'description':project.description},
                                                   "members_list":members_list,
                                                   "progress":{"total":total,"completed":size["completed"],"verification":size["to_verify"],"current":size["in_verification"]+size["in_transcription"],"new":size["to_transcribe"]}, #TODO CLEAN
                                                   "progress_percent":{"completed":size["completed"]*100/total,"verification":size["to_verify"]*100/total,"current":(size["in_verification"]+size["in_transcription"])*100/total,"new":size["to_transcribe"]*100/total}
                                                   }
                  )

# @login_required()
class VerificationPage(View):
    template_name = "local/verification.html"
    def get(self, request, doc_id):
        user = request.user
        document = Document.objects.get(pk=doc_id)

        if document.status == "to_verify": #debut de la verif
            transcription_same_user = Task.objects.filter(document=document, type="transcription", user=request.user)
            if(len(transcription_same_user)>0): #not same user transcription and verif
                # return HttpResponseForbidden() #TODO
                pass

            task = Task()
            task.document = document
            task.ended = now() + timedelta(hours=1)
            task.user = request.user
            task.type = 'verification'
            task.save()
            document.status = 'in_verification'
            document.save()

        elif document.status == "in_verification": #load a save
            task = Task.objects.filter(document=document, status='in_progress',type='verification')[0]
            if task.user != user:
                return HttpResponseForbidden()
        else:
            return HttpResponseForbidden()

        #generate data
        image = document.image
        rectangles = Rectangle.objects.filter(document=doc_id)
        forms = [(rect, TextForm(instance=rect)) for rect in rectangles]
        # TODO get les object subtask correct pour donner au templates les text des autres task

        transcription_data = []  # liste des textes des rectangles correspondant

        for rect in rectangles:
            current_subtask = ""
            try:
                # print(rect)
                current_subtask = Subtask.objects.filter(rectangle=rect,status='in_progress')[0].text
            except Exception as e:
                print(e)
            # print("current",current_subtask)
            rectangle_data = {
                "current":current_subtask,
                "rectangle_id": rect.id,  # Inclure l'ID du rectangle
                "subtasks": [],  # Liste des subtasks
                "done": rect.done,
            }

            subtasks = Subtask.objects.filter(rectangle=rect,status="completed")
            print("=",subtasks)

            # POUR AVOIR TOUT L HISTORIQUE DE PROPOSITIONS
            # for subtask in subtasks:
            #     rectangle_data["subtasks"].append({
            #         "subtask_id": subtask.id,
            #         "text": subtask.text,
            #     })

            #QUE LA DERNIER PROPOSITION
            subtask = subtasks[len(subtasks)-1]
            rectangle_data["subtasks"].append({
                        "subtask_id": subtask.id,
                        "text": subtask.text,
                    })

            transcription_data.append(rectangle_data)

        # Prepare rectangle data as a list of dictionaries
        rectangles_data = [
            {
                "x": rect.x,
                "y": rect.y,
                "width": rect.width,
                "height": rect.height,
                "angle": rect.angle,
                "id": rect.id
            }
            for rect in rectangles
        ]

        return render(request, self.template_name, {
            'image': image,
            'transcription_data': transcription_data,
            'rectangles_data': rectangles_data,
            'forms': forms
        })



    def post(self, request, doc_id):
        document = Document.objects.get(pk=doc_id)
        task = Task.objects.get(document=document, status='in_progress')

        change = False
        save = True

        to_del=[]

        for key, text_value in request.POST.items():
            if key.startswith("submit"):
                document.status = 'completed'
                document.save()
                task.status = 'completed'
                task.save()
                save = False

        for key, text_value in request.POST.items():
            print(key,text_value)
            if key in ["csrfmiddlewaretoken", 'submit', 'save']:
                continue

            if(key.startswith('del')):
                rect_id = int(key.split("del_")[1])
                rectangle = Rectangle.objects.get(id=rect_id)
                to_del.append(rectangle)
                print("id rectangle à supprimer : ", rectangle)

            if(key.startswith('rect_')):
                rect_id = key.split("rect_")[1]

                if text_value != '':
                    change = True
                    rectangle = Rectangle.objects.get(id=rect_id)
                    verif_subtask = Subtask.objects.get_or_create(rectangle=rectangle, task=task)[0]
                    # verif_subtask.task = task
                    # verif_subtask.rectangle = Rectangle.objects.get(id=rect_id)

                    if (not save):
                        verif_subtask.status = 'completed'
                    verif_subtask.text = text_value
                    verif_subtask.save()
                else:  # si pas de modif pour ce rectangle
                    if not save:
                        rect = Rectangle.objects.get(id=rect_id)
                        rect.done = True
                        rect.save()

                if change and not save:
                    document.status = 'to_verify'

                task.save()
                document.save()

        for elem in to_del:
            elem.delete()

        return redirect('/project/' + str(document.project.id))  # Rediriger après le succès


def completed_page(request,doc_id):
    document = get_object_or_404(Document,pk=doc_id)

    try:
        get_object_or_404(UserPost, related_document=document).id
        general_forum = doc_id
    except Exception as e:
        general_forum =''


    if(document.status != 'completed'):
        return HttpResponseForbidden()
    image = document.image
    rectangles = Rectangle.objects.filter(document=doc_id)

    transcription_data = []  # liste des textes des rectangles correspondant
    rectangles_forum = []

    for rect in rectangles:

        rectangle_data = {
            'forum':'',
            "rectangle_id": rect.id,  # Inclure l'ID du rectangle
            "subtasks": [],  # Liste des subtasks
        }
        try:
            get_object_or_404(UserPost, related_rectangle=rect).id
            rectangle_data['forum'] = rect.id
        except Exception as e:
            pass

        subtasks = Subtask.objects.filter(rectangle=rect)

        for subtask in subtasks:
            rectangle_data["subtasks"].append({
                "subtask_id": subtask.id,
                "text": subtask.text,
            })
        transcription_data.append(rectangle_data)

    # Prepare rectangle data as a list of dictionaries
    rectangles_data = [
        {
            "x": rect.x,
            "y": rect.y,
            "width": rect.width,
            "height": rect.height,
            "angle": rect.angle,
            "id": rect.id
        }
        for rect in rectangles
    ]

    return render(request, 'local/completed.html', {
        'doc_id':doc_id,
        'image': image,
        'transcription_data': transcription_data,
        'rectangles': rectangles_data,
        'general_forum':general_forum,
        "rectangles_forum":rectangles_forum #TODO remove pcq 99% sure useless
    })

def export_data(request,export,type,id):

    response = HttpResponse(content_type='text/csv')
    if(export=="csv" and type=="document"):
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name image', 'x', 'y', 'width', 'height', 'angle', 'text'])
        rectangles = Rectangle.objects.filter(document=id)

        for rectangle in rectangles:
            subtasks = Subtask.objects.filter(rectangle=rectangle)
            writer.writerow([rectangle.document.image,rectangle.x,rectangle.y,rectangle.width,rectangle.height,rectangle.angle,subtasks[len(subtasks)-1].text])

    elif(export=="txt" and type=="document"):
        response['Content-Disposition'] = 'attachment; filename="export.txt"'
        rectangles = Rectangle.objects.filter(document=id)

        for rectangle in rectangles:
            subtasks = Subtask.objects.filter(rectangle=rectangle)
            response.write(str(subtasks[len(subtasks) - 1].text)+'\n')

    elif(type=="project"):
        pass
    else:
        return HttpResponseForbidden()
    return response


def help(request):
    return render(request, 'local/help.html')

def about(request):
    return render(request, 'local/about.html')

def preview_page(request,doc_id):
    document = get_object_or_404(Document, pk=doc_id)

    image = document.image
    return render(request, 'local/preview.html',context={'image': image})