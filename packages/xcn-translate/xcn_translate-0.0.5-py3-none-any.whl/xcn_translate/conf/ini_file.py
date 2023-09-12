import os
import configparser
import sys

class IniFile(object):
    def __init__(self, ini_file=None):
        self.__ini_file_path = None if ini_file is None else ini_file
        _file = self.__ini_file_path if self.__ini_file_path is not None and os.path.exists(self.__ini_file_path) else None

        self.__parser_obj = configparser.ConfigParser()

        if _file is not None:
            s = self.__read_file(self.__ini_file_path)
            if type(s) == str and len(s) > 0:
                self.__parser_obj.read_string(s)

    @property
    def ini_file(self):
        return self.__ini_file_path

    def __read_file(self, filename):
        abs_nm = None
        conf_str = None
        if os.path.isabs(filename):
            abs_nm = filename
        else:
            for x in sys.path:
                t = os.path.join(x, filename)
                if os.path.isfile(t):
                    abs_nm = t
                    #print("file found. - {0}".format(abs_nm))
                    break
        if abs_nm:
            f = open(abs_nm, 'r', encoding='utf-8')
            conf_str = f.read()
            f.close()
        else:
            conf_str = ''
            # print("file is not found. - {0}".format(filename))
        return conf_str

    def __get_value(self, node, key):
        if self.__parser_obj is None:
            return None
        try:
            ret = self.__parser_obj.get(node, key)
            # if '{0}-{1}-{2}'.format(node,key,ret) not in TestEnv.__log_mask__:
            #     print('get key({0}) in node({1}) is [{2}] on launch configure!'.format(key, node, ret))
            #     TestEnv.__log_mask__.add('{0}-{1}-{2}'.format(node,key,ret))
        except:
            ret = None
            print('can not find key({0}) in node({1}) on launch configure({2})!'.format(key, node, self.__ini_file_path))
        return ret

    @property
    def dict(self):
        ret = {}
        for sec in self.sections:
            cont = {}
            for key in self.keys(sec):
                val = self.get(sec, key)
                cont[key] = val

            ret[sec] = cont

        return ret

    @property
    def sections(self):
        return self.__gets_f('sections')

    def section(self, section):
        keys = self.keys(section)
        ret = {}
        for key in keys:
            ret[key] = self.get(section, key)
        return ret

    def keys(self, section):
        return self.__gets_f('keys', section)

    def get(self, section, key):
        return self.__gets_f('get', section, key)

    def __gets_f(self, cmd='', arg1=None, arg2=None):
        if self.__parser_obj is None:
            return None
        elif cmd == 'sections':
            return self.__parser_obj.sections()
        elif cmd == 'keys':
            keys = []
            for key in self.__parser_obj[arg1]:
                keys.append(key)
            return keys
        elif cmd == 'get':
            return self.__parser_obj.get(arg1, arg2)

    def set(self, section, key, value):
        if section in self.sections and isinstance(key, str) and len(key)>0:
            self.__sets_f('key', section, key, value)
        elif section in self.sections and ( not isinstance(key, str) or len(key) < 1) and isinstance(value,dict):
            self.__sets_f('section', section, val=value)
        # elif section in self.sections and \
        #         isinstance(key, str) and len(key) >0 and \
        #         isinstance(value, str):
        #     self.__sets_f('key', section, key, val=value)
        else:
            self.__sets_f('section', section, val={})
            self.__sets_f('key', section, key, value)

    def __sets_f(self, cmd='', arg1=None, arg2=None, val=None):
        if self.__parser_obj is None:
            return None
        elif cmd == 'section':
            self.__parser_obj[arg1]= val
        elif cmd == 'key':
            self.__parser_obj[arg1][arg2] = val

    def write(self, new_ini_file=None):
        if self.__parser_obj is None:
            raise RuntimeError("No object")

        _file = new_ini_file if new_ini_file is not None and len(new_ini_file)>4 else self.__ini_file_path

        with open(_file, 'w') as new_file:
            self.__parser_obj.write(new_file)

