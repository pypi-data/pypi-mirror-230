from sklearn.svm import SVC
from copy import deepcopy
from ast import literal_eval


def Customization_SVM(mods=None):
    if mods is None:
        mods = {}
    svc = SVC()

    # Selection Loop
    selectingParams = True
    while selectingParams:
        print('-------------------------------------------------------------------')
        print('|             PLEASE CUSTOMIZE SUPPORT VECTOR MACHINE             |')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. C (regularization parameter)                                |')
        print('|  2. kernel                                                      |')
        print('|  3. degree                                                      |')
        print('|  4. gamma                                                       |')
        print('|  5. coef0                                                       |')
        print('|  6. shrinking                                                   |')
        print('|  7. probability                                                 |')
        print('|  8. tol (tolerance)                                             |')
        print('|  9. cache_size                                                  |')
        print('| 10. class_weight                                                |')
        print('| 11. verbose                                                     |')
        print('| 12. max_iter                                                    |')
        print('| 13. decision_function_shape                                     |')
        print('| 14. break_ties                                                  |')
        print('| 15. random_state                                                |')
        print('-------------------------------------------------------------------')
        print('| Choose number here or enter 0 if you have no more modifications |')

        try:
            parameter = int(input("| Enter here: "))

            # Decision Tree
            if parameter == 0:
                selectingParams = False
            elif parameter == 1:
                print('-------------------------------------------------------------------')
                print('|                         You selected "C"                        |')
                C_input = float(input("| Select the regularization parameter: "))
                mods.update(C=C_input)
                svc.set_params(**{'C': C_input})
            elif parameter == 2:
                print('-------------------------------------------------------------------')
                print('|                      You selected "kernel"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. rbf (default)                                               |')
                print('|  2. linear                                                      |')
                print('|  3. poly                                                        |')
                print('|  4. sigmoid                                                     |')
                print('|  5. precomputed                                                 |')
                kernel_input = int(input("| Select the kernel to be used: "))
                if kernel_input == 1:
                    mods.update(kernel="rbf")
                    svc.set_params(**{'kernel': "rbf"})
                elif kernel_input == 2:
                    mods.update(kernel="linear")
                    svc.set_params(**{'kernel': "linear"})
                elif kernel_input == 3:
                    mods.update(kernel="poly")
                    svc.set_params(**{'kernel': "poly"})
                elif kernel_input == 4:
                    mods.update(kernel="sigmoid")
                    svc.set_params(**{'kernel': "sigmoid"})
                elif kernel_input == 5:
                    mods.update(kernel="precomputed")
                    svc.set_params(**{'kernel': "precomputed"})
            elif parameter == 3:
                print('-------------------------------------------------------------------')
                print('|                      You selected "degree"                      |')
                degree_input = int(input("| Select the degree of the kernel function: "))
                mods.update(degree=degree_input)
                svc.set_params(**{'degree': degree_input})
            elif parameter == 4:
                print('-------------------------------------------------------------------')
                print('|                      You selected "gamma"                       |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. scale (default)                                             |')
                print('|  2. auto                                                        |')
                print('|  3. custom                                                      |')
                gamma_input = int(input("| Select the kernel coefficient: "))
                if gamma_input == 1:
                    mods.update(gamma="scale")
                    svc.set_params(**{'gamma': "scale"})
                elif gamma_input == 2:
                    mods.update(gamma="auto")
                    svc.set_params(**{'gamma': "auto"})
                elif gamma_input == 3:
                    customGamma = float(input("| Enter the coefficient number here: "))
                    mods.update(gamma=customGamma)
                    svc.set_params(**{'gamma': customGamma})
            elif parameter == 5:
                print('-------------------------------------------------------------------')
                print('|                      You selected "coef0"                       |')
                coef_input = float(input("| Enter the independent term here: "))
                mods.update(coef0=coef_input)
                svc.set_params(**{'coef0': coef_input})
            elif parameter == 6:
                print('-------------------------------------------------------------------')
                print('|                    You selected "shrinking"                     |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. true (default)                                              |')
                print('|  2. false                                                       |')
                shrinking_input = int(input("| Select whether to use the shrinking heuristic: "))
                if shrinking_input == 1:
                    mods.update(shrinking=True)
                    svc.set_params(**{'shrinking': True})
                elif shrinking_input == 2:
                    mods.update(shrinking=False)
                    svc.set_params(**{'shrinking': False})
            elif parameter == 7:
                print('-------------------------------------------------------------------')
                print('|                   You selected "probability"                    |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. false (default)                                             |')
                print('|  2. true                                                        |')
                shrinking_input = int(input("| Select whether to enable probability estimates: "))
                if shrinking_input == 1:
                    mods.update(shrinking=False)
                    svc.set_params(**{'shrinking': False})
                elif shrinking_input == 2:
                    mods.update(shrinking=True)
                    svc.set_params(**{'shrinking': True})
            elif parameter == 8:
                print('-------------------------------------------------------------------')
                print('|                       You selected "tol"                        |')
                tol_input = float(input("| Enter the tolerance criterion: "))
                mods.update(tol=tol_input)
                svc.set_params(**{'tol': tol_input})
            elif parameter == 9:
                print('-------------------------------------------------------------------')
                print('|                   You selected "cache_size"                     |')
                cache_size_input = int(input("| Enter the tolerance criterion: "))
                mods.update(cache_size=cache_size_input)
                svc.set_params(**{'cache_size': cache_size_input})
            elif parameter == 10:
                print('-------------------------------------------------------------------')
                print('|                   You selected "class_weight"                   |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. None (default)                                              |')
                print('|  2. balanced                                                    |')
                print('|  3. Custom dictionary                                           |')
                class_weight_input = int(input("| Select the class weight option: "))
                if class_weight_input == 1:
                    mods.update(class_weight=None)
                    svc.set_params(**{'class_weight': None})
                elif class_weight_input == 2:
                    mods.update(class_weight="balanced")
                    svc.set_params(**{'class_weight': "balanced"})
                elif class_weight_input == 3:
                    class_weight_input = input("| Enter in the class weights in dictionary or list of dicts format: ")
                    class_weight_input = literal_eval(class_weight_input)
                    mods.update(class_weight=class_weight_input)
                    svc.set_params(**{'class_weight': class_weight_input})
            elif parameter == 11:
                print('-------------------------------------------------------------------')
                print('|                     You selected "verbose"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. false (default)                                             |')
                print('|  2. true                                                        |')
                verbose_input = int(input("| Select whether to enable probability estimates: "))
                if verbose_input == 1:
                    mods.update(verbose=False)
                    svc.set_params(**{'verbose': False})
                elif verbose_input == 2:
                    mods.update(verbose=True)
                    svc.set_params(**{'verbose': True})
            elif parameter == 12:
                print('-------------------------------------------------------------------')
                print('|                     You selected "max_iter"                     |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. No limit (default)                                          |')
                print('|  2. Custom                                                      |')
                max_iter_input = int(input("| Select the number of iterations: "))
                if max_iter_input == 1:
                    mods.update(max_iter=-1)
                    svc.set_params(**{'max_iter': -1})
                elif max_iter_input == 2:
                    max_iter_num = int(input("| Enter the number of iterations: "))
                    mods.update(max_iter=max_iter_num)
                    svc.set_params(**{'max_iter': max_iter_num})
            elif parameter == 13:
                print('-------------------------------------------------------------------')
                print('|              You selected "decision_function_shape"             |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. ovr (one vs rest) (default)                                 |')
                print('|  2. ovo (one vs one)                                            |')
                dfs_input = int(input("| Select the decision function shape: "))
                if dfs_input == 1:
                    mods.update(decision_function_shape="ovr")
                    svc.set_params(**{'decision_function_shape': "ovr"})
                elif dfs_input == 1:
                    mods.update(decision_function_shape="ovr")
                    svc.set_params(**{'decision_function_shape': "ovr"})
            elif parameter == 14:
                print('-------------------------------------------------------------------')
                print('|                    You selected "break_ties"                    |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. false (default)                                             |')
                print('|  2. true                                                        |')
                break_ties_input = int(input("| Select whether to enable probability estimates: "))
                if break_ties_input == 1:
                    mods.update(break_ties=False)
                    svc.set_params(**{'break_ties': False})
                elif break_ties_input == 2:
                    mods.update(break_ties=True)
                    svc.set_params(**{'break_ties': True})
            elif parameter == 15:
                print('-------------------------------------------------------------------')
                print('|                   You selected "random_state"                   |')
                random_state_input = int(input("| Select the key for the randomizer: "))
                mods.update(random_state=random_state_input)
                svc.set_params(**{'random_state': random_state_input})
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
        svc.set_params(**{parameter: setting})

    newMods = deepcopy(mods)
    return svc, newMods


