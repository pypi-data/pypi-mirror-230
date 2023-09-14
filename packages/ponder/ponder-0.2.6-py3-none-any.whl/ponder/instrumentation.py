import csv
import inspect
import time
from datetime import datetime
from functools import update_wrapper

import modin.pandas as mpd
from modin.pandas.groupby import DataFrameGroupBy as ModinDataFrameGroupByClazz
from modin.pandas.groupby import SeriesGroupBy as ModinSeriesGroupByClazz
from modin.pandas.resample import Resampler as ModinResamplerClazz
from modin.pandas.series_utils import DatetimeProperties as ModinDatetimePropertiesClazz
from modin.pandas.window import Expanding as ModinExpandingClazz
from modin.pandas.window import Rolling as ModinRollingClazz
from modin.pandas.window import Window as ModinWindowClazz

dunder_api_methods = ["__add__", "__dataframe__", "__array__", "__iter__"]


class PonderInstrumentation:
    _instrumentation_initialized = False
    _writer = None

    def __init__(self):
        self.init_instrumetation()

    def _instrument_function(self, func, classname, funcname, writer):
        from ponder.core.io import DBMSIO

        def wrapped(*args, **kwargs):
            excp = None
            start_time = time.perf_counter()
            try:
                output = func(*args, **kwargs)
            except Exception as e:
                excp = e
                raise e
            finally:
                stop_time = time.perf_counter()
                expname = None if excp is None else excp.__class__.__name__
                dbname = (
                    DBMSIO.default_connection.__class__.__module__
                    + "."
                    + DBMSIO.default_connection.__class__.__name__
                )
                non_none_params = list(
                    dict(filter(lambda x: x[1] is not None, kwargs.items())).keys()
                )
                data = {
                    "class": classname,
                    "method": funcname,
                    "db": dbname,
                    "params": non_none_params,
                    "exception": expname,
                    "start": start_time,
                    "stop": stop_time,
                }
                writer.write(data)
            return output

        update_wrapper(wrapped, func)
        return wrapped

    def _instrument_class(self, clazz, writer):
        # The Dtypes are not only noisy to instrument
        # they also introduce some unique issues with
        # typecasting once they are modified
        if clazz.__name__.endswith("Dtype"):
            return
        if hasattr(clazz, f"_ponder_instrumented_{clazz.__name__}"):
            return
        for funcname in dir(clazz):
            if funcname.startswith("_") and funcname not in dunder_api_methods:
                continue
            func = getattr(clazz, funcname)
            # Properties need to to have their getter wrapped
            if isinstance(func, property):
                wrapped_getter = self._instrument_function(
                    func.__get__, clazz.__name__, funcname, writer
                )
                new_property = property(wrapped_getter, func.__set__, func.__delattr__)
                try:
                    setattr(clazz, funcname, new_property)
                except:  # noqa: E722
                    pass
            # Anything else that is not callable should be ignored
            if not callable(func):
                continue
            # A property reference pointing at an implementation
            # class using __get__ or other methods. Instead of
            # modifying this property on the class we descend one
            # level into the implementation class
            if inspect.isclass(func):
                self._instrument_class(func, writer)
                continue
            wrapped_func = self._instrument_function(
                func, clazz.__name__, funcname, writer
            )
            try:
                setattr(clazz, funcname, wrapped_func)
            except:  # noqa: E722
                pass
        try:
            setattr(clazz, f"_ponder_instrumented_{clazz.__name__}", True)
        except:  # noqa: E722
            pass

    def _instrument_module(self, module, writer):
        exports = module.__all__
        for name in exports:
            if name.startswith("_") and name not in dunder_api_methods:
                continue
            object = getattr(module, name)
            if inspect.isclass(object):
                self._instrument_class(object, writer)
                continue
            if callable(object):
                self._instrument_function
                wrapped_func = self._instrument_function(
                    object, module.__name__, name, writer
                )
                try:
                    setattr(module, name, wrapped_func)
                except:  # noqa: E722
                    pass

    def init_instrumetation(self):
        if PonderInstrumentation._instrumentation_initialized is True:
            return
        PonderInstrumentation._instrumentation_initialized = True
        header = ["class", "method", "db", "params", "exception", "start", "stop"]
        PonderInstrumentation._writer = RecordWriter(header)

        self._instrument_module(mpd, PonderInstrumentation._writer)
        self._instrument_class(
            ModinDataFrameGroupByClazz, PonderInstrumentation._writer
        )
        self._instrument_class(ModinSeriesGroupByClazz, PonderInstrumentation._writer)
        self._instrument_class(ModinResamplerClazz, PonderInstrumentation._writer)
        self._instrument_class(ModinExpandingClazz, PonderInstrumentation._writer)
        self._instrument_class(ModinRollingClazz, PonderInstrumentation._writer)
        self._instrument_class(
            ModinDatetimePropertiesClazz, PonderInstrumentation._writer
        )
        self._instrument_class(ModinWindowClazz, PonderInstrumentation._writer)


class RecordWriter:
    _filename = None

    def __init__(self, header):
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d_%H%M%S")
        RecordWriter._filename = f"record-{dt_string}.csv"
        output = open(RecordWriter._filename, "a")
        writer = csv.DictWriter(output, fieldnames=header)
        writer.writeheader()
        self._writer = writer
        self._file = output

    def write(self, data):
        self._writer.writerow(data)
        # dtor not reliably called on process exit
        self._file.flush()

    def close(self):
        self._file.flush()
        self._file.close()

    def __del__(self):
        self.close()
