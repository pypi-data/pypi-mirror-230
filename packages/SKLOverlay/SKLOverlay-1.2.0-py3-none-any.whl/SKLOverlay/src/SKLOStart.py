from .SKLOClassMenu import Classification_Menu


def Beware():
    print('Not in production')
    print('-------------------------------------------------------------------')
    print('|     WARNING  WARNING   WARNING   WARNING   WARNING  WARNING     |')
    print('|                                                                 |')
    print('|     Read instructions carefully and only use correct inputs     |')
    print('|           In addition, this runs on Sci-Kit Learn\'s work.      |')
    print('|        If you like what you see here, go check them out!        |')
    print('|                                                                 |')
    print('|     WARNING  WARNING   WARNING   WARNING   WARNING  WARNING     |')
    print('-------------------------------------------------------------------')


def Title_Screen():
    print('-------------------------------------------------------------------')
    print('|                     Welcome to SK-Overlay!                      |')
    print('|   This Program can be used on Datasets with only one Y Column.  |')
    print('|        Use on multilabel or other sets at your own risk.        |')
    print('|                                                                 |')
    print('|            Press 1 to run a classification algorithm            |')
    print('|                   Press 0 to end the program                    |')
    print('-------------------------------------------------------------------')


def Choice():
    choice = int(input('|                          Enter here: '))
    if choice == 0:
        print('-------------------------------------------------------------------')
        print('|                 Thank you for using Sk-Overlay!                 |')
        print('-------------------------------------------------------------------')
    elif choice == 1:
        print('-------------------------------------------------------------------')
        print('|                         CLASSIFICATION MENU                     |')
        Classification_Menu()
        print('-------------------------------------------------------------------')
        print('|                 Thank you for using Sk-Overlay!                 |')
        print('-------------------------------------------------------------------')
    else:
        print('-------------------------------------------------------------------')
        print('|                          ERROR CAUGHT                           |')
        print('|                 Thank you for using Sk-Overlay!                 |')
        print('-------------------------------------------------------------------')


def Test():
    print('Placeholder')


def Run():
    # Test()
    Beware()
    Title_Screen()
    Choice()


if __name__ == "__main__":
    Run()

"""
if __name__ == '__main__':
    Run()
"""


'''

How this will work. 

SKLOverlay
    1) leads to title screen saying welcome to SKLOverlay, 
    2) short explanation about how its just an easier way (for me) to use SKLearn modules
    3) warning about any file or folder that wishes to be worked with must be located within same directory
    3) asks what wishes to be done. Options are
        3a) Classification
        3b) Preprocessing (Standalone)
        3c) Regression
        
SKLOClass
SKLOReg
SKLOPre      

'''