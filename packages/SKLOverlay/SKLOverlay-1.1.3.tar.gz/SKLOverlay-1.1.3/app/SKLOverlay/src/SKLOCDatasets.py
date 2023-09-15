from SKLOCDataMods import Dataset_Config
import pandas as pd
import sklearn.datasets as ds
from random import random


def Dataframe_Processing(sample, yCol=''):
    if yCol != '':
        yColName = yCol + '_Y'
    else:
        yColName = 'Y'

    sampleX = sample.data
    sampleY = sample.target

    sampleX = pd.DataFrame(sampleX, columns=sample.feature_names)
    sampleY = pd.DataFrame({yColName: sampleY})

    sampleDF = sampleX.join(sampleY)
    return sampleDF


def Tuple_Processing(sampleX, sampleY):
    xLabels = []
    labelNum = len(sampleX[0])
    for i in range(labelNum):
        xLabels.append('Feature' + str(i + 1))

    DFX = pd.DataFrame(sampleX, columns=xLabels)
    print(f'Type: {type(DFX)}')

    sampleY = {'Y': sampleY}

    DFY = pd.DataFrame(sampleY)

    sampleDF = DFX.join(DFY)
    return sampleDF


def Make_Class_Configuration():
    # Data creation
    datapoints = int(input('| How many samples do you want (Press 0 for default): '))
    features = int(input('| How many features should the data have (Press 0 for default): '))
    infoFeatures = int(input('| How many of those features should be important?\n(Press 0 for default): '))
    reduFeatures = int(input('| How many of those features should be red herrings?\n(Press 0 for default): '))
    classes = int(input('How many classes do you want (Press 0 for default): '))
    distribution = int(input('Should the data be balanced (0) or imbalanced (1)?\n(Choose corresponding number): '))
    scal = int(input('What numbers should the numbers be magnified by?\n(Must be greater than 1): '))

    if datapoints <= 0:
        datapoints = 100
    if features <= 0:
        features = 20
    if infoFeatures <= 0:
        infoFeatures = 2
    if reduFeatures <= 0:
        reduFeatures = 2
    if infoFeatures + reduFeatures >= features:
        print('|                  Feature number insufficient.                   |')
        print('|           Raising number of features to accommodate.            |')

        features += (infoFeatures + reduFeatures)
        print(f'| There are now {features} features.')
    if classes <= 0:
        classes = 2
    if classes >= datapoints:
        print('|                   Sample number insufficient.                   |')
        print('|            Raising number of samples to accommodate.            |')

        datapoints = (datapoints + classes) * 2
        print(f'| There are now {datapoints} samples.')
    if distribution == 0:
        dist = None
    elif distribution == 1:
        dist = []
        for i in range(classes):
            weightCoef = random() * 2 + 0.1
            dist.append(weightCoef)
    else:
        print('|      Unrecognized option chosen. Classes will be balanced.      |')

        dist = None
    if scal <= 1:
        print('|             Scale number insufficient or redundant.             |')
        print('|                    Using default scale of 1.                    |')

        scal = 1

    sampleX, sampleY = ds.make_classification(
        n_samples=datapoints,
        n_features=features,
        n_informative=infoFeatures,
        n_redundant=reduFeatures,
        n_classes=classes,
        weights=dist,
        scale=scal,
        random_state=42
    )

    sampleDF = Tuple_Processing(sampleX, sampleY)
    return sampleDF


def Make_Circles_Configuration():
    datapoints = int(input('| How many samples do you want (Press 0 for default): '))
    if datapoints <= 0:
        datapoints = 100

    sampleX, sampleY = ds.make_circles(n_samples=datapoints, random_state=42)

    sampleDF = Tuple_Processing(sampleX, sampleY)
    return sampleDF


def Make_Hastie_Configuration():
    datapoints = int(input('| How many samples do you want (Press 0 for default): '))
    if datapoints <= 0:
        datapoints = 12000

    sampleX, sampleY = ds.make_hastie_10_2(n_samples=datapoints, random_state=42)

    sampleDF = Tuple_Processing(sampleX, sampleY)
    return sampleDF


def Make_Moons_Configuration():
    datapoints = int(input('| How many samples do you want (Press 0 for default): '))
    gauNoise = int(input('| Should the data contain noise(1) or not(0)\n(Choose corresponding number): '))
    if datapoints <= 0:
        datapoints = 100
    if gauNoise == 0:
        gau = None
    elif gauNoise == 1:
        gau = random()
    else:
        print('|       Unrecognized option chosen. No noise will be added.       |')
        gau = None

    sampleX, sampleY = ds.make_moons(n_samples=datapoints, noise=gau, random_state=42)

    sampleDF = Tuple_Processing(sampleX, sampleY)
    return sampleDF


def Make_S_Configuration():
    datapoints = int(input('| How many samples do you want (Press 0 for default): '))
    gauNoise = int(input('| Should the data contain noise(1) or not(0)\n(Choose corresponding number): '))
    if datapoints <= 0:
        datapoints = 100
    if gauNoise == 0:
        gau = 0.0
    elif gauNoise == 1:
        gau = random()
    else:
        print('|       Unrecognized option chosen. No noise will be added.       |')
        gau = 0.0

    sampleX, sampleY = ds.make_s_curve(n_samples=datapoints, noise=gau, random_state=42)

    sampleDF = Tuple_Processing(sampleX, sampleY)
    return sampleDF


