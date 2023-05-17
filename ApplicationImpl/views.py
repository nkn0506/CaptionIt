from django.shortcuts import render
from django.http import HttpResponse
from ApplicationImpl.models import UserDetails
import re
# Create your views here.
from django.core.files.storage import FileSystemStorage

from django.conf import settings
from django.conf.urls.static import static
############################################################
#library Import
from pickle import load
from keras.models import load_model
from keras.applications.xception import Xception
from keras_preprocessing.sequence import pad_sequences
import numpy as np
from PIL import Image
import warnings
warnings.filterwarnings('ignore')

import urllib.request

def extract_features(filename, model):
    image=Image.open(settings.STATIC_DIR/ 'image/logo.png')
    try:
        if (isinstance(filename, str)):
            urllib.request.urlretrieve(filename, settings.STATIC_DIR/ 'image/temp_image.png')
            image = Image.open(settings.STATIC_DIR/ 'image/temp_image.png')
        else:
            image = Image.open(filename)
    except:
        print("ERROR: Couldn't open image! Make sure the image path and extension is correct")
    image = image.resize((299, 299))
    image = np.array(image)
    # for images that has 4 channels, we convert them into 3 channels
    if image.shape[2] == 4:
        image = image[..., :3]
    image = np.expand_dims(image, axis=0)
    image = image / 127.5
    image = image - 1.0
    feature = model.predict(image)
    return feature

def word_for_id(integer, tokenizer):
  for word, index in tokenizer.word_index.items():
    if index == integer:
      return word
  return None

def generate_desc(model, tokenizer, photo, max_length):
    in_text = 'start'
    for i in range(max_length):
        sequence = tokenizer.texts_to_sequences([in_text])[0]
        sequence = pad_sequences([sequence], maxlen=max_length)
        pred = model.predict([photo,sequence], verbose=0)
        pred = np.argmax(pred)
        word = word_for_id(pred, tokenizer)
        if word is None:
            break
        in_text += ' ' + word
        if word == 'end':
            break
    return in_text

############################################################
def about(request):
    return render(request, 'FrontPage.html')

def signup(request):
    if request.method=='POST':
        name = request.POST['name']
        mobile = request.POST['mobile']
        email = request.POST['email']
        password = request.POST['password']
        description=''
        mobpat='[6-9][0-9]{9}'
        emailpat = "^[a-zA-Z0-9-_]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
        passpat= "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,18}$"
        '''''
        Please enter password should be
           1) One Capital Letter
           2) Special Character
           3) One Number
           4) Length Should be 8-18:
             ex: asd@Asda
        '''''
        #if ((not re.match(emailpat, email)) or (not re.match(mobpat, mobile)) or (not re.match(passpat, password))):
         #   return render(request, 'popup.html')
        if (name=='' or mobile=='' or email=='' or password==''):
            return "Try again"
        alldata = UserDetails.objects.all()
        exit_loop=0
        for x in alldata:
            if (x.email == email and x.password==password):
                exit_loop=1
                break
        if (exit_loop==1):
            return render(request, 'popup.html')
        else:
            ins = UserDetails(name=name, mobile=mobile, email=email, password=password, description=description)
            ins.save()
            return render(request, 'SignUp.html')
    return render(request, 'SignUp.html')

def feedback(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        description= request.POST["text_area"]
        if(len(email)==0 or len(password) == 0 or len(description)==0):
            return render(request, 'popup.html')
        alldata = UserDetails.objects.all()
        finded=0
        for x in alldata:
            if (x.email == email  and password==password):
                x.description=description
                x.save()
                finded=1
                break;
            if(finded==0):
                return render(request, 'popup.html')
    return render(request, 'Feedback.html')

def frontpage(request):
    return render(request, 'FrontPage.html')

def login(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        alldata = UserDetails.objects.all()
        if(len(email)==0 or len(password) == 0):
            return render(request, 'login.html')
        finded=0
        for x in alldata:
            if (x.email == email  and x.password == password):
                finded=1
                return render(request, 'prediction.html')
            elif(finded==1):
                break
    return render(request, 'login.html')

def forget(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        passpat = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,18}$"
        if(len(email)==0 or len(password)==0 or (not re.match(passpat, password))):
            return render(request, 'popup.html')
        alldata = UserDetails.objects.all()
        finded=0
        for x in alldata:
            if (x.email == email):
                finded=1
                x.password=password
                x.save()
                break
        if(finded==0):
            return render(request, 'SignUp.html')
        else:
            return render(request, 'login.html')
    return render(request, 'forget.html')

def prediction(request):
    if request.method == "POST":
        max_length = 32
        loc1 = settings.MODEL_FILES_ROOT / "tokenizer.pkl"
        loc2 = settings.MODEL_FILES_ROOT / "model_new_19.h5"
        tokenizer = load(open(loc1, "rb"))
        model = load_model(loc2)
        xception_model = Xception(include_top=False, pooling="avg")
        chooser_file = request.POST['locationInput']
        result=""
        if(chooser_file==""):
            uploaded_file = request.FILES['uploadedImage']
            photo = extract_features(uploaded_file, xception_model)
            description = generate_desc(model, tokenizer, photo, max_length)
            result=description
        else:
            uploaded_file = chooser_file
            photo = extract_features(uploaded_file, xception_model)
            description = generate_desc(model, tokenizer, photo, max_length)
            result=description
        des = result.split(' ')
        des = des[1:-1]
        result = ' '.join(des)
        return render(request, 'prediction.html', {"result": result})
    des="No Result"
    return render(request, 'prediction.html', {"result": des})


