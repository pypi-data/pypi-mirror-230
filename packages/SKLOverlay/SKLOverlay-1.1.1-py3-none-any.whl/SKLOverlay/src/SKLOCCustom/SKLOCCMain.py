from .SKLOCC_RF import *
from .SKLOCC_KN import *
from .SKLOCC_SVM import *
from .SKLOCC_SVML import *
from .SKLOCC_MLP import *


def Customize_Classifier_Batch(actClassInfo, batchNum):
    classifier = actClassInfo[1]
    classMods = actClassInfo[2]
    classifierNum = actClassInfo[3]
    if classifierNum == 1:
        classList = Mod_List_RF(batchNum, classMods)
    elif classifierNum == 2:
        classList = Mod_List_KN(batchNum, classMods)
    elif classifierNum == 3:
        classList = Mod_List_SVM(batchNum, classMods)
    elif classifierNum == 4:
        classList = Mod_List_SVML(batchNum, classMods)
    elif classifierNum == 5:
        classList = Mod_List_MLP(batchNum, classMods)
    else:
        print('|         Something went wrong. Defauulting to option 1.          |')
        classList = [classifier] * batchNum

    return classList


def Customize_Classifier(classifierNum, classifierNickname=''):
    if classifierNum == 1:
        if classifierNickname == '':
            classifierNickname = input("| Name new Random Forest Algorithm: ")
        return classifierNickname, Customization_RF()
    elif classifierNum == 2:
        if classifierNickname == '':
            classifierNickname = input("| Name new K-Neighbors Algorithm: ")
        return classifierNickname, Customization_KN()
    elif classifierNum == 3:
        if classifierNickname == '':
            classifierNickname = input("| Name new Support Vector Algorithm: ")
        return classifierNickname, Customization_SVM()
    elif classifierNum == 4:
        if classifierNickname == '':
            classifierNickname = input("| Name new Linear SVM: ")
        return classifierNickname, Customization_SVML()
    elif classifierNum == 5:
        if classifierNickname == '':
            classifierNickname = input("| Name new Neural Network: ")
        return classifierNickname, Customization_MLP()
    else:
        default = RandomForestClassifier()
        print('|      Unrecognized option chosen. Using default RF algorithm.    |')
        print('|        Please check current algorithms list if unwanted.        |')
        print('-------------------------------------------------------------------')
        return 'default', (default, {})


"""

List of Classifiers:
* Random Forest 
* KNeighborsClassifier
* NeighborhoodComponentsAnalysis (transform)
Gradient Boosting Classifier
Ada-Boost Classifier
Bagging Classifier
Isolation Forest Classifier
Voting Classifier
Stacking Classifier
Gaussian Process Classifier
Ridge Classifier
Precision Recall Display (results)
ROC Display (results)
K Folds verification (results)
Learning Curve display (results)
Gaussian Naive Bayes
Multinomial Naive Bayes
Complement Naive Bayes
Bernoulli Naive Bayes
Categorical Naive Bayes
* Multi-layer Perceptron
* Linear SVM
* C-SVM
Decision Trees Classifier

"""