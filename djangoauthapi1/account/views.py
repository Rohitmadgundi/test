from typing import Any
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from account.serializers import SendPasswordResetEmailSerializer, UserChangePasswordSerializer, UserLoginSerializer, UserPasswordResetSerializer, UserProfileSerializer, UserRegistrationSerializer
from django.contrib.auth import authenticate
from account.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score
from sklearn import tree
from sklearn.svm import SVC
from sklearn.tree import _tree
import numpy as np
import re
from .serializer import ContactSerializer
from rest_framework import viewsets
from .models import Contact
from django.core.mail import send_mail

# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }

# def send():
#   send_mail(
#       "Subject here",
#       "Here is the message.",
#       "madgundirohit@gmail.com",
#       ["rohitmadgundi@gmail.com"],
#       fail_silently=False,
#   )
# send()
class ContactModelViewSet(viewsets.ModelViewSet):
    # print("gelll")
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class UserRegistrationView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserRegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = get_tokens_for_user(user)
    return Response({'token':token, 'msg':'Registration Successful'}, status=status.HTTP_201_CREATED)

class UserLoginView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.data.get('email')
    password = serializer.data.get('password')
    user = authenticate(email=email, password=password)
    if user is not None:
      token = get_tokens_for_user(user)
      return Response({'token':token, 'msg':'Login Success'}, status=status.HTTP_200_OK)
    else:
      return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfileView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def get(self, request, format=None):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)

class UserChangePasswordView(APIView):
  renderer_classes = [UserRenderer]
  permission_classes = [IsAuthenticated]
  def post(self, request, format=None):
    serializer = UserChangePasswordSerializer(data=request.data, context={'user':request.user})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Changed Successfully'}, status=status.HTTP_200_OK)

class SendPasswordResetEmailView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, format=None):
    serializer = SendPasswordResetEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset link send. Please check your Email'}, status=status.HTTP_200_OK)

class UserPasswordResetView(APIView):
  renderer_classes = [UserRenderer]
  def post(self, request, uid, token, format=None):
    serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
    serializer.is_valid(raise_exception=True)
    return Response({'msg':'Password Reset Successfully'}, status=status.HTTP_200_OK)


class Name(APIView):
  def post(self, request, uid, token, format=None):
    return Response({'message':'Hello '}, status=status.HTTP_200_OK)
   