def Make_Swiss_Roll_Configuration():
    datapoints = int(input('| How many samples do you want (Press 0 for default): '))
    gauNoise = int(input('| Should the data contain noise(1) or not(0)\n(Choose corresponding number): '))
    if datapoints <= 0:
        datapoints = 100
    if gauNoise == 0:
        gau = 0.0
    elif gauNoise == 1:
        gau = random()
    else:
        print('|       Unrecognized option chosen. No noise will be added.       |')
        gau = 0.0

    sampleX, sampleY = ds.make_swiss_roll(n_samples=datapoints, noise=gau, random_state=42)

    sampleDF = Tuple_Processing(sampleX, sampleY)
    return sampleDF


def Dataset_Setup_Sample(nickname):
    print('| Note: Keep in mind sample sets already have a Y, noted by "(Y)" |')
    print('|       in one of the columns. For details pertaining to each     |')
    print('|       sample, visit the Sci-Kit Learn website and search the    |')
    print('|       dataset Name.                                             |')
    print('|                                                                 |')
    print('|                 Please select a dataset to use:                 |')
    print('|                              -----                              |')
    print('|  0. Cancel                                                      |')
    print('|  1. California Housing                                          |')
    print('|  2. Cover Type                                                  |')
    print('|  3. Breast Cancer                                               |')
    print('|  4. Digits                                                      |')
    print('|  5. Iris Plants                                                 |')
    print('|  6. Wine                                                        |')
    print('|  7. Random Dataset Generation                                   |')
    print('|  8. Circle Generation                                           |')
    print('|  9. Random Binary (Hastie) Generation                           |')
    print('| 10. Moon Generation                                             |')
    print('| 11. Cool S Generation                                           |')
    print('| 12. Swiss Roll Generation                                       |')
    try:
        choice = int(input('|                      Enter number here: '))
        if choice == 0:
            return 0
        elif choice == 1:
            sample = ds.fetch_california_housing()
            sampleDF = Dataframe_Processing(sample, yCol='Value')
        elif choice == 2:
            sample = ds.fetch_covtype()
            sampleDF = Dataframe_Processing(sample, yCol='CovType')
        elif choice == 3:
            sample = ds.load_breast_cancer()
            sampleDF = Dataframe_Processing(sample, yCol='Diagnosis')
        elif choice == 4:
            sample = ds.load_digits()
            sampleDF = Dataframe_Processing(sample, yCol='Number')
        elif choice == 5:
            sample = ds.load_iris()
            sampleDF = Dataframe_Processing(sample, yCol='Plant')
        elif choice == 6:
            sample = ds.load_wine()
            sampleDF = Dataframe_Processing(sample, yCol='Wine')
        elif choice == 7:
            sampleDF = Make_Class_Configuration()
        elif choice == 8:
            sampleDF = Make_Circles_Configuration()
        elif choice == 9:
            sampleDF = Make_Hastie_Configuration()
        elif choice == 10:
            sampleDF = Make_Moons_Configuration()
        elif choice == 11:
            sampleDF = Make_S_Configuration()
        elif choice == 12:
            sampleDF = Make_Swiss_Roll_Configuration()
        else:
            print('|          Unrecognized option chosen. Please try again.          |')
            print('-------------------------------------------------------------------')
            return 0
    except ValueError:
        print('-------------------------------------------------------------------')
        print('|                          ERROR CAUGHT                           |')
        print('| Tip: Unless specifically asked, you will only have to use       |')
        print('|      numbers to move around and make selections. Until further  |')
        print('|      improvements, this error will result in loss of progress   |')
        print('|      or even shutdown of the program. I apologize for any       |')
        print('|      inconvenience.                                             |')
        print('-------------------------------------------------------------------')
        return 0

    print(sampleDF)

    return Dataset_Config(nickname, sampleDF)


def Dataset_Setup_Local(nickname, filePath):
    # Being kind to user
    if filePath.startswith('"'):
        filePath = filePath[1:]

    if filePath.endswith('"'):
        filePath = filePath[:-1]

    print(f'| Dataset: {filePath}')

    extension = filePath.split('.')[-1]
    if extension == 'csv':
        datasetDF = pd.read_csv(filePath)
    elif extension in {'xls', 'xlsx', 'xlsm', 'xlsb', 'odf', 'ods', 'odt'}:
        datasetDF = pd.read_excel(filePath)
    elif extension == 'json':
        datasetDF = pd.read_json(filePath)
    elif extension == 'txt':
        delimiter = input('| Type the character used to split entities in your dataset file: ')
        datasetDF = pd.read_table(filePath, sep=delimiter)
    else:
        print('|                  Unrecognized option chosen.                    |')
        print('|     Please use a file path that leads to a supported format     |')
        print('-------------------------------------------------------------------')
        return 0

    return Dataset_Config(nickname, datasetDF)
