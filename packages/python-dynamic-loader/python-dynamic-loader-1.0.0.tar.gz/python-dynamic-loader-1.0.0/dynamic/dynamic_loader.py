# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import logging
import sys
import types
from importlib import abc, import_module, machinery, reload
from typing import Any, Mapping, Optional, Type, TypeVar

from dynamic.source_grabbers import CloudStorage, SourceGrabber


class DynamicClassFinder(abc.MetaPathFinder):
  """Check class type

  This class checks to see if the class being loaded is a subclass of
  'DynamicClass' and in the correct package. If it isn't, it won't be loaded.
  """

  def __init__(self, storage: SourceGrabber) -> None:
    self.storage = storage

  def find_spec(self,
                fullname: str,
                path: str,
                target: Optional[str] = None) -> machinery.ModuleSpec:
    """Locate the file in GCS.

    Args:
        fullname (str): fully specified class name
        path (str): path to the file. unused here as we us our own loader.
        target (Optional[str], optional): The target. Defaults to None.

    Returns:
        machinery.ModuleSpec: a module spec
    """
    logging.debug(f'in find_spec: full_name = "{fullname}"')
    # if 'dynamic' not in fullname:
    #   # Ignore anything requested that is not a part of the dynamic loader
    #   # package.
    #   return None

    # else:
    return machinery.ModuleSpec(fullname, DynamicClassLoader(self.storage))


class DynamicClassLoader(abc.Loader):
  """Load a DynamicClass

  Load an arbitrary DynamicClass subclass into the Python class library
  dynamically. The location to check is hardwired here for security
  reasons.
  """
  storage: SourceGrabber = None

  def __init__(self, storage: SourceGrabber) -> None:
    self.storage = storage

  def exec_module(self, module: types.ModuleType):
    """Read the code from GCS and execute (load) it.

    Args:
        module (types.ModuleType): the module.

    Raises:
        ModuleNotFoundError: raised if the module does not exist.
    """
    try:
      # Split the package to get the base class name - it's the last element
      # of the fully qualified name.
      filename = module.__name__.split('.')[-1]

      # Fetch the code here as string.
      # GCS? BQ? Firestore? Secret Manager? All good options - but for this
      # purpose we're hardcoding a specific GCS bucket. More, we're not passing
      # any credentials so it will be accessed as the service account.
      # source = f'{filename}.py'
      code = self.storage.fetch_source(source=filename)

      exec(code, vars(module))

    except:
      raise ModuleNotFoundError(module)


class DynamicClass(object):
  """DynamicClass Abstract parent class

  In order to be loaded by the DynamicClass mechanism, all/any classes
  MUST extend this class and implement the 'run' method.
  """
  TDatastore = TypeVar('TDatastore', bound=SourceGrabber)

  def install(module_name: str,
              class_name: str = 'Class',
              storage: Type[TDatastore] = CloudStorage,
              **args) -> DynamicClass:
    """Inserts the finder into the import machinery.

    *** THIS METHOD SHOULD NOT BE OVERRIDDEN ***

    Args:
        module_name (str): the name of the module
        class_name (str, optional): the name of the loaded class.
                                    Defaults to 'Class'.
        storage (Type[TDatastore]): the StorageGrabber class to use

    Returns:
        DynamicClass: the new Class
    """
    datastore = storage(**args)
    sys.meta_path.append(DynamicClassFinder(datastore))
    _module = f'dynamic.{module_name}'

    if _module in sys.modules:
      module = sys.modules[_module]
      module = reload(module)

    else:
      module = import_module(_module)

    return getattr(module, class_name)

  def run(self, **attributes: Mapping[str, str]) -> Any:
    """Run the user's command code.

    This is placed simply as a placeholder. If you are calling specific
    methods from within your code, you need not use this method, but when you
    are inserting generic methods, it's useful to have a single entry point.

    Args:
        **attributes: list of attributes passed to the Class.
                      These are optional.

    Returns:
        Any: the function's return value
    """
    pass
