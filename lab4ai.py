

-----------------------------------------------------------# **Cerinta 1**----------------------------------------------------------------------------------------
#Sa se foloseasca un algoritm de clasificare a imaginilor (etapa de inferenta/testare) si sa se stabileasca performanta acestui algoritm de clasificare binara (imagini cu biciclete vs. imagini fara biciclete).


from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
from msrest.authentication import CognitiveServicesCredentials
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Model
from array import array
import cv2
import os
from PIL import Image
import sys
import time
import matplotlib.pyplot as plt
from skimage import io
import numpy as np


def Authenticate():
  subscription_key = os.environ["KEY"]
  endpoint = os.environ["ENDPOINT"]
  computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


def evaluateClassification(realLbl, computedLbl, lbl):
  confusionMatrix = confusion_matrix(realLbl,computedLbl, labels = lbl)
  accuracy = accuracy_score(realLbl, computedLbl)
  precision = precision_score(realLbl,computedLbl, average =None, labels = lbl)
  recall = recall_score(realLbl,computedLbl, average=None,labels=lbl)
  return accuracy, precision, recall


from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras.models import Model
def getPredictions(imgPath, labels):
    model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    x = model.output
    x = GlobalAveragePooling2D()(x)
    predictions = Dense(1, activation='sigmoid')(x)
    model = Model(inputs=model.input, outputs=predictions)
    image = cv2.imread(imgPath)
    image = cv2.resize(image, (224, 224))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.expand_dims(image, axis=0)
    image = preprocess_input(image)
    # Make predictions
    prob = model.predict(image)[0][0]
    if prob >= 0.5:
        return "bike"
    else:
        return "no_bike"


def predictionsAccuracy(folderPath,realLabels,labels):
  images = os.listdir(folderPath)
  allMetrics = []
  computedLabels = []
  for img in images:
      imgPath = os.path.join(folderPath, img)
      predictions = getPredictions(imgPath, labels)
      computedLabels.append(predictions)  # Append predictions for the current image
  realLabels = [str(label) for label in realLabels]
  computedLabels = [str(label) for label in computedLabels]
  labels = [str(label) for label in labels]
  accuracy, precision, recall = evaluateClassification(realLabels, computedLabels, labels)
  metrics = {'accuracy:': accuracy, "precision:": precision, 'recall:': recall}
  return metrics



def main():
  realLabels = ["bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike","no_bike","no_bike","no_bike","no_bike","no_bike","no_bike","no_bike","no_bike","no_bike","no_bike"]
  labels = ["bike", "no_bike"]
  allMetrics = predictionsAccuracy("/content/images/images/bikes",realLabels,labels)
  print(allMetrics)
main()






"""
-----------------------------------------------------------# **Cerinta 2**--------------------------------------------------------------------------------------------
Pentru imaginile care contin biciclete:

a. sa se localizeze automat bicicletele in aceste imagini si sa se evidentieze chenarele care incadreaza bicicletele

b. sa se eticheteze (fara ajutorul algoritmilor de AI) aceste imagini cu chenare care sa incadreze cat mai exact bicicletele. Care task dureaza mai mult (cel de la punctul a sau cel de la punctul b)?
"""

from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score
from msrest.authentication import CognitiveServicesCredentials
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Model
from array import array
import cv2
import os
from PIL import Image
import sys
import time
import matplotlib.pyplot as plt
from skimage import io
import numpy as np


def Authenticate():
  subscription_key = os.environ["KEY"]
  endpoint = os.environ["ENDPOINT"]
  computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
  return computervision_client


import io
import os
import time
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
def getBoundingBoxes(folderPath):
  start_time = time.time()
  computervision_client = Authenticate()
  images = os.listdir(folderPath)
  images.sort()
  realLabels = ["bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike"]
  computedLabels = []
  for img in images:
      try:
          imgPath = os.path.join(folderPath, img)
          image = cv2.imread(imgPath)
          if realLabels[images.index(img)] == "bike":
              print(images.index(img))
              with io.BytesIO() as output:
                  ret, buffer = cv2.imencode('.jpg', image)
                  image_stream = io.BytesIO(buffer)
                  result = computervision_client.analyze_image_in_stream(image_stream, visual_features=[VisualFeatureTypes.objects])
                  fig, ax = plt.subplots(1)
                  ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))  # Convert BGR to RGB for plotting
                  for ob in result.objects:
                      bikeBb = [ob.rectangle.x, ob.rectangle.y, ob.rectangle.x + ob.rectangle.w, ob.rectangle.y + ob.rectangle.h]
                      rect = patches.Rectangle((bikeBb[0], bikeBb[1]), bikeBb[2]-bikeBb[0], bikeBb[3]-bikeBb[1], linewidth=1, edgecolor='r', facecolor='none')
                      ax.add_patch(rect)
                  plt.show()
      except Exception as e:
          print(f"Error processing image {img}: {e}")
          continue
  end_time = time.time()
  execution_time = end_time - start_time
  print("Timpul de executie: " + str(execution_time))
  return realLabels



def findEdges(imgPath):
    image = cv2.imread(imgPath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    withEdges = cv2.Canny(blurred, 10, 100)
    return withEdges


import cv2
from google.colab.patches import cv2_imshow
import time
def detectBicycle(folderPath):
    realLabels = ["bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike", "no_bike"]
    start_time = time.time()
    images = os.listdir(folderPath)
    images.sort()
    for img in images:
      image_path = os.path.join(folderPath,img)
      image = cv2.imread(image_path)
      if realLabels[images.index(img)]=="bike":
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        potential_bicycles = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 60:  #treshold
                potential_bicycles.append(contour)
        cv2.drawContours(image, potential_bicycles, -1, (0, 255, 0), 2)
        cv2_imshow(image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    end_time = time.time()
    execution_time = end_time - start_time
    print("Timpul de executie: " +  str(execution_time))


def main():
  getBoundingBoxes("/content/images/images/bikes")
  #detectBicycle("/content/images/images/bikes")
main()

