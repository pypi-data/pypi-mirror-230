from importlib.resources import contents, path
from IPython.display import display, Image


def theory(qn=0):
    print()
    if not qn:
        with path(
                'pm20_3.q',
                'task_1.png'
        ) as pt:
            img = Image(filename=pt)
            display(img)

        with path(
                'pm20_3.q',
                'task_2.png'
        ) as pt:
            img = Image(filename=pt)
            display(img)

        with path(
                'pm20_3.q',
                'task_3.png'
        ) as pt:
            img = Image(filename=pt)
            display(img)

        with path(
                'pm20_3.q',
                'task_4.png'
        ) as pt:
            img = Image(filename=pt)
            display(img)

        with path(
                'pm20_3.q',
                'task_5.png'
        ) as pt:
            img = Image(filename=pt)
            display(img)

        with path(
                'pm20_3.q',
                'task_6.png'
        ) as pt:
            img = Image(filename=pt)
            display(img)

    else:
        qn = str(qn)
        files = sorted(contents('pm20_3.q'))
        to_disp = []

        for elem in files:
            if 'q_' + qn + '_' in elem:
                to_disp.append(elem)
        if not to_disp:
            to_disp.append('q_' + qn + '.png')
        to_disp.sort()
        for elem in to_disp:
            with path(
                    'pm20_3.q',
                    elem
            ) as pt:
                img = Image(filename=pt)
                display(img)

