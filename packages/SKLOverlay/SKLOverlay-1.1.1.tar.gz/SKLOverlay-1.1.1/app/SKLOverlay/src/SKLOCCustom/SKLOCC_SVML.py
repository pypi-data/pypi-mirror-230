from sklearn.svm import LinearSVC
from copy import deepcopy
from ast import literal_eval


def Customization_SVML(mods=None):
    if mods is None:
        mods = {}
    linSVM = LinearSVC()

    # Selection Loop
    selectingParams = True
    while selectingParams:
        print('-------------------------------------------------------------------')
        print('|                   PLEASE CUSTOMIZE LINEAR SVM                   |')
        print('|                   Parameters to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. penalty                                                     |')
        print('|  2. loss                                                        |')
        print('|  3. dual                                                        |')
        print('|  4. tol                                                         |')
        print('|  5. C (regularization parameter)                                |')
        print('|  6. multi_class                                                 |')
        print('|  7. fit_intercept                                               |')
        print('|  8. intercept_scaling                                           |')
        print('|  9. class_weight                                                |')
        print('| 10. verbose                                                     |')
        print('| 11. random_state                                                |')
        print('| 12. max_iter                                                    |')
        print('| Choose number here or enter 0 if you have no more modifications |')

        try:
            parameter = int(input("| Enter here: "))

            # Decision Tree
            if parameter == 0:
                selectingParams = False
            elif parameter == 1:
                print('-------------------------------------------------------------------')
                print('|                     You selected "penalty"                      |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. l1                                                          |')
                print('|  2. l2 (default)                                                |')
                penalty_input = int(input("| Select the norm of the penalty to be used: "))
                if penalty_input == 1:
                    mods.update(penalty="l1")
                    linSVM.set_params(**{'penalty': "l1"})
                elif penalty_input == 2:
                    mods.update(penalty="l2")
                    linSVM.set_params(**{'penalty': "l2"})
            elif parameter == 2:
                print('-------------------------------------------------------------------')
                print('|                       You selected "loss"                       |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. hinge (do not use with l1 penalty)                          |')
                print('|  2. squared_hinge (default)                                     |')
                loss_input = int(input("| Select the loss function: "))
                if loss_input == 1:
                    mods.update(loss="hinge")
                    linSVM.set_params(**{'loss': "hinge"})
                elif loss_input == 2:
                    mods.update(loss="squared_hinge")
                    linSVM.set_params(**{'loss': "squared_hinge"})
            elif parameter == 3:
                print('-------------------------------------------------------------------')
                print('|                       You selected "dual"                       |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. True                                                        |')
                print('|  2. False                                                       |')
                print('|  3. auto                                                        |')
                dual_input = int(input("| Select the dual optimization option: "))
                if dual_input == 1:
                    mods.update(dual=True)
                    linSVM.set_params(**{'dual': True})
                elif dual_input == 2:
                    mods.update(dual=False)
                    linSVM.set_params(**{'dual': False})
                elif dual_input == 3:
                    mods.update(dual="auto")
                    linSVM.set_params(**{'dual': "auto"})
            elif parameter == 4:
                print('-------------------------------------------------------------------')
                print('|                       You selected "tol"                        |')
                tol_input = float(input("| Enter the tolerance criterion: "))
                mods.update(tol=tol_input)
                linSVM.set_params(**{'tol': tol_input})
            elif parameter == 5:
                print('-------------------------------------------------------------------')
                print('|                         You selected "C"                        |')
                C_input = float(input("| Select the regularization parameter: "))
                mods.update(C=C_input)
                linSVM.set_params(**{'C': C_input})
            elif parameter == 6:
                print('-------------------------------------------------------------------')
                print('|                    You selected "multi_class"                   |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. ovr (default)                                               |')
                print('|  2. crammer_singer                                              |')
                multi_class_input = int(input("| Select the strategy for classifying more than two classes: "))
                if multi_class_input == 1:
                    mods.update(multi_class="ovr")
                    linSVM.set_params(**{'multi_class': "ovr"})
                elif multi_class_input == 2:
                    mods.update(multi_class="crammer_singer")
                    linSVM.set_params(**{'multi_class': "crammer_singer"})
            elif parameter == 7:
                print('-------------------------------------------------------------------')
                print('|                   You selected "fit_intercept"                  |')
                print('|                   Parameters to choose below:                   |')
                print('|                              -----                              |')
                print('|  1. True (default)                                              |')
                print('|  2. False                                                       |')
                fit_intercept_input = int(input("| Select whether to calculate the fit intercept: "))
                if fit_intercept_input == 1:
                    mods.update(fit_intercept=True)
                    linSVM.set_params(**{'fit_intercept': True})
                elif fit_intercept_input == 2:
                    mods.update(fit_intercept=False)
                    linSVM.set_params(**{'fit_intercept': False})
            elif parameter == 8:
                print('-------------------------------------------------------------------')
                print('|                You selected "intercept_scaling"                 |')
                intercept_scaling_input = float(input("| Enter the synthetic feature weight: "))
                mods.update(intercept_scaling=intercept_scaling_input)
                linSVM.set_params(**{'intercept_scaling': intercept_scaling_input})
            elif parameter == 9:
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
                    linSVM.set_params(**{'class_weight': None})
                elif class_weight_input == 2:
                    mods.update(class_weight="balanced")
                    linSVM.set_params(**{'class_weight': "balanced"})
                elif class_weight_input == 3:
                    class_weight_input = input("| Enter in the class weights in dictionary or list of dicts format: ")
                    class_weight_input = literal_eval(class_weight_input)
                    mods.update(class_weight=class_weight_input)
                    linSVM.set_params(**{'class_weight': class_weight_input})
            elif parameter == 10:
                print('-------------------------------------------------------------------')
                print('|                     You selected "verbose"                      |')
                verbose_input = int(input("| Enter the verbose setting: "))
                mods.update(verbose=verbose_input)
                linSVM.set_params(**{'verbose': verbose_input})
            elif parameter == 11:
                print('-------------------------------------------------------------------')
                print('|                      You selected "random_state"                      |')
                random_state_input = int(input("| Select the key for the randomizer: "))
                mods.update(random_state=random_state_input)
                linSVM.set_params(**{'random_state': random_state_input})
            elif parameter == 12:
                print('-------------------------------------------------------------------')
                print('|                     You selected "max_iter"                     |')
                max_iter_input = int(input("| Enter the maximum iterations: "))
                mods.update(max_iter=max_iter_input)
                linSVM.set_params(**{'max_iter': max_iter_input})
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
        linSVM.set_params(**{parameter: setting})

    newMods = deepcopy(mods)
    return linSVM, newMods


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


