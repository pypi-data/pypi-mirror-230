from sklearn.neighbors import KNeighborsClassifier
from copy import deepcopy


def Customization_KN(mods=None):
    if mods is None:
        mods = {}
    kneighbor = KNeighborsClassifier()

    # Selection Loop
    selectingParams = True
    while selectingParams:
        print('-------------------------------------------------------------------')
        print('|                   PLEASE CUSTOMIZE K-NEIGHBORS                  |')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. n_neighbors                                                 |')
        print('|  2. weights                                                     |')
        print('|  3. algorithm                                                   |')
        print('|  4. leaf_size (for algorithm)                                   |')
        print('|  5. p (Minkowski distance power factor)                         |')
        print('|  6. n_jobs                                                      |')
        print('-------------------------------------------------------------------')
        print('| Choose number here or enter 0 if you have no more modifications |')

        try:
            parameter = int(input("| Enter here: "))

            # Decision Tree
            if parameter == 0:
                selectingParams = False
            elif parameter == 1:
                print('-------------------------------------------------------------------')
                print('|                   You selected "n_neighbors"                    |')
                n_neighbors_input = int(input("| Select the number of neighbors per point: "))
                mods.update(n_neighbors=n_neighbors_input)
                kneighbor.set_params(**{'n_neighbors': n_neighbors_input})
            elif parameter == 2:
                print('-------------------------------------------------------------------')
                print('|                     You selected "weights"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. uniform                                                     |')
                print('|  2. distance                                                    |')
                weights_input = int(input("| Select the weight function used: "))
                if weights_input == 1:
                    mods.update(weights="uniform")
                    kneighbor.set_params(**{'weights': "uniform"})
                elif weights_input == 2:
                    mods.update(weights="distance")
                    kneighbor.set_params(**{'weights': "distance"})
            elif parameter == 3:
                print('-------------------------------------------------------------------')
                print('|                    You selected "algorithm"                     |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. auto                                                        |')
                print('|  2. ball_tree                                                   |')
                print('|  3. kd_tree                                                     |')
                print('|  4. brute                                                       |')
                algorithm_input = int(input("| Select the neighbor function used: "))
                if algorithm_input == 1:
                    mods.update(algorithm="auto")
                    kneighbor.set_params(**{'algorithm': "auto"})
                elif algorithm_input == 2:
                    mods.update(algorithm="ball_tree")
                    kneighbor.set_params(**{'algorithm': "ball_tree"})
                elif algorithm_input == 3:
                    mods.update(algorithm="kd_tree")
                    kneighbor.set_params(**{'algorithm': "kd_tree"})
                elif algorithm_input == 4:
                    mods.update(algorithm="brute")
                    kneighbor.set_params(**{'algorithm': "brute"})
            elif parameter == 4:
                print('-------------------------------------------------------------------')
                print('|                    You selected "leaf_size"                     |')
                leaf_size_input = int(input("| Select the leaf size for tree algorithms: "))
                mods.update(leaf_size=leaf_size_input)
                kneighbor.set_params(**{'leaf_size': leaf_size_input})
            elif parameter == 5:
                print('-------------------------------------------------------------------')
                print('|                        You selected "p"                         |')
                p_input = int(input("| Select the power parameter for minkowski distance: "))
                mods.update(p=p_input)
                kneighbor.set_params(**{'p': p_input})
            elif parameter == 6:
                print('-------------------------------------------------------------------')
                print('|                      You selected "n_jobs"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. One job (default)                                           |')
                print('|  2. Custom number of jobs                                       |')
                print('|  3. Use all processors on laptop                                |')
                n_jobs_input = int(input("| Select one of the threading options: "))
                if n_jobs_input == 1:
                    mods.update(n_jobs=None)
                    kneighbor.set_params(**{'n_jobs': None})
                elif n_jobs_input == 2:
                    n_jobs_num = int(input("| Select how many jobs should be done: "))
                    mods.update(n_jobs=n_jobs_num)
                    kneighbor.set_params(**{'n_jobs': n_jobs_num})
                elif n_jobs_input == 3:
                    mods.update(n_jobs=-1)
                    kneighbor.set_params(**{'n_jobs': -1})
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')

    # Restore all old mods along with new mods
    for parameter, setting in mods.items():
        kneighbor.set_params(**{parameter: setting})

    newMods = deepcopy(mods)
    return kneighbor, newMods


def Set_Shiftlist(parameter, batchNum):
    shiftList = []
    print(f'|                  You selected {parameter}                    |')
    parameter_start = int(input("| What is the starting number: "))

    print('|  What interval would you like to use for adding/removing units? |')
    intervalChange = int(input("| Input a positive number for increase and a negative number for  |\n| decrease: "))
    parameter_end = parameter_start + (intervalChange * (batchNum - 1))

    print(f'| The number of units will start at {parameter_start} for the first classifier.')
    print(f'| This number will change by {intervalChange} units, {batchNum} times for each classifier.')
    print(f'| A total of {abs(intervalChange * (batchNum - 1))} units will be added or removed.')
    print(f'| The number will end at {parameter_end} for the last classifier. Is this okay?')

    choice = int(input('Choose 1 to confirm: '))
    if choice == 1:
        for i in range(batchNum):
            shiftList.append(parameter_start)
            parameter_start = round(parameter_start + intervalChange, 8)
        settingParam = False
    else:
        print('|             Confirmation unsuccessful. Trying again.            |')
        print('-------------------------------------------------------------------')
        settingParam = True

    print(shiftList)

    return shiftList, settingParam


def Mod_List_KN(batchNum, classMods=None):
    settingParam = True

    if classMods is None:
        classMods = {}

    workingMods = deepcopy(classMods)
    kNeighList = []

    while settingParam:
        print('-------------------------------------------------------------------')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. n_neighbors                                                 |')
        print('|  2. weights                                                     |')
        print('|  3. algorithm                                                   |')
        print('|  4. leaf_size (for algorithm)                                   |')
        print('|  5. p (Minkowski distance power factor)                         |')
        print('|  6. n_jobs                                                      |')
        print('-------------------------------------------------------------------')
        try:
            print('| Which parameter should be the shifting parameter?')
            shiftParam = int(input('(Choose number or 0 to cancel): '))
            if shiftParam == 0:
                settingParam = False
                return 0
            elif shiftParam == 1:
                shiftList, sp = Set_Shiftlist("n_neighbors", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(n_neighbors=num)
                    kneighbor = KNeighborsClassifier()

                    for parameter, setting in workingMods.items():
                        kneighbor.set_params(**{parameter: setting})

                    kNeighList.append(kneighbor)
            elif shiftParam == 2:
                print('-------------------------------------------------------------------')
                print('|                      You selected "weights"                     |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 3:
                print('-------------------------------------------------------------------')
                print('|                     You selected "algorithm"                    |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 4:
                shiftList, sp = Set_Shiftlist("leaf_size", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(leaf_size=num)
                    kneighbor = KNeighborsClassifier()

                    for parameter, setting in workingMods.items():
                        kneighbor.set_params(**{parameter: setting})

                    kNeighList.append(kneighbor)
            elif shiftParam == 5:
                print('-------------------------------------------------------------------')
                print('|                         You selected "p"                        |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 6:
                print('-------------------------------------------------------------------')
                print('|                      You selected "n_jobs"                      |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')

    print(kNeighList)
    return kNeighList
