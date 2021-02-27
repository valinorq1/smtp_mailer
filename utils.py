import os
import string
import random


def split_list(alist, wanted_parts, sender):
    sender_to_dict_keys = {}
    for i in sender:
        sender_to_dict_keys[i] = 0
    length = len(alist)
    q = [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts)]

    for z, v in zip(q, sender_to_dict_keys.keys()):
        sender_to_dict_keys[v] = z
    print(sender_to_dict_keys)
    return sender_to_dict_keys

