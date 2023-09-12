# coding=utf-8
"""
This module contains the ProtectedMethodMetaClass class
"""
from . import __author__, __email__, __version__, __maintainer__, __date__


# ==================================================================================================
# IMPORTS
# ==================================================================================================
from .protected_decorator import Protected


# ==================================================================================================
# INITIALISATIONS
# ==================================================================================================

# ==================================================================================================
# CLASSES
# ==================================================================================================

# ===================================
class ProtectedMethodMetaClass(type):
    """
    This metaclass is designed to allow the protected mechanism for methods.
    Methods to make protected have to be declared as private and then decorated with the
    Protected decrorator (from protected_method_metaclass.protected_decorator import Protected)

    These method can be overloaded in child classes. if it is the case, direct mother class method
    is still accessible with the __old prefix.

    Ex:
    class A(object, metaclass=ProtectedMethodMetaClass):

        @Protected
        def __a(self):
            ...
        @Protected
        def __b(self):
            ...

    class B(A):

        def __a(self):
            ...

    For class B:
        __a, from A is overloaded by __a from B.
        __a from A is still accessible in B with the name __old_a
        __b from A is accessible in B with the name __b
    """

    # =============================================================
    def __new__(mcs, classname, bases, classdict, no_return=False):
        """
        __new__ method of the metaclasse

        :type classname: str
        :param classname: the name of the class to be created

        :type bases: tuple[type]
        :param bases: the parent classes of the classes to be created

        :type classdict: dict
        :param classdict: the dict of the class to be created

        :rtype: ProtectedMethodMetaClass
        :return: the class create through metaclass
        """

        # =====================================
        def get_dict(the_dict, the_class=None):
            """
            This is a recursive function designed to return all the methods
            (and their mangled names) to be added to hte classdict by walking its mother classes
            NOTE: if the class declares a protected method it is added in this dict.

            :type the_dict: dict[str, function]
            :param the_dict: dictionnary with the names of the added methods ass key and the methods
                             as values

            :type the_class: ProtectedMethodMetaClass
            :param the_class: the inspected class

            :rtype: set[str]
            :return: set of the added names for this class (just the name, no mangled name)
            """
            # ==========================================
            # Specific Initialization for this metaclass
            # if the_class is None data are gathered from the class to create
            if the_class is None:
                the_name = classname
                prefix = "_" + the_name
                the_class_dict = classdict
                the_bases = bases
                # ============================================================
                # get the name of the protected methods declared in this class
                protected_method_names = []
                prefix_size = len(prefix)
                for cur_name, item in the_class_dict.items():
                    if isinstance(item, Protected):
                        if cur_name.startswith(prefix):
                            protected_method_names.append(cur_name[prefix_size:])
                            the_class_dict[cur_name] = item.get_f()
                the_class_dict[prefix + "__protected_methods"] = protected_method_names
            else:
                the_name = the_class.__name__
                prefix = "_" + the_name
                the_class_dict = the_class.__dict__
                the_bases = the_class.__bases__
                # ============================================================
                # get the name of the protected methods declared in this class
                protected_method_names = the_class_dict[prefix + "__protected_methods"]

            # =================================================
            # prefix for the mangled names of the current class
            # and set of the added names for the current class
            added_names = set()

            # ===================================
            # loop over direct parent classes ...
            for base in the_bases:
                if isinstance(base, ProtectedMethodMetaClass):
                    # Only parent classes intheriting from the metaclass are inspected

                    # ====================================
                    # gathering data from the parent class
                    base_added_names = get_dict(the_dict, base)

                    # ===================================
                    # get the prefix for the parent class
                    base_name = base.__name__
                    base_prefix = "_" + base_name

                    # ===========================================================
                    # loop over the names of the added names of the parent class
                    for added_name in base_added_names:
                        # ==================================================
                        # mangled name in the current class and parent class
                        test_name = prefix + added_name
                        the_base_prefixed_name = base_prefix + added_name

                        if test_name in the_class_dict:
                            # In this case it means that one of the parents protected
                            # methods is overload in the current class

                            test_name3 = base_prefix + added_name
                            new_old_name = prefix + "__old" + added_name[1:]
                            replace_item = the_class_dict[test_name]

                            olds_to_add = {}
                            for test_name2 in the_dict:
                                if test_name2.endswith(added_name):
                                    if not test_name2.endswith("__old" + added_name[1:]):
                                        if new_old_name not in olds_to_add:
                                            test_item = the_dict[test_name3]
                                            olds_to_add[new_old_name] = test_item
                                        the_dict[test_name2] = replace_item
                            the_dict[test_name] = replace_item
                            the_dict.update(olds_to_add)
                        else:
                            # In this case the protected methods from parent classes
                            # are just added to the the current class
                            target = the_dict[the_base_prefixed_name]
                            the_dict[test_name] = target
                        added_names.add(added_name)

                    old_prefix = base_prefix + "__old_"
                    keys = [elem for elem in the_dict if elem.startswith(old_prefix)]
                    for key in keys:
                        del the_dict[key]

            for the_name in protected_method_names:
                test_name = prefix + the_name
                if test_name not in the_dict:
                    the_dict[test_name] = the_class_dict[test_name]
                    added_names.add(the_name)

            return added_names

        blop_dict = {}
        get_dict(blop_dict)
        old_keys = {elem for elem in classdict}
        classdict["_" + classname + "__old_classdict_keys"] = old_keys
        for name, func in blop_dict.items():
            if name not in classdict:
                classdict[name] = func

        if no_return:
            res = False
        else:
            res = type.__new__(mcs, classname, bases, classdict)

        return res


# ==================================================================================================
# FONCTIONS
# ==================================================================================================
