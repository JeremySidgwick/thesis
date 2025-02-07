import csv

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponse

from forum.models import UserPost
from .forms import ImageUploadForm, TextForm
from .models import Document, Rectangle, Task, Subtask, Project, UserProject
from datetime import timedelta
import json
from django.contrib.auth.decorators import login_required
from authentication.models import User
from django.views.generic import View


#TODO to delete
def upload_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = ImageUploadForm()
    return render(request, 'local/upload_image.html', {'form': form})




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
            'image': image,
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

#
# @login_required()
# def transcription_page(request, doc_id):
#
#     #TODO check user
#     #TODO check si pas ok niveau task
#     document = get_object_or_404(Document, pk=doc_id)
#     if document.status not in ["to_transcribe","in_transcription"]:
#         return HttpResponseForbidden()
#     try:
#         tasks = Task.objects.filter(document=document,status='in_progress',type='transcription')
#         if(len(tasks)>1):
#             print('|', tasks, '|')
#             print("trop de resultats")
#             return None
#
#         task= tasks[0]
#
#         if task.user != request.user:
#             return HttpResponseForbidden()
#     except Exception as e:
#         print(e)
#         task=Task()
#         task.document = document
#         task.ended = now() + timedelta(hours=1)
#         task.user = request.user
#         task.save()
#         #TODO task.ended + check le started at + user
#
#     document.status = 'in_transcription'
#     document.save()
#     image = document.image
#
#     if request.method == 'POST':
#         for key, text_value in request.POST.items():
#             if key.startswith("submit"):
#                 document.status = 'to_verify'
#                 document.save()
#                 task.status = 'completed'
#                 task.save()
#
#             if key.startswith('rect_'):  # Identifier les champs par un préfixe unique
#                 rect_id = key.split('_')[1]  # Extraire l'ID du rectangle
#                 try:
#                     rectangle = Rectangle.objects.get(id=rect_id)
#                     existing_subtasks = Subtask.objects.filter(task=task, rectangle=rectangle)
#                 except Rectangle.DoesNotExist:
#                     print("Rectangle with ID", rect_id, "does not exist")
#                     continue
#                 if(len(existing_subtasks)>0):
#                     print("existing_subtasks", existing_subtasks)
#                     sub = existing_subtasks[0]
#                 else:
#                     print("creating subtask with rectangle", rectangle.id, "with value:", text_value)
#                     sub = Subtask()
#                     sub.task = task
#                     sub.rectangle = rectangle
#                 sub.text = text_value
#                 sub.save()
#
#         return redirect('/project/'+str(document.project.id))  # Rediriger après le succès
#
#
#     # Récupérer tous les rectangles pour le formulaire
#     rectangles = Rectangle.objects.filter(document=doc_id)
#
#
#     forms = []
#     for rect in rectangles:
#         text_value = ""
#         try:
#             subtask = Subtask.objects.get(task=task, rectangle=rect)
#             print(subtask)
#             text_value = subtask.text
#         except Exception as e:
#             pass
#
#         forms.append((rect, TextForm(instance=rect),text_value))
#
#     # Prepare rectangle data as a list of dictionaries
#     rectangles_data = [
#         {
#             "x": rect.x,
#             "y": rect.y,
#             "width": rect.width,
#             "height": rect.height,
#             "angle": rect.angle,
#             "id": rect.id
#         }
#         for rect in rectangles
#     ]
#
#     return render(request, 'local/transcription.html', {
#         'image': image,
#         'rectangles': rectangles_data,
#         'forms': forms,
#     })

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
    projects = Project.objects.all()
    return render(request, 'local/main.html', {"projects":projects})

