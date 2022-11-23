from django.shortcuts import render # Returns an HttpResponse whose content is filled with the result of calling the HTML file as the passed arguments.
# from django.http import HttpResponse 
from django.http.response import StreamingHttpResponse # It is a response whose body is sent to the client in multiple pieces, or “chunks.”
from django.core.files.storage import default_storage # Provides access to the current default storage system 
from ai.camera import VideoCamera # Importing the VideoCamera class from camera.py which will be used for streaming the real-time video captured which would detect whether the person is meditating or not; and also change the background while meditating
from ai.constants import * # Import all the constant variables from constant.py
from ai.forms import * # Import the forms required handle the data that will get uploaded
from ai.predict import * # Import all the functions from predict.py which will be used to predict the emotions from the audio files
from templates.ai import * # Import the template files
from django.contrib.auth.decorators import login_required
from accounts.models import Meditation, Health
from django.contrib.auth.models import Group
from accounts.decorator import *
# Create your views here.

TIME = 0
blinked = 0

@login_required(login_url='login')
def index(response): # View for the the home page
    return render(response, 'ai\index.html') # Renders the index.html for the home page

@login_required(login_url='login')
@allowed_users(allowed_roles=['meditator'])
def meditate(response): # View for the /meditate/ page
    if response.method == "POST":
        global TIME 
        TIME = int(response.POST['duration'])
        return render(response, 'ai\meditate.html') # Renders the meditate.html for the /meditate/ page
    else:
        return render(response, 'ai\pre_meditate.html')

def gen(camera, request): # Function to call a VideoCamera object to get the classification of the meditation
    global blinked
    while True: # THe loop will run until the finish trigger doesn't become true and it breaks the loop
        frame, finish, blink = camera.get_frame(rpred, lpred, lbl, lbl_pred) # Get the current frame and the trigger response
        if finish==True: # Means that the meditation is over

            profile = request.user.profile
            print(profile)
            Meditation.objects.create(
                profile = profile,
                duration = TIME,
                no_distracted = blinked,
                score = TIME - blinked
            )

            break # Breaks out of the loop
        blinked = blink
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n') # Yields the frame formatted as a response chunk with a content type of image/jpeg

def video_feed(request):
    # Returns the HttpResponse whose body is chunks from the response of gen(VideoCamera()) with 'multipart/x-mixed-replace' content type 
    # which is used for the purpose of having a real-time stream where each part replaces the previous part 
    return StreamingHttpResponse(gen(VideoCamera(TIME=TIME, blinked= blinked),request),
                    content_type='multipart/x-mixed-replace; boundary=frame')  

@login_required(login_url='login')
@allowed_users(allowed_roles=['meditator'])
def predict_emotions(request): # # View for the /pred_health/ page
    if request.method == "POST": # If the request method is POST, i.e, A POST request is typically sent via an HTML form and results in a change on the server
        # In our case, when the audio file is uploaded
        file = request.FILES["audioFile"] # Gets the file  and the file name
        file_name = default_storage.save(file.name, file) # Saves the file in default_storage
        file_url = str(default_storage.path(file_name)) # Gets the files url/path
        file_url= str('\\'.join(file_url.split('\\')[:-1])+'\\') # Formatting the file url
        ans = [] # Store the predictions in this list
        if os.listdir(BASE_DIR+'\media\\')!=[]: # If the directory media is not empty
            print('Sound exists!!!!!') 
            ans, duration = app(k,str(file_url),str(file_name)) # Predict the emotions 

        emotion = ""
        genders = ""

        for i in ans.values():
            s = i.split('_')
            genders+= s[0].title()+","
            emotion+= s[1].title()+", "

        profile = request.user.profile
    
        Health.objects.create(
                profile = profile,
                duration = duration,
                emotions = emotion[:-2],
                gender = genders.split(",")[0]
        )

        return render(request, "ai\predict.html", {"predictions": ans}) # Renders the predict.html for /pred_health/ page with the predictions

    else:
        return render(request, "ai\predict.html", {"predictions": 0}) # Renders the predict.html for /pred_health/ page without the predictions
    
    # return render(request, "ai\predict.html", {"predictions": 0}) # Renders the predict.html for /pred_health/ page without the predictions