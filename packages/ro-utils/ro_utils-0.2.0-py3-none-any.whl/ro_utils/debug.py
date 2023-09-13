from pprint import PrettyPrinter


def pprint(args: object):
    """
    pretty print
    :param args:
    :return:
    """
    p = PrettyPrinter()
    p.pprint(args)