@login_required #TODO pas forcement mais faudrait etre co pour postuler
def project_page(request,project_id):

    user = User.objects.get(id=request.user.id)
    project = Project.objects.get(id=project_id)

    # if already a task in progress direct link to it
    existing_tasks = Task.objects.filter(user=user,status='in_progress')
    print("existing_tasks 163",existing_tasks)
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


    #TODO filter pour avoir que les projets ou le users peut avoir +/-
    to_transcribe = Document.objects.filter(project=project_id,status="to_transcribe")
    in_transcription = Document.objects.filter(project=project_id,status="in_transcription")
    to_verify =  Document.objects.filter(project=project_id,status="to_verify")
    in_verification = Document.objects.filter(project=project_id, status="in_verification")
    done = Document.objects.filter(project=project_id,status="completed")

    return render(request, 'local/project.html', { "to_transcribe":to_transcribe,
                                                                        "in_transcription":in_transcription,
                                                                        "to_verify":to_verify,
                                                                        "in_verification":in_verification,
                                                                        "to_continue":to_continue,
                                                                        "done":done,
                                                                        "role":role,
                                                                        "to_continue_type" : to_continue_type,
                                                                        "project":{"id":project_id,"name":project.name,'description':project.description},
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
            print("111",task)
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
        print(request.POST.items())
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

#
# @login_required()
# def verification_page(request, doc_id):
#     document = get_object_or_404(Document, pk=doc_id)
#
#     #check user
#     previous_transcription = Task.objects.filter(document=document, type="transcription",user=request.user)
#     if len(previous_transcription) >0:
#         pass
#         # return HttpResponseForbidden("Vous ne pouvez pas verifier un document que vous avez transcrit")
#         #TODO soit uncomment le return + changer le filter de la project page pour pas afficher au user ce qu'il peut pas
#
#     if document.status not in ["to_verify","in_verification"]:
#         return HttpResponseForbidden()
#     try:
#         tasks = Task.objects.filter(document=document, status='in_progress',
#                                     type='verification')  # TODO modif pour le user
#         if (len(tasks) > 1):
#             print('|',tasks,'|')
#             print("trop de resultats")
#             return None
#
#         task = tasks[0]
#         if task.user != request.user:
#             return HttpResponseForbidden()
#     except Exception as e:
#         task = Task()
#         task.document = document
#         task.ended = now() + timedelta(hours=1)
#         task.user = request.user
#         task.type = 'verification'
#         task.save()
#         # TODO task.ended + check le started at + user
#     document.status = 'in_verification'
#     document.save()
#     image = document.image
#
#
#
#     if request.method == 'POST':
#         print("post", request.POST)
#         #TODO HERE gerer le submit du form de verification
#         # task done
#         change= False
#         save = False
#         # if all submit are empty then document done,
#         print(request.POST.items())
#         if "save" in request.POST.items():
#             save = True
#             print('SUBMIT')
#
#         for key, text_value in request.POST.items():
#             if key in ["csrfmiddlewaretoken",'submit','save']:
#                 continue
#             rect_id = key.split("rect_")[1]
#             if text_value !='':
#                 change=True
#                 verif_subtask = Subtask.objects.get_or_create(rectangle=Rectangle.objects.get(id=rect_id), task=task)[0]
#
#                 verif_subtask.task = task
#                 verif_subtask.rectangle = Rectangle.objects.get(id=rect_id)
#                 # if()
#                 if(not save):
#                     verif_subtask.status = 'completed'
#                 verif_subtask.text = text_value
#                 verif_subtask.save()
#             else: #si pas de modif pour ce rectangle
#                 rect = Rectangle.objects.get(id=rect_id)
#                 rect.done = True
#                 rect.save()
#
#             # else document status = to verify
#             # print("change",change)
#             if change or save:
#                 document.status = 'to_verify'
#             else:
#                 document.status = 'completed'
#             if save:
#                 task.status = 'completed'
#             task.save()
#             document.save()
#
#         return redirect('/project/'+str(document.project.id))  # Rediriger après le succès
#
#     # Récupérer tous les rectangles pour le formulaire
#     rectangles = Rectangle.objects.filter(document=doc_id)
#     forms = [(rect, TextForm(instance=rect)) for rect in rectangles]
#     #TODO get les object subtask correct pour donner au templates les text des autres task
#
#     transcription_data=[] #liste des textes des rectangles correspondant
#
#     for rect in rectangles:
#         rectangle_data = {
#             "rectangle_id": rect.id,  # Inclure l'ID du rectangle
#             "subtasks": [],  # Liste des subtasks
#             "done": rect.done,
#         }
#
#         subtasks = Subtask.objects.filter(rectangle=rect)
#
#         for subtask in subtasks:
#             rectangle_data["subtasks"].append({
#                 "subtask_id": subtask.id,
#                 "text": subtask.text,
#             })
#
#         transcription_data.append(rectangle_data)
#
#     # Prepare rectangle data as a list of dictionaries
#     rectangles_data = [
#         {
#             "x": rect.x,
#             "y": rect.y,
#             "width": rect.width,
#             "height": rect.height,
#             "angle": rect.angle,
#             "id": rect.id
#         }
#         for rect in rectangles
#     ]
#
#     print(rectangles_data)
#     return render(request, 'local/verification.html', {
#         'image': image,
#         'transcription_data':transcription_data,
#         'rectangles_data': rectangles_data,
#         'forms': forms
#     })


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
        "rectangles_forum":rectangles_forum
    })



def export_data(request,type,id):
    print(type,id)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name image', 'x', 'y', 'width', 'height', 'angle', 'text'])

    if(type=="document"):
        # document = Document.objects.filter(pk=id)
        rectangles = Rectangle.objects.filter(document=id)
        print("rectangles:",rectangles)
        for rectangle in rectangles:
            subtasks = Subtask.objects.filter(rectangle=rectangle)
            print('subtasks:',subtasks)
            print(rectangle.document.image,rectangle.x,rectangle.y,rectangle.width,rectangle.height,rectangle.angle,subtasks[len(subtasks)-1].text)
            writer.writerow([rectangle.document.image,rectangle.x,rectangle.y,rectangle.width,rectangle.height,rectangle.angle,subtasks[len(subtasks)-1].text])
    elif(type=="project"):
        pass
    else:
        return HttpResponseForbidden()
    return response


def help(request):
    return render(request, 'local/help.html')