def Set_Shiftlist(parameter, batchNum):
    shiftList = []
    print(f'|                  You selected {parameter}                    |')
    parameter_start = float(input("| What is the starting number: "))

    print('|  What interval would you like to use for adding/removing units? |')
    intervalChange = float(input("| Input a positive number for increase and a negative number for  |\n| decrease: "))
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


def Mod_List_SVM(batchNum, classMods=None):
    settingParam = True

    if classMods is None:
        classMods = {}

    workingMods = deepcopy(classMods)
    svmList = []

    while settingParam:
        print('-------------------------------------------------------------------')
        print('|                    Parameter to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. C (regularization parameter)                                |')
        print('|  2. kernel                                                      |')
        print('|  3. degree                                                      |')
        print('|  4. gamma                                                       |')
        print('|  5. coef0                                                       |')
        print('|  6. shrinking                                                   |')
        print('|  7. probability                                                 |')
        print('|  8. tol (tolerance)                                             |')
        print('|  9. cache_size                                                  |')
        print('| 10. class_weight                                                |')
        print('| 11. verbose                                                     |')
        print('| 12. max_iter                                                    |')
        print('| 13. decision_function_shape                                     |')
        print('| 14. break_ties                                                  |')
        print('| 15. random_state                                                |')
        try:
            print('| Which parameter should be the shifting parameter?')
            shiftParam = int(input('(Choose number or 0 to cancel): '))

            if shiftParam == 0:
                settingParam = False
                return 0
            elif shiftParam == 1:
                shiftList, sp = Set_Shiftlist("C", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(C=num)
                    svc = SVC()

                    for parameter, setting in workingMods.items():
                        svc.set_params(**{parameter: setting})

                    svmList.append(svc)
            elif shiftParam == 2:
                print('| As this is a non-digit parameter, customization is not allowed. |')
                print('|     There will be five classifiers created for each option.    |')

                shiftList = ["rbf", "linear", "poly", "sigmoid", "precomputed"]
                settingParam = False

                for desc in shiftList:
                    workingMods.update(criterion=desc)
                    svc = SVC()

                    for parameter, setting in workingMods.items():
                        svc.set_params(**{parameter: setting})

                    svmList.append(svc)
            elif shiftParam == 3:
                shiftList, sp = Set_Shiftlist("degree", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(degree=int(num))
                    svc = SVC()

                    for parameter, setting in workingMods.items():
                        svc.set_params(**{parameter: setting})

                    svmList.append(svc)
            elif shiftParam == 4:
                print('-------------------------------------------------------------------')
                print('|                       You selected "gamma"                      |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 5:
                shiftList, sp = Set_Shiftlist("coef0", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(coef0=num)
                    svc = SVC()

                    for parameter, setting in workingMods.items():
                        svc.set_params(**{parameter: setting})

                    svmList.append(svc)
            elif shiftParam == 6:
                print('-------------------------------------------------------------------')
                print('|                     You selected "shrinking"                    |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 7:
                print('-------------------------------------------------------------------')
                print('|                    You selected "probability"                   |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 8:
                shiftList, sp = Set_Shiftlist("tol", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(tol=num)
                    svc = SVC()

                    for parameter, setting in workingMods.items():
                        svc.set_params(**{parameter: setting})

                    svmList.append(svc)
            elif shiftParam == 9:
                print('-------------------------------------------------------------------')
                print('|                    You selected "cache_size"                    |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 10:
                print('-------------------------------------------------------------------')
                print('|                    You selected "class_weight"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 11:
                print('-------------------------------------------------------------------')
                print('|                      You selected "verbose"                     |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 12:
                shiftList, sp = Set_Shiftlist("max_iter", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_iter=int(num))
                    svc = SVC()

                    for parameter, setting in workingMods.items():
                        svc.set_params(**{parameter: setting})

                    svmList.append(svc)
            elif shiftParam == 13:
                print('-------------------------------------------------------------------')
                print('|              You selected "decision_function_shape"             |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 14:
                print('-------------------------------------------------------------------')
                print('|                     You selected "break_ties"                   |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 15:
                print('-------------------------------------------------------------------')
                print('|                    You selected "random_state"                  |')
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

    print(svmList)
    return svmList
