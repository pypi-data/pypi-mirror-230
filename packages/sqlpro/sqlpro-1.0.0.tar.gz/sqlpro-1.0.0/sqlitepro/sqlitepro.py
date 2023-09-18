# coding=utf-8
import ctypes
import os


class Sqlite:
    def __init__(self):
        dllPath = os.path.join(os.path.dirname(__file__), "sqlite3.dll")
        self._dll = ctypes.CDLL(dllPath)
        self._db = None

    def _sqlite3_open(self, dbpath):
        db = ctypes.c_void_p()
        self._dll.sqlite3_open.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_void_p)]
        self._dll.sqlite3_open.restype = ctypes.c_int
        result = self._dll.sqlite3_open(dbpath.encode('utf-8'), ctypes.byref(db))
        return result, db

    def _sqlite3_key(self, db, key):
        self._dll.sqlite3_key.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_key.restype = ctypes.c_int
        return self._dll.sqlite3_key(db, key, len(key))

    def _sqlite3_prepare_v2(self, db, sql, ppStmt, pzTail):
        self._dll.sqlite3_prepare_v2.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int,
                                                 ctypes.POINTER(ctypes.c_void_p),
                                                 ctypes.POINTER(ctypes.c_char_p)]
        self._dll.sqlite3_prepare_v2.restype = ctypes.c_int
        return self._dll.sqlite3_prepare_v2(db, sql, len(sql), ctypes.byref(ppStmt), ctypes.byref(pzTail))

    def _sqlite3_step(self, pStmt):
        self._dll.sqlite3_step.argtypes = [ctypes.c_void_p]
        self._dll.sqlite3_step.restype = ctypes.c_int
        return self._dll.sqlite3_step(pStmt)

    def _sqlite3_column_count(self, pStmt):
        self._dll.sqlite3_column_count.argtypes = [ctypes.c_void_p]
        self._dll.sqlite3_column_count.restype = ctypes.c_int
        return self._dll.sqlite3_column_count(pStmt)

    def _sqlite3_column_name(self, pStmt, N):
        self._dll.sqlite3_column_name.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_column_name.restype = ctypes.c_char_p
        return self._dll.sqlite3_column_name(pStmt, N)

    def _sqlite3_column_type(self, pStmt, N):
        self._dll.sqlite3_column_type.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_column_type.restype = ctypes.c_int
        return self._dll.sqlite3_column_type(pStmt, N)

    def _sqlite3_column_int(self, pStmt, N):
        self._dll.sqlite3_column_int.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_column_int.restype = ctypes.c_int
        return self._dll.sqlite3_column_int(pStmt, N)

    def _sqlite3_column_double(self, pStmt, N):
        self._dll.sqlite3_column_double.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_column_double.restype = ctypes.c_double
        return self._dll.sqlite3_column_double(pStmt, N)

    def _sqlite3_column_text(self, pStmt, N):
        self._dll.sqlite3_column_text.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_column_text.restype = ctypes.c_char_p
        return self._dll.sqlite3_column_text(pStmt, N)

    def _sqlite3_column_blob(self, pStmt, N):
        self._dll.sqlite3_column_blob.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self._dll.sqlite3_column_blob.restype = ctypes.c_void_p
        return self._dll.sqlite3_column_blob(pStmt, N)

    def _sqlite3_finalize(self, pStmt):
        self._dll.sqlite3_finalize.argtypes = [ctypes.c_void_p]
        self._dll.sqlite3_finalize(pStmt)

    def connect(self, dbPath, key):
        key = key.encode('utf-8')
        result, self._db = self._sqlite3_open(dbPath)
        if result != 0:
            return False

        if self._sqlite3_key(self._db, key) != 0:
            return False

        return True

    def execute(self, sql):
        sql = sql.encode('utf-8')
        ppStmt = ctypes.c_void_p()
        pzTail = ctypes.c_char_p()
        result = self._sqlite3_prepare_v2(self._db, sql, ppStmt, pzTail)
        if result != 0:
            return False

        table = []
        columnCnt = self._sqlite3_column_count(ppStmt)

        while self._sqlite3_step(ppStmt) == 100:
            row = {}
            for i in range(columnCnt):
                name = self._sqlite3_column_name(ppStmt, i).decode('utf-8')
                columnType = self._sqlite3_column_type(ppStmt, i)
                if columnType == 1:
                    value = self._sqlite3_column_int(ppStmt, i)
                elif columnType == 2:
                    value = self._sqlite3_column_double(ppStmt, i)
                elif columnType == 3:
                    value = self._sqlite3_column_text(ppStmt, i).decode('utf-8')
                elif columnType == 4:
                    value = self._sqlite3_column_blob(ppStmt, i)
                else:
                    value = ""
                row[name] = value
            table.append(row)

        self._sqlite3_finalize(ppStmt)
        return table