def Mod_List_SVML(batchNum, classMods=None):
    settingParam = True

    if classMods is None:
        classMods = {}

    workingMods = deepcopy(classMods)
    linSVMList = []

    while settingParam:
        print('-------------------------------------------------------------------')
        print('|                    Parameter to choose below:                   |')
        print('|                              -----                              |')
        print('|  1. penalty                                                     |')
        print('|  2. loss                                                        |')
        print('|  3. dual                                                        |')
        print('|  4. tol                                                         |')
        print('|  5. C (regularization parameter)                                |')
        print('|  6. multi_class                                                 |')
        print('|  7. fit_intercept                                               |')
        print('|  8. intercept_scaling                                           |')
        print('|  9. class_weight                                                |')
        print('| 10. verbose                                                     |')
        print('| 11. random_state                                                |')
        print('| 12. max_iter                                                    |')
        print('| Choose number here or enter 0 if you have no more modifications |')
        try:
            print('| Which parameter should be the shifting parameter?')
            shiftParam = int(input('(Choose number or 0 to cancel): '))

            if shiftParam == 0:
                settingParam = False
                return 0
            elif shiftParam == 1:
                print('-------------------------------------------------------------------')
                print('|                      You selected "penalty"                     |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 2:
                print('-------------------------------------------------------------------')
                print('|                        You selected "loss"                      |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 3:
                print('-------------------------------------------------------------------')
                print('|                        You selected "dual"                      |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 4:
                shiftList, sp = Set_Shiftlist("tol", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(tol=num)
                    linSVM = LinearSVC()

                    for parameter, setting in workingMods.items():
                        linSVM.set_params(**{parameter: setting})

                    linSVMList.append(linSVM)
            elif shiftParam == 5:
                shiftList, sp = Set_Shiftlist("C", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(C=num)
                    linSVM = LinearSVC()

                    for parameter, setting in workingMods.items():
                        linSVM.set_params(**{parameter: setting})

                    linSVMList.append(linSVM)
            elif shiftParam == 6:
                print('-------------------------------------------------------------------')
                print('|                    You selected "multi_class"                   |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 7:
                print('-------------------------------------------------------------------')
                print('|                   You selected "fit_intercept"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 8:
                print('-------------------------------------------------------------------')
                print('|                 You selected "intercept_scaling"                |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 9:
                print('-------------------------------------------------------------------')
                print('|                    You selected "class_weight"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 10:
                print('-------------------------------------------------------------------')
                print('|                       You selected "verbose"                    |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 11:
                print('-------------------------------------------------------------------')
                print('|                    You selected "random_state"                  |')
                print('|    This one isn\'t available as the need for it isn\'t strong.    |')
                print('| If this is truly desired, set it in the active classifier first.|')
            elif shiftParam == 12:
                shiftList, sp = Set_Shiftlist("max_iter", batchNum)
                settingParam = sp

                for num in shiftList:
                    workingMods.update(max_iter=int(num))
                    linSVM = LinearSVC()

                    for parameter, setting in workingMods.items():
                        linSVM.set_params(**{parameter: setting})

                    linSVMList.append(linSVM)
        except ValueError:
            print('-------------------------------------------------------------------')
            print('|                          ERROR CAUGHT                           |')
            print('| Tip: Unless specifically asked, you will only have to use       |')
            print('|      numbers to move around and make selections. Until further  |')
            print('|      improvements, this error will result in loss of progress   |')
            print('|      or even shutdown of the program. I apologize for any       |')
            print('|      inconvenience.                                             |')
            print('-------------------------------------------------------------------')

    print(linSVMList)
    return linSVMList