class Predict(APIView):
  def __init__(self):
    self.training = pd.read_csv(r'D:\rohit\test\djangoreactjsauth1\djangoauthapi1\account\dataset\training.csv',delimiter=",",index_col=0).fillna(0)
    # self.rohit = 10
    # print(self.rohit)
    self.cols= self.training.columns
    self.cols= self.cols[:-1]
    self.x = self.training[self.cols]
    self.y = self.training['Prognosis']

    self.x_train, x_test, y_train, y_test = train_test_split(self.x, self.y, test_size=0.33, random_state=42)

    self.classifier  = DecisionTreeClassifier()

    self.classifierModel = self.classifier.fit(self.x_train.values,y_train.values)
    self.scores = cross_val_score(self.classifierModel, x_test, y_test, cv=3)
    self.features = self.x_train.columns
    self.svcModel=SVC()
    self.svcModel.fit(self.x_train.values,y_train.values)
    self.severities = pd.read_csv(r'D:\rohit\test\djangoreactjsauth1\djangoauthapi1\account\dataset\Symptom-severity.csv',delimiter=",")
    self.descriptions = pd.read_csv(r'D:\rohit\test\djangoreactjsauth1\djangoauthapi1\account\dataset\symptom_Description.csv',delimiter=",")
    self.precautions = pd.read_csv(r'D:\rohit\test\djangoreactjsauth1\djangoauthapi1\account\dataset\symptom_precaution.csv',delimiter=",")
    self.diseasesData = pd.read_csv(r'D:\rohit\test\djangoreactjsauth1\djangoauthapi1\account\dataset\dataset.csv',delimiter=",")
    self.precautions.set_index("Disease",inplace=True)
    self.descriptions.set_index("Disease",inplace=True)

    self.modelTree = self.classifierModel.tree_

    self.groupedData = self.training.groupby(self.training['Prognosis']).max()
    self.le = preprocessing.LabelEncoder()
    self.le.fit(y_train)
    #y = le.transform(y)
      
  def walkTree(self,node, userInput):
    names = self.training.columns[:-1]
    featureNames = [
        names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in self.modelTree.feature
    ]

    if self.modelTree.feature[node] != _tree.TREE_UNDEFINED:
            name = featureNames[node]
            threshold = self.modelTree.threshold[node]
            if name.strip() == userInput.strip():
                val = 1
            else:
                val = 0
            if  val <= threshold:
                return self.walkTree(self.modelTree.children_left[node],userInput)
            else:
                return self.walkTree(self.modelTree.children_right[node], userInput)
    else:
        #print(modelTree.value[node])
        node = self.modelTree.value[node][0].nonzero()
        disease = self.le.inverse_transform(node[0])
        possibleDisease = disease[0]
        indices  = self.groupedData.loc[disease].values[0].nonzero()
        columnList = self.groupedData.columns.values[0]
        symptomSuggestions = [self.groupedData.columns.values[i] for i in indices][0]
        return (symptomSuggestions , possibleDisease) 
      
  def makePrediction(self,experiencedSymptoms):
    x = self.training.iloc[:, :-1]
    symptomsDict = {symptom.strip(): index for index, symptom in enumerate(x)}
    inputVector = np.zeros(len(symptomsDict))
    for s in experiencedSymptoms:
      inputVector[[symptomsDict[s]]] = 1
    #print(classifierModel.predict([inputVector]))
    return self.classifierModel.predict([inputVector])[0]
  
  def getRelatedSymptoms(self,userInput):
    result=[]
    # print(self.rohit)
    symptoms = self.severities['Symptom']
    userInput=userInput.replace(' ','_')
    pattern = f"{userInput}"
    regexp = re.compile(pattern)
    predictionList=[item.replace('_',' ') for item in symptoms if regexp.search(item)]
    # print("predictionList")
    # print(predictionList)
    # print("regexp")
    # print(regexp)
    # print("symptoms")
    # print(symptoms)
    if(len(predictionList)>0):
        return (True,predictionList)
    else:
        return (False, [])

  def getRelatedSymptomsFromUser(self):
    print("\nEnter the symptom you are experiencing \t\t",end="->") 
    userInput = input("") 
    return self.getRelatedSymptoms(userInput)

  def getSymptomsChoiceFromUser(self,relatedSymptoms):
    print("searches related to input: ") 
    for num, it in enumerate(relatedSymptoms): 
        print(num,")",it)
    i=0
    if num!=0: 
        print(f"Select the one you meant (0 - {num}): ", end="") 
        try:
            i = int(input("")) 
        except:
            pass
    else: 
        i=0 
    return relatedSymptoms[i]

  def getAdditionalSymptomsFromUser(self,symptomSuggestions):
    result = []
    print("Are you experiencing any ")
    # print(symptomSuggestions)
    for s in symptomSuggestions:
        inp=""
        print(s,"? : ",end='')
        while True:
            inp=input("")
            if(inp=="yes" or inp=="no"):
                break
            else:
                print("provide proper answers i.e. (yes/no) : ",end="")
            if(inp=="yes"):
                result.append(s)
    return result

  def printDiseaseRecommendation(self,disease):
    print("You may have ", disease)
    print(self.descriptions.loc[disease].values[0])
    print("Take the following precautions: ")
    for p in self.precautions.loc[disease].values:
        print("- " + str(p))

  def post(self, request, format=None):
    print("-----------------------------------HealthCare ChatBot-----------------------------------")
    print("\nWhat's your name? \t\t\t\t",end="->")
    
    # return Response({'message':'Hello welcome to chatbot enter your name'}, status=status.HTTP_200_OK)
    userName = input("Hello: ")
    print("Hello,",userName,"! Nice to see you!")
    while True:
        currentSymptom = "" 
        (result, relatedSymptoms) = self.getRelatedSymptomsFromUser()
        if result == True: 
            currentSymptom = self.getSymptomsChoiceFromUser(relatedSymptoms)
            (symptomSuggestions, possibleDisease) = self.walkTree(0, currentSymptom.replace(" ","_"))
            #print(symptomSuggestions,possibleDisease )
            additionalSymptoms = self.getAdditionalSymptomsFromUser(symptomSuggestions)
            #print(additionalSymptoms)
            otherPossibleDisease = self.makePrediction(additionalSymptoms)
            self.printDiseaseRecommendation(possibleDisease)
            if not possibleDisease == otherPossibleDisease:
                print("You may also have: \n")
                self.printDiseaseRecommendation(otherPossibleDisease)
                print("\n")
        break    
    return Response({'meg':'good'}, status=status.HTTP_200_OK)

     
# class Hello():
#   def __init(self):
#     self.x = 10
#   def print(self):
#      print(self.x)